# coding: utf_8
import json
import websocket
import _thread
import time
import pyautogui
import os
from pathlib import Path
import datetime
from decimal import Decimal, ROUND_HALF_UP
import re
import sys
import subprocess
import codecs
import shutil

class Websocket_Client():

    def __init__(self, host_addr):

        # デバックログの表示/非表示設定
        #websocket.enableTrace(True)

        # WebSocketAppクラスを生成
        # 関数登録のために、ラムダ式を使用
        self.ws = websocket.WebSocketApp(host_addr,
            on_message = lambda ws, msg: self.on_message(ws, msg),
            on_error   = lambda ws, msg: self.on_error(ws, msg),
            on_close   = lambda ws: self.on_close(ws))
        self.ws.on_open = lambda ws: self.on_open(ws)

    # メッセージ受信に呼ばれる関数
    def on_message(self, ws, message):
        #print("receive : {}".format(message))
        #test = "songStart" in message
        #print(test)
        
        json_load = json.loads(message)#1回目の"songStart"は"star"のキーが無い
        if json_load["event"] == "songStart" and json_load.get("status",{}).get("beatmap",{}).get("star") == None:
            #print("\nevent",json_load["event"])
            #print("\n1回目のsongStart eventなので曲情報は記録しません")
            print("\n--------------Start recording------------------------")
            ##"star"のキーが無いから録画開始
            pyautogui.press(recstartkey)
        elif json_load["event"] == "songStart":
            #print("2回目のsongStart eventなので曲情報を記録します")
            #json_load["status"]["beatmap"]["songCover"] = ""#長いので消す
            global event_start
            event_start = json_load
            songName = json_load["status"]["beatmap"]["songName"]
            print("曲名 ",songName)
        if json_load["event"] == "failed" or json_load["event"] == "finished":
            if json_load["event"] == "finished":
                t = htos
                print("Completed")
            else:
                t = htof
                print("Withdrawal on the way")
            print("GameOver",t,"second countdown")
            while t>0:
                print(t)
                time.sleep(1)
                t -= 1            
            pyautogui.press(recendkey)
            global event_end
            event_end = json_load
            print("--------------Recording end--------------------------")           
            print("----------Disconnect WebSocket once--------------")
            ws.close()

    # エラー時に呼ばれる関数
    def on_error(self, ws, error):
        print(error)

    # サーバーから切断時に呼ばれる関数
    def on_close(self, ws):
        print("### closed ###")

    # サーバーから接続時に呼ばれる関数
    def on_open(self, ws):
        _thread.start_new_thread(self.run, ())

    # サーバーから接続時にスレッドで起動する関数
    def run(self, *args):
        while True:
            time.sleep(0.1)
            input_data = input("websocket connection OK:") 
            self.ws.send(input_data)
    
        self.ws.close()
        print("thread terminating...")
    
    # websocketクライアント起動
    def run_forever(self):
        self.ws.run_forever()

