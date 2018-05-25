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

# sampleID = ['HCT116-21-3-c1', 'HCT116-21-3-c3', 'HCT116-5-4', 'HCT116-5-4-p']
# sessionid= "testAnnie"
# organism = "Human"
# host = "localhost"
# port = 3306
# user = "root"
# passwd = ""
# unix_socket = "/tmp/mysql.sock"
# upper_limit = 2
# lower_limit = -2


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
query1 = 'SELECT target_exp.sampleID, target_exp.geneID, target_exp.log2, target_exp.pvalue, target_mut.mutation FROM target_exp LEFT JOIN target_mut ON target_exp.sampleID=target_mut.sampleID AND target_exp.geneID=target_mut.geneID WHERE target_exp.sampleID in ('+','.join(map("'{0}'".format, sampleID))+') AND target_exp.userID in ("mitox","'+sessionid+'")'
main = pd.read_sql(query1, con=conn)
query2 = 'SELECT * from target'
genefunc = pd.read_sql(query2, con=conn)
conn.close()

main = main.drop(main[(main.log2 > upper_limit) | (main.log2 < lower_limit)].index)

if (isGroup):
    main = pd.merge(main,grouping,on='sampleID',how='inner')
    log2 = main.groupby(['group','geneID'])['log2'].mean().unstack('group')
    log2.reset_index(inplace=True)
    log2 = pd.melt(log2,id_vars=['geneID'],var_name='sampleID', value_name='log2')
    mutation = main.groupby(['group','geneID'])['mutation'].count().unstack('group')
    mutation.reset_index(inplace=True)
    mutation = pd.melt(mutation,id_vars=['geneID'],var_name='sampleID', value_name='mutation')
    main = pd.merge(log2,mutation,how='left', on=['geneID','sampleID'])
    main['pvalue']=1
    main['mutation'].fillna(0,inplace=True)
    main['mutation'] = main['mutation'].astype(int).astype(str) + ' mutation(s)'
    main['isgroup'] = "y"
else:
    main['isgroup'] = "n"


main.fillna('',inplace=True)

main_exp = main.pivot(index='geneID',columns='sampleID',values='log2')
main_exp.reset_index(inplace=True)

main_exp = pd.merge(main_exp,genefunc[['geneID','process']],on="geneID",how='inner')

exist = True

# Generating new directory for storing the results
# Saving json output in database instead of file system?
# Storing with unique file name instead of 
while exist == True:
    newint = np.random.randint(low=10000, high=99999)
    targeturl = './data/user_uploads/'+sessionid+'/heatmap/'+str(newint)+'_'
    targetpath_main = "." + targeturl + "main.csv"
    exist = os.path.isfile('.'+targetpath_main)

main.to_csv(targetpath_main, index=False)

targetpath_genefunc= "." + targeturl + "genefunc.csv"
genefunc.to_csv(targetpath_genefunc, index=False)

targetpath= "." + targeturl + "main_exp.csv"
main_exp.to_csv(targetpath,index=False)

processes = sorted(main_exp.process.unique())
pro_list = []
for process in processes:
    
    df = main_exp[main_exp['process'] == process]   
    df.drop(['process'],1,inplace=True)
    df.dropna(thresh=len(df.columns)*0.5,inplace=True)
    df.fillna(0,inplace=True)
    
    if (df.shape[0] >= 3):
        pro_list.append(targeturl+process+".json")
        
pro_list = json.dumps(pro_list)
        
print 'Content-Type: application/json\n\n'
print (pro_list)