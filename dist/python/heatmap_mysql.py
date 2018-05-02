#!/usr/bin/env python

import cgi, os, re, sys
#import cgitb;cgitb.enable()
import json
import pandas as pd
import numpy as np
import collections

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

import mpld3
from mpld3 import utils
from mpld3 import plugins
import seaborn_hm
import os.path

#import seaborn as sns

form = cgi.FieldStorage()
targeturl = "."+form.getvalue('targeturl')
# targeturl = "."+"./data/user_uploads/test/heatmap/33655/Amino Acid Metabolism.json"

urlbd = targeturl.split("/")
analysisID = urlbd[len(urlbd)-1].split("_")[0]
main_exp_path = "/".join(urlbd[0:len(urlbd)-1])+"/"+analysisID+"_main_exp.csv"
main_all_path = "/".join(urlbd[0:len(urlbd)-1])+"/"+analysisID+"_main.csv"
genefunc_path = "/".join(urlbd[0:len(urlbd)-1])+"/"+analysisID+"_genefunc.csv"
process = urlbd[len(urlbd)-1].split(".json")[0].split("_")[1]


if not os.path.isfile(targeturl):

    class NumpyEncoder(json.JSONEncoder):
        """ Special json encoder for numpy types """

        def default(self, obj):
            if isinstance(obj, (numpy.int_, numpy.intc, numpy.intp, numpy.int8,
                numpy.int16, numpy.int32, numpy.int64, numpy.uint8,
                numpy.uint16,numpy.uint32, numpy.uint64)):
                return int(obj)
            elif isinstance(obj, (numpy.float_, numpy.float16, numpy.float32, 
                numpy.float64)):
                return float(obj)
            elif isinstance(obj,(numpy.ndarray,)): #### This is the fix
                return obj.tolist()
            return json.JSONEncoder.default(self, obj)

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

    main_exp = pd.read_csv(main_exp_path)
    #main_exp.set_index(['geneID'],inplace=True)

    df = main_exp[main_exp['process'] == process]  

    if (df.shape[0] >= 3):

        df.set_index(['geneID'],inplace=True)
        #df.dropna(thresh=len(df.columns)*0.5,inplace=True)
        df.drop(['process'],1,inplace=True)
        mask = df.isnull()
        df.fillna(0,inplace=True)

        ratio = float(df.shape[0])/50
        if (ratio < 1):
            ratio = 1
        canvasHeight = (0.65*ratio + 0.35)*800+100
        cbar_kws = { 'vmin' : -2, 'vmax':2, 'cmap':'RdBu'}
        cm= seaborn_hm.clustermap(df,mask=mask,**cbar_kws)

        p = cm.heatmap.mesh
        df2 = cm.data2d
        dcol = cm.ax_col_dendrogram.get_position()
        drow = cm.ax_row_dendrogram.get_position()
        cax = cm.cax.get_position()
        hm = cm.ax_heatmap.get_position()
        cm.ax_col_dendrogram.set_position([dcol.x0, dcol.y0, dcol.width, 0.11])
        cm.ax_row_dendrogram.set_position([drow.x0, drow.y0-(drow.height*(ratio-1)), drow.width, drow.height*ratio])
        cm.ax_heatmap.set_position([hm.x0, hm.y0-(hm.height*(ratio-1)), hm.width, hm.height*ratio])
        #cm.ax_heatmap.set_position([hm.x0, hm.y0, hm.width, hm.height*ratio/canvasHeightRatio])
        #cm.cax.set_position([cax.x0,cax.y0,cax.width,cax.height])
        cm.cax.set_position([cax.x0,cax.y0-(cax.height*0.25),cax.width,cax.height*0.75])

        # cm.ax_col_dendrogram.set_position([dcol.x0, dcol.y0+((ratio-1)*0.04), dcol.width, 0.1])
        # cm.ax_row_dendrogram.set_position([drow.x0, drow.y0+((ratio-1)*0.04), drow.width, drow.height])
        # cm.ax_heatmap.set_position([hm.x0, hm.y0+((ratio-1)*0.04), hm.width, hm.height*ratio/1.5])
        # cm.cax.set_position([cax.x0,cax.y0+((ratio-1)*0.04)-0.02,cax.width,0.1])

        # print(cm.fig)

        df2 = cm.data2d
        genes = list(reversed(df2.index.tolist()))
        samples = df2.columns.tolist() * len(df2.index)
        genes = list(np.repeat(genes,len(df2.columns)))
        df3 = pd.DataFrame({'sampleID': samples, 'geneID': genes})

        genefunc = pd.read_csv(genefunc_path)
        genefunc.drop_duplicates('geneID',inplace=True)

        main_all = pd.read_csv(main_all_path)
        main_all.drop_duplicates(subset=['geneID','sampleID'],inplace=True)

        df3 = pd.merge(df3,genefunc,on=['geneID'],how='left')
        df3 = pd.merge(df3,main_all,on=['geneID','sampleID'],how='left')

        labels = df3.to_json(orient='records')

        tooltip = PointHTMLTooltip2(p, labels,voffset=10, hoffset=10)
        plugins.connect(cm.fig, tooltip)

        html = mpld3.fig_to_dict(cm.fig)
        json_all = [{'svg' : html, 'canvasHeight' : canvasHeight}]

        with open(targeturl, 'w') as fp:
            json.dump(json_all, fp, cls=NumpyEncoder)


print "Content-type: text/html\n"
print "<html>"
print sessionid
print "</html>"

# print 'Content-Type: application/json\n\n'
# print (output)

# print "Content-type: text/html\n"
# print (hm.height)
