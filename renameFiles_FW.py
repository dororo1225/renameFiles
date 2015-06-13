# -*- coding: utf-8 -*-
__author__ = 'yamamoto'
# env: Python2.7

import os
import pandas as pd
import datetime

################################################
#  初期入力
################################################

# 参加者の名前を入力
Name = 'hogehoge'

# 調査日程を以下の形式で入力
# Date = '2015-06-01'
tstr = '2015-06-30'


################################################
#  処理関数
################################################

def day_input(text=None):
    if text is None:
        if sys.version_info.major > 2:  # 3系かどうかの判定
            return input()
        else:
            return raw_input()  # python2ではraw_input
    else:
        if sys.version_info.major > 2:  # 3系かどうかの判定
            return input(text)
        else:
            return raw_input(text)  # python2ではraw_input


def set_day():
    sday = day_input('Please enter base date (e.g. 2015/06/04, None => today)  ')
    return sday

# 誕生日を入力させる
def get_birthday():
    # 入力待ち(関数を別に作ってPython2系にも対応)
    bday = day_input('Please enter ones birthday (e.g. 2015/06/04)  ')
    return bday


# 年齢の計算（閏日補正含む） ：今何歳何ヶ月なのか？
def count_years(b, s):
    try:
        this_year = b.replace(year=s.year)
    except ValueError:
        b += timedelta(days=1)
        this_year = b.replace(year=s.year)

    age = s.year - b.year
    if base_day < this_year:
        age -= 1

# 何歳”何ヶ月”を計算
    if (s.day - b.day) >= 0:
        year_months = (s.year - b.year) * 12 - age * 12 + (s.month - b.month)
    else:
        year_months = (s.year - b.year) * 12 - age * 12 + (s.month - b.month) - 1  # 誕生日が来るまでは月齢も-1

    return age, year_months


# 月齢の計算
def count_months(b, s):
    if (s.day - b.day) >= 0:
        months = (s.year - b.year) * 12 + (s.month - b.month)
    else:
        months = (s.year - b.year) * 12 + (s.month - b.month) - 1  # 誕生日が来るまでは月齢も-1
    return months


# 月齢および何歳何ヶ月の余り日数（何歳何ヶ月”何日”）
def count_days(b, s):
    if (s.day - b.day) >= 0:
        days = s.day - b.day
    else:
        before = s.replace(month=s.month - 1, day=b.day)
        days = (s - before).days
    return days


################################################
#  メイン処理
################################################

if __name__ == '__main__':
    # 日付入力を確認
    try:
        datetime_obs = datetime.datetime.strptime(tstr, '%Y-%m-%d')
        print 'date of observation:', tstr
        print
    except Exception, e_date:
        print "-----------------------------------"
        print "error occured"
        print e_date
        print "-----------------------------------"


# 参加者データの読み込み
    desktop_path = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop"
    try:
        infants = pd.read_csv(desktop_path + '\\infants.csv')
    except Exception, e_file:
        print "-----------------------------------"
        print "error occured"
        print e_file
        print "-----------------------------------"

    try:
        if len(infants.query("Name==@Name")) == 0:
            e_name = "There is no name like " + Name
            print "-----------------------------------"
            print e_name
            print "Check participant's name"
            print "-----------------------------------"
        else:
            df = infants.query("Name==@Name")
            print df
            print
    except Exception, e_name:
        print "-----------------------------------"
        print "error occured"
        print e_name
        print "-----------------------------------"


if not ('e_date' in locals() or 'e_file' in locals() or 'e_name' in locals()):
        # 調査日程・誕生日から月齢・日齢を計算
        # NameID・調査日程を取得
        idx = df.index[0]  # インデックスを取得
        NameID = df.ix[idx, "NameID"]
        datetime_birth = datetime.datetime.strptime(df.ix[idx, "Birth"], '%Y/%m/%d')

        # 日齢計算
        Age_days = (datetime_obs - datetime_birth).days  # 日齢
        print 'age in days:',  Age_days

        # 月齢計算・余り日数計算
        Months = count_months(datetime_birth, datetime_obs)
        Days = count_days(datetime_birth, datetime_obs)
        print 'age in months;', Months
        print 'days:', Days
        print

        # 調査日程の記録をcsv出力
        df_obs = pd.DataFrame({'Obs': [datetime_obs.strftime('%Y/%m/%d')],
                               'AgeinDays': [Age_days],
                               'Months': [Months],
                               'Days': [Days]},
                               index=[idx])
        df_obs = df_obs[['Obs', 'AgeinDays', 'Months', 'Days']]
        df = pd.concat([df, df_obs], axis=1)
        print df
        if os.path.isfile(desktop_path + '\\Observation.csv'):
            df_old = pd.read_csv(desktop_path + '\\Observation.csv')
            del df_old['ObsID']
            df = pd.concat([df_old, df], axis=0)
            # 重複行があれば削除
            df = df[df.duplicated() == False]
        df = df.sort('Obs')  # 観察日順に並び替え
        df.insert(0, 'ObsID', range(1, len(df)+1))
        print df
        df.to_csv(desktop_path + '\\Observation.csv', index=False)


        # 映像データをRename
        fileID = NameID + str(datetime_obs.year)[-2:] + str(datetime_obs.month).zfill(2) + str(datetime_obs.day).zfill(2)
        files = os.listdir(os.getcwd()) # ディレクトリのファイル全体を取得

        # ファイルの更新日時を取得
        GP ={}
        TB ={}
        AD ={}
        for file in files:
            if file.startswith('GP') or file.startswith('GOPR'):
               GP[os.stat(os.path.join(file)).st_mtime] = file
            elif file.endswith('mp4'):
               TB[os.stat(os.path.join(file)).st_mtime] = file
            elif file.endswith('mp3'):
                AD[os.stat(os.path.join(file)).st_mtime] = file

        if len(GP) != 0:
            i = 0
            for st_mtime, fileName in sorted(GP.items()):
                i += 1
                newName = 'GP_' + fileID + '_' + str(i) + '.mp4'
                os.rename(fileName, newName)

        if len(TB) != 0:
            i = 0
            for st_mtime, fileName in sorted(TB.items()):
                i += 1
                newName = 'TB_' + fileID + '_' + str(i) + '.mp4'
                os.rename(fileName, newName)

        if len(AD) != 0:
            i = 0
            for st_mtime, fileName in sorted(AD.items()):
                i += 1
                newName = 'AD_' + fileID + '_' + str(i) + '.mp3'
                os.rename(fileName, newName)