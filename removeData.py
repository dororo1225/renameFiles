# -*- coding: utf-8 -*-
__author__ = 'yamamoto'
# env: Python2.7

import os
import datetime
import pandas as pd
import sys

# ################################################
# #  初期入力
# ################################################
#
# # 参加者の名前を入力
NameID = 'HOGEHOGE'
# like 'YAMAMO'
# NameID = 'INOKEI'

str = '2015-07-01'
# like '2015-05-07'

################################################
#  メイン処理
################################################

datetime_obs = datetime.datetime.strptime(str, '%Y-%m-%d')
print 'datetime_obs', datetime_obs
print

# 参加者データの読み込み
desktop_path = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop"
try:
    data = pd.read_csv(desktop_path + '\\Observation_hoken.csv')
except Exception, e_file:
    print "-----------------------------------"
    print "error occured"
    print e_file
    print "-----------------------------------"

try:
    if len(data.query("NameID==@NameID")) == 0:
        e_name = "There is no NameID like " + NameID
        print "-----------------------------------"
        print e_name
        print "Check participant's NameID"
        print "-----------------------------------"
except Exception, e_name:
    print "-----------------------------------"
    print "error occured"
    print e_name
    print "-----------------------------------"


for idx in data.index:
    data.ix[idx, 'Obs'] = datetime.datetime.strptime(data.ix[idx, 'Obs'], '%Y/%m/%d %H:%M')

if 'e_name' not in locals():
    # 除きたい行を抽出
    data_remove = data[data['NameID'] == NameID]
    if len(data_remove) != 0:
        data_remove = data_remove[data_remove['Obs'].dt.year.isin([datetime_obs.year])]
    if len(data_remove) != 0:
        data_remove = data_remove[data_remove['Obs'].dt.month.isin([datetime_obs.month])]
    if len(data_remove) != 0:
        data_remove = data_remove[data_remove['Obs'].dt.day.isin([datetime_obs.day])]
    if len(data_remove) == 0:
        print '-------------------------------------------'
        print 'There is no row you are going to delete'
        print 'Check pair of NameID and ObservDay'
        print '-------------------------------------------'
    else:
        idx_remove = data_remove.index
        data_removed = data[data.index != idx_remove]

        del data_removed['ObsID']
        data_removed = data_removed.sort('Obs')
        data_removed.insert(0, 'ObsID', range(1, len(data_removed)+1))  # ObsIDをつける
        data_removed = data_removed.sort(['id', 'Obs'])  # id, ObsIDの順にソート
        # data_removed.to_csv(desktop_path + '\\Observation.csv', index=False)

        print 'data.shape', data.shape
        print
        print 'data_removed.shape', data_removed.shape
        print
        print 'data_remove'
        print data_remove