default_setting = {"basic_setting":{"Recording_holder":"V:\\OBSREC\\",\
"0010":"_______________________________Recording_holder　OBS Studioの録画ファイルのパス",\
"Move_folder_after_renaming":"OK",\
"0020":"_______________________________Move_folder_after_renaming　録画後移動するフォルダー　nullで移動しない　録画フォルダ内に作成します(フォルダ名のみ)",\
"Move_folder_when_game_fails":"Failed",\
"0030":"_______________________________Move_folder_when_game_fails　ゲーム失敗した場合に移動するフォルダー",\
"Hold_time_on_failure":4,\
"0040":"_______________________________Hold_time_on_failure　ゲーム途中終了時の録画停止を遅らせる時間(秒)",\
"Hold_time_on_success":9,\
"0050":"_______________________________Hold_time_on_success　ゲーム成功時の録画停止を遅らせる時間(秒)",\
"OBS_recording_start_hotkey":"f7",\
"0060":"_______________________________OBS_recording_start_hotkey　OBSの録画開始ホットキー",\
"OBS_recording_end_hotkey":"f8",\
"0070":"_______________________________OBS_recording_end_hotkey　OBSの録画終了ホットキー",\
"songName_length":20,\
"0080":"_______________________________songName_length　曲名の最大文字数",\
"songSubName_length":20,\
"0090":"_______________________________songSubName_length　曲名(サブネーム)の最大文字数",\
"songAuthorName_length":20,\
"0100":"_______________________________songAuthorName_lengt　アーチスト名の最大文字数",\
"mapper_length":20,\
"0110":"_______________________________mapper_length　マップ作成者の最大文字数",\
"space_or_Underbar":"_",\
"0120":"_______________________________space_or_Underbar　曲名などにスペースが含まれる場合に変換する文字(スペースでも問題なし)",\
"log_enable":"true",\
"0130":"_______________________________log_enable　trueでログをとる　falseでログをとらない",\
"organize_names":"<songName>-<mapper>_[<difficulty>]#<percent>#[<rank>]_[<current_pp>pp]_(<maxCombo>-<hitNotes>-<missedNotes>)_[★<star>]_<recording_time>_[<success_failure>]",\
"0140":"_______________________________以下の<と>で括ったものは曲名などに変換されます",\
"0141":"_______________________________括られていないものはそのまま　全角も使用可たぶん",\
"<songName>":"曲名","<songSubName>":"曲名（サブネーム）","<songAuthorName>":"アーチスト名","<mapper>":"マップ作成者",\
"<difficulty>":"難易度","<star>":"難易度数","<notesCount>":"総ノーツ数","<recording_time>":"録画終了時間",\
"<percent>":"成功率","<rank>":"ランクSS~E","<current_pp>":"PP","<maxCombo>":"Maxコンボ","<hitNotes>":"ヒットノーツ",\
"<missedNotes>":"ミスノーツ","<success_failure>":"成功か失敗か"}}
if not os.path.isfile("setting.json"):
    print("setting.jsonがないのでデフォルトのsetting.jsonを作ります")
    print("デンバ時計さん製作のHttpSiraStatusとHttpStatusExtentionが必要となります。")
    print("HttpSiraStatusは転送される画像データが大きいと遅延が発生して録画が失敗することがあるので")
    print("画像データを小さくする改変版のHttpSiraStatusと差し替えると遅延が少なくなります。")
    print("")
    print("OBS Studioの録画ファイルのパスと録画開始と録画終了のホットキーを設定してください。")
    print("")
    print("OBS Studioの設定に合わせsetting.jsonを編集します。")
    print("OBS_recording_start_hotkeyとOBS_recording_end_hotkey (デフォルトはf7とf8)")
    print("Recording_holder OBSの録画ファイルのパス")
    print("Hold_time_on_failure ゲーム途中終了時の録画停止タイミング(秒)")
    print("Hold_time_on_success ゲーム成功時の録画停止タイミング(秒)")
    print("songName_length 曲名の最大文字数 (songSubName_length songAuthorName_length mapper_lengthも同じ)")
    print("space_or_Underbar 曲名などにスペースが含まれる場合に変換する文字(スペースでも問題なし)")   
    print("log_enable trueでログをとる　falseでログをとらない")
    print("organize_names ファイル名にする文字列")
    print("    <songName>など<>で括られたものはHttpSiraStatusから送られてきたデータに変換されます。")
    print("    括られていないものはそのまま反映します。")
    print("")
    tf = codecs.open("setting.json", "w", "utf-8")
    json.dump(default_setting,tf,indent=4, ensure_ascii=False)
    tf.close()
    os.system("notepad.exe setting.json")
    os.system("notepad.exe readme.txt")
    exit()

        
