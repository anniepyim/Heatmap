#!/usr/bin/env python

import cgi, os, re, sys
import cgitb;cgitb.enable()
import json
import pandas as pd
import numpy as np
import collections

import pymysql


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
upper_limit = float(form.getvalue('upper_limit'))
lower_limit = float(form.getvalue('lower_limit'))


#sampleID = ['HCT116-21-3-c1', 'HCT116-21-3-c3', 'HCT116-5-4', 'HCT116-5-4-p']
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
query1 = 'SELECT sampleID, gene, log2 FROM target_exp WHERE sampleID in ('+','.join(map("'{0}'".format, sampleID))+') AND userID in ("mitox","'+sessionid+'")'
main = pd.read_sql(query1, con=conn)
query = 'SELECT gene, process, gene_function from target'
genefunc = pd.read_sql(query, con=conn)
conn.close()

main = main.drop(main[(main.log2 > upper_limit) | (main.log2 < lower_limit)].index)

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
pro_list = []
for process in processes:
    
    df = main[main['process'] == process]   
    df.drop(['process'],1,inplace=True)
    df.drop(['gene_function'],1,inplace=True)
    df.dropna(thresh=len(df.columns)*0.5,inplace=True)
    mask = df.isnull()
    df.fillna(0,inplace=True)
    
    if (df.shape[0] >= 3):
        pro_list.append(process)
        
pro_list = json.dumps(pro_list)
        
print 'Content-Type: application/json\n\n'
print (pro_list)