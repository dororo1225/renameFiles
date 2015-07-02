# coding:utf-8
__author__ = 'yamamoto'
# env: Python2.7

import os
import cv2
import datetime
import numpy as np
import pandas as pd
import sys

# ################################################
# #  初期入力
# ################################################
#
# # 何秒おきにデータを入力するか
scan_int = 30  # (seconds)


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
        try:
            before = s.replace(month=s.month - 1, day=b.day)
            days = (s - before).days
        except ValueError:
            days = s.day
            # 2月は1ヶ月バックするとエラーになる時がある(誕生日が29-31日の時)
            # なのでそうなった場合は、すでに前月の誕生日を迎えたことにする（setされた日が日数とイコールになる）
    return days


def perdelta(start, end, delta):
    curr = start
    while curr <= end:
        yield curr
        curr += delta



################################################
#  メイン処理
################################################

# 調査情報の取得
obs_id = os.getcwd().split('\\')[-1]
NameID = obs_id[0:6]
obs_str = obs_id[6:12]

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
    if len(infants.query("NameID==@NameID")) == 0:
        e_name = "There is no name like " + NameID
        print "-----------------------------------"
        print e_name
        print "Check participant's name"
        print "-----------------------------------"
    else:
        df = infants.query("NameID==@NameID")
        print df
        print
except Exception, e_name:
    print "-----------------------------------"
    print "error occured"
    print e_name
    print "-----------------------------------"


# 調査日程・誕生日から月齢・日齢を計算
# NameID・調査日程を取得
idx_nid = df.index[0]  # インデックスを取得
datetime_birth = datetime.datetime.strptime(df.ix[idx_nid, "Birth"], '%Y/%m/%d')
datetime_obs = datetime.datetime.strptime(obs_str, '%y%m%d')
Age_days = (datetime_obs - datetime_birth).days  # 日齢
Months = count_months(datetime_birth, datetime_obs) # 月齢
Days = count_days(datetime_birth, datetime_obs) # 余り日

print obs_id
print NameID
print obs_str
print 'age in days :',  Age_days
print 'age in months :', Months
print 'days:', Days
print

# 動画情報を取得

files = os.listdir(os.getcwd())
videos = [file for file in files if file.startswith('GP_')]

if len(videos) == 0:
    print '-------------------------------------'
    print 'there is no file starts with "GP_". '
    print '-------------------------------------'
else:
    df = pd.DataFrame({'ObsID': [],
                       'NameID': [],
                       'Observe': [],
                       'AgeinDays': [],
                       'AgeinMonth': [],
                       'Days': [],
                       'VideoName': [],
                       'VideoTime': [],
                       'Posture': [],
                       'Memo1': [],
                       'Memo2': []}
                      )
    for video in videos:
        # # ビデオの読み込み・プロパティの取得
        cap = cv2.VideoCapture(video)  # Read Video File
        FrameRate = float(cap.get(cv2.cv.CV_CAP_PROP_FPS))
        FrameNum_Total = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, FrameNum_Total)
        TotalMinutes = int(cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC)) / 1000 / 60
        cap.release()  # キャプチャー解放
        print 'video', video
        print 'FrameRate', FrameRate, '(fps)'
        print 'TotalFrameNumber', FrameNum_Total
        print 'VideoTime', TotalMinutes
        print

        scan_time = []
        video_start = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
        video_end = video_start + datetime.timedelta(minutes=TotalMinutes)
        for result in perdelta(video_start, video_end, datetime.timedelta(seconds=scan_int)):
            scan_time.append(result)

        df_video = pd.DataFrame({'ObsID': [obs_id] * len(scan_time),
                                 'NameID': [NameID] * len(scan_time),
                                 'Observe': [obs_str] * len(scan_time),
                                 'AgeinDays': [Age_days] * len(scan_time),
                                 'AgeinMonth': [Months] * len(scan_time),
                                 'Days': [Days] * len(scan_time),
                                 'VideoName': [video] * len(scan_time),
                                 'VideoTime': scan_time,
                                 'Posture': np.array([None] * len(scan_time)),
                                 'Memo1': np.array([None] * len(scan_time)),
                                 'Memo2': np.array([None] * len(scan_time))
                                 })
        df = pd.concat([df, df_video], ignore_index=True)

    # 列の並び替え
    df = df[['ObsID', 'NameID', 'Observe', 'AgeinDays', 'AgeinMonth', 'Days',
             'VideoName', 'VideoTime', 'Posture', 'Memo1', 'Memo2']]

    # ファイル出力
    file_dir = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + '\\Documents' + '\\Fieldwork_data\\PostureData'
    os.chdir(file_dir)
    csv_name = 'Posture_' + obs_id + '.csv'
    df.to_csv(csv_name, index=False)
    print df