setting_json = open("setting.json","r", encoding="utf-8").read()
setting = json.loads(setting_json)
rec_path = setting["basic_setting"]["Recording_holder"]
Move_folder_after_renaming = setting["basic_setting"]["Move_folder_after_renaming"]
Move_folder_when_game_fails = setting["basic_setting"]["Move_folder_when_game_fails"]
htof = setting["basic_setting"]["Hold_time_on_failure"]
htos = setting["basic_setting"]["Hold_time_on_success"]
recstartkey = setting["basic_setting"]["OBS_recording_start_hotkey"]
recendkey = setting["basic_setting"]["OBS_recording_end_hotkey"]
organize_names = setting["basic_setting"]["organize_names"]
songName_length = setting["basic_setting"]["songName_length"]
songSubName_length = setting["basic_setting"]["songSubName_length"]
songAuthorName_length = setting["basic_setting"]["songAuthorName_length"]
space_or_Underbar = setting["basic_setting"]["space_or_Underbar"]
mapper_length = setting["basic_setting"]["mapper_length"]
log_enable = setting["basic_setting"]["log_enable"]
if Move_folder_after_renaming != "":
    if not os.path.exists(rec_path + Move_folder_after_renaming):
        print(Move_folder_after_renaming,"フォルダーを作成します")
        os.makedirs(rec_path + Move_folder_after_renaming)
if Move_folder_when_game_fails != "":
    if not os.path.exists(rec_path + Move_folder_when_game_fails):
        print(Move_folder_when_game_fails,"フォルダーを作成します")
        os.makedirs(rec_path + Move_folder_when_game_fails)
if log_enable == "true":
    if not os.path.exists("log"):
        print("logフォルダーを作成します")
        os.makedirs("log")

#ファイル名に「使ってはいけない」文字　\⁄:*?"><|の変換と文字列数の切り詰め
def chr_cov(before,name_length):
    return before.replace("?","？").replace("*","＊").replace(":","：").replace("\\","＼").replace("⁄","／").replace(">","＞").replace("<","＜").replace("|","｜")[0:name_length]

i = 0
print("100回で終了します")

while i < 100:
    print(i)
    i += 1
    event_start = {}
    result = {}

    HOST_ADDR = "ws://localhost:6557/socket"
    ws_client = Websocket_Client(HOST_ADDR)
    ws_client.run_forever()

    ###########################################################################################
    if not event_start:
        print("BeatSaber is not running")
    else:
        #ファイル名に「使ってはいけない」文字　\⁄:*?"><|
        #ダブルクオートで括らなければならない文字 & ( ) [ ] { } ^ = ; ! ' + , ` ~
        #曲名を指定された文字数に切り詰める

        result["songName"] = chr_cov(event_start["status"]["beatmap"]["songName"],songName_length)
        result["songSubName"] = chr_cov(event_start["status"]["beatmap"]["songSubName"],songSubName_length)
        result["songAuthorName"] = chr_cov(event_start["status"]["beatmap"]["songAuthorName"],songAuthorName_length)
        result["mapper"] = chr_cov(event_start["status"]["beatmap"]["levelAuthorName"],mapper_length)
        result["difficulty"] = event_start["status"]["beatmap"]["difficulty"].replace("Expert+","ExpertPlus")#難易度の名前を変更
        result["star"] = str(event_start["status"]["beatmap"]["star"])#数値から文字列
        result["notesCount"] = str(event_start["status"]["beatmap"]["notesCount"])#数値から文字列
        #以上は開始前情報
        #以下は結果情報
        time_e = event_end["time"]
        jst_time = datetime.datetime.fromtimestamp(int(time_e/1000))#日本時間に修正
        result["recording_time"] = jst_time.strftime('%Y%m%d%H%M%S')#14桁の時間表記文字列に変換
        relativeScore = event_end["status"]["performance"]["relativeScore"]
        y = Decimal(str(relativeScore*100))#少数第二位四捨五入
        result["percent"] = str(y.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        result["rank"] = event_end["status"]["performance"]["rank"]
        pp =  event_end["status"]["performance"]["current_pp"]
        y = Decimal(str(pp))#少数第二位四捨五入
        result["current_pp"] = str(y.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        result["maxCombo"] = str(event_end["status"]["performance"]["maxCombo"])
        result["hitNotes"] = str(event_end["status"]["performance"]["hitNotes"])
        result["missedNotes"] = str(event_end["status"]["performance"]["missedNotes"])

        p = Path(rec_path)
        files = list(p.glob("*"))#最新タイムスタンプのファイルを探す
        file_updates = {file_path: os.stat(file_path).st_mtime for file_path in files}
        rec_file = max(file_updates, key=file_updates.get)

        timetest = os.stat(rec_file).st_mtime
        if event_end["time"]/1000-timetest > 900:#録画ファイルが見つからなかった場合はexitする
            print("The detected file may not be the recorded file.")
            print("The recording folder is not set or it is not recorded by OBS.")
            exit()

        event = event_end["event"]
        if event == "failed":
            result["success_failure"] = "failed"
        else:
            result["success_failure"] = "cleared"
        print("成功？",result["success_failure"])
        print("曲名",result["songName"])
        print("マッパー",result["mapper"])
        print("難易度",result["difficulty"])
        print("精度",result["percent"])
        print("ランク",result["rank"])
        print("pp",result["current_pp"])
        print("Maxコンボ",result["maxCombo"])
        print("ヒットノーツ",result["hitNotes"])
        print("ミスノーツ",result["missedNotes"])
        print("スター",result["star"])
        print("日時",result["recording_time"])

        #ファイル名のフォーマット(organize_names)を参照してファイル名を作る
        r = Path(rec_file)
        extension = os.path.splitext(r)[1]#extension　拡張子
        name_split = re.split("[<>]",organize_names)# <>で切り分けてリストに代入([変換しない文字列]と[変換させる文字列]が交互に並ぶ)
        division_number = len(name_split)# 切り分けた数
        reconnect = ""# 再連結させる変数
        for num in range(0,division_number,2):# 切り分けた奇数番目と偶数番目を一つずつ抽出
            reconnect += name_split[num]# 抽出した1番目の文字はそのまま連結
            n = num +1
            if n < division_number:# 切り分けた総数は奇数の為最後はエラーとなるので回避
                reconnect += result[name_split[n]]# 抽出した2番目の文字は辞書resultから参照して連結
        new_faile_name = Path(rec_path + reconnect.replace(' ',space_or_Underbar) + extension)
        
        time.sleep(1)#リネームのタイミングが早いため1秒ウエイト


        print("録画ファイル名",rec_file)
        print("リネームファイル名",new_faile_name)
        os.rename(rec_file,new_faile_name)
        if os.path.isfile(new_faile_name):
            print("リネーム成功")
        if result["success_failure"] == "cleared" and Move_folder_after_renaming != "":
            shutil.move(new_faile_name,rec_path + Move_folder_after_renaming)
            print(rec_path + Move_folder_after_renaming,"に移動")
        if result["success_failure"] == "failed" and Move_folder_after_renaming != "" and Move_folder_when_game_fails == "":
            shutil.move(new_faile_name,rec_path + Move_folder_after_renaming)
            print(rec_path + Move_folder_after_renaming,"に移動")
        if result["success_failure"] == "failed" and Move_folder_when_game_fails != "":
            shutil.move(new_faile_name,rec_path + Move_folder_when_game_fails)
            print(rec_path + Move_folder_when_game_fails,"に移動")

        if log_enable == "true":
            
            log_faile_name = "log\\" + reconnect.replace(' ',space_or_Underbar) + "[eventlog].json"
            event_start["status"]["beatmap"]["songCover"] = ""
            event_json = {"start":event_start,"end":event_end,}
            tf = open(log_faile_name, "w")
            json.dump(event_json,tf,indent=4)
            tf.close()

            result_faile_name = "log\\" + reconnect.replace(' ',space_or_Underbar) + "[result].json"
            result["rec_file"] = str(rec_file)
            result["new_faile_name"] = str(new_faile_name)
            tf = open(result_faile_name, "w")
            json.dump(result,tf,indent=4)
            tf.close()         
