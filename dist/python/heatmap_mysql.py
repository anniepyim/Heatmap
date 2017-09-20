#!/usr/bin/env python

import cgi, os, re, sys
import cgitb;cgitb.enable()
import json
import pandas as pd
import numpy as np
import collections

import matplotlib
matplotlib.use('Agg')

import mpld3
from mpld3 import utils
from mpld3 import plugins
import seaborn_hm
#import seaborn as sns
import pymysql
#import time

#start_time = time.time()

class PluginBase(object):
    def get_dict(self):
        return self.dict_

    def javascript(self):
        if hasattr(self, "JAVASCRIPT"):
            if hasattr(self, "js_args_"):
                return self.JAVASCRIPT.render(self.js_args_)
            else:
                return self.JAVASCRIPT
        else:
            return ""

    def css(self):
        if hasattr(self, "css_"):
            return self.css_
        else:
            return ""
        
class PointHTMLTooltip2(PluginBase):

    def __init__(self, points, labels=None,
                 hoffset=0, voffset=10, css=None):
        self.points = points
        self.labels = labels
        self.voffset = voffset
        self.hoffset = hoffset
        self.css_ = css or ""
        if isinstance(points, matplotlib.lines.Line2D):
            suffix = "pts"
        else:
            suffix = None
        self.dict_ = {"type": "htmltooltip",
                      "id": utils.get_id(points, suffix),
                      "labels": labels,
                      "hoffset": hoffset,
                      "voffset": voffset}

form = cgi.FieldStorage()
jsons = form.getvalue('jsons')
sampleID = json.loads(jsons)
sessionid = form.getvalue('sessionid')
organism = form.getvalue('organism')
host = form.getvalue('host')
port = form.getvalue('port')
user = form.getvalue('user')
passwd = form.getvalue('passwd')
unix_socket = form.getvalue('unix_socket')

#sampleID = {'group1':['HCT116-21-3-c1', 'HCT116-21-3-c3', 'HCT116-5-4', 'HCT116-5-4-p'],'group2':['HCT116-8-3-c3', 'HCT116-8-3-c4', 'RPE-21-3-c1', 'RPE-21-3-c1-p','RPE-21-3-c2', 'RPE-5-3-12-3-p']}
#sessionid= "test"
#organism = "Human"
#host = "localhost"
#port = 3306
#user = "root"
#passwd = ""
#unix_socket = "/tmp/mysql.sock"


isGroup = isinstance(sampleID, dict)

if (isGroup):
    grouping = pd.DataFrame()
    for group in sampleID:
        grouping_tmp = pd.DataFrame(np.array(sampleID[group]), columns = ["sampleID"])
        grouping_tmp['group'] = group
        if grouping.empty:
            grouping = grouping_tmp
        else:
            grouping = pd.concat([grouping,grouping_tmp])
    
    grouping.drop_duplicates(subset='sampleID', keep="first")
    sampleID = grouping['sampleID']

#connecting to mysql database
conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=organism, unix_socket=unix_socket)
query = 'SELECT sampleID, gene, log2 FROM target_exp WHERE sampleID in ('+','.join(map("'{0}'".format, sampleID))+') AND userID in ("mitox","'+sessionid+'")'
main = pd.read_sql(query, con=conn)
query = 'SELECT gene, process from target'
genefunc = pd.read_sql(query, con=conn)
conn.close()

main.loc[main.log2 > 10, 'log2'] = 10
main.loc[main.log2 < -10, 'log2'] = -10

if (isGroup):
    main = pd.merge(main,grouping,on='sampleID',how='inner')
    main = main.groupby(['group','gene'])['log2'].mean().unstack('group')
    main.reset_index(inplace=True)
    main = pd.melt(main,id_vars=['gene'],var_name='sampleID', value_name='log2')

main = main.pivot(index='gene',columns='sampleID',values='log2')
main.reset_index(inplace=True)
main = pd.merge(genefunc,main,on="gene",how='inner')
main.set_index("gene",inplace=True)

cmd = "rm -R ../data/user_uploads/" + ''.join(sessionid) + "/heatmap/*"
os.system(cmd)

targetpath= "../data/user_uploads/" + ''.join(sessionid) + "/combined-heatmap.csv"
main.to_csv(targetpath)

outputpath= "../data/user_uploads/" + ''.join(sessionid) + "/heatmap/"

processes = sorted(main.process.unique())
processes = processes[0:5]
for process in processes:
    
    df = main[main['process'] == process]   
    df.drop(['process'],1,inplace=True)
    df.dropna(thresh=len(df.columns)*0.5,inplace=True)
    mask = df.isnull()
    df.fillna(0,inplace=True)
    
    if (df.shape[0] >= 3):
    
        cbar_kws = { 'vmin' : -2, 'vmax':2, 'cmap':'RdBu' }
        cm= seaborn_hm.clustermap(df,mask=mask,**cbar_kws)
        
        p = cm.heatmap.mesh
        df2 = cm.data2d
        dcol = cm.ax_col_dendrogram.get_position()
        drow = cm.ax_row_dendrogram.get_position()
        cax = cm.cax.get_position()
        hm = cm.ax_heatmap.get_position()
        cm.ax_col_dendrogram.set_position([dcol.x0-drow.width*0.75, dcol.y0, dcol.width, dcol.height*0.75])
        cm.ax_row_dendrogram.set_position([drow.x0, drow.y0, drow.width*0.25, drow.height])
        cm.ax_heatmap.set_position([hm.x0-drow.width*0.75, hm.y0, hm.width, hm.height])
        cm.cax.set_position([cax.x0,cax.y0,cax.width,cax.height*0.75])
        
        
        df2 = df2.T
        df2= df2[df2.columns[::-1]]
        
        df3 = pd.DataFrame()
        index=0
        rowc=0
        for row in df2:
            colc=0
            for col in df2[row]:
                thing = {'gene': [row], 'sample': [df2.index[colc]], 'value': col}
                things = pd.DataFrame(thing, index=[index])
                if df3.empty:
                    df3 = things
                else:
                    df3 = pd.concat([df3,things])
                colc += 1
                index += 1
            rowc+=1
        
        labels = df3.to_json(orient='records')
        
        tooltip = PointHTMLTooltip2(p, labels,voffset=10, hoffset=10)
        plugins.connect(cm.fig, tooltip)
        
        html = mpld3.fig_to_dict(cm.fig)
        outputname = outputpath + process+ '.json'
        with open(outputname, 'w') as fp:
            json.dump(html, fp)

        
print "Content-type: text/html\n"
print "<html>"
print sessionid
print "</html>"
#print("--- %s seconds ---" % (time.time() - start_time))