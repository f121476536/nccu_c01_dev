import requests
import json
import time
import datetime
import os
import xml.etree.ElementTree as ET
import cv2
import math
import numpy
from PIL import Image, ImageDraw, ImageFont
import base64

from requests.api import post

# 從XML設定檔案中，讀取對內本地目錄以及對外API參數


class XMLConfig():
    def __init__(self):

        # to_local
        self.c01_api_ip = ''
        self.c01_api_port = ''
        self.c01_camera_save_pic = ''
        self.c01_camera_save_done_pic = ''
        self.c01_lib_file_dir = ''
        self.run_chrome_file_dir = ''
        self.run_chrome_prs_page = ''
        self.run_chrome_para_usr = ''
        self.run_chrome_start_page = ''
        self.usr_lib_account_cache_dir = ''
        self.usr_lib_account_cache = ''
        self.usrinfo_js_file_dir = ''
        self.prsresult_js_file_dir = ''
        self.emotion_result_js_file_dir = ''
        self.usr_pic_file_dir = ''

        # to_server
        self.alma_api_protocol = ''
        self.alma_api_address = ''
        self.alma_api_name = ''
        self.alma_api_version = ''
        self.alma_api_key = ''
        self.alma_api_response_format = ''
        self.get_PRS_list_address = ''
        self.get_PRS_list_port = ''
        self.get_PRS_list_routing = ''
        self.get_user_emotion_pic_address = ''
        self.get_user_emotion_pic_port = ''
        self.get_user_emotion_pic_routing = ''

    # 透過卡片內碼(_code)，組成Alma查詢讀者API，進而查找讀者身分
    def get_alma_searching_user_API(self, _code):
        return '{}://{}/{}/{}/users?limit=50&q=identifiers~{}&apikey={}&format={}'.format(self.alma_api_protocol, self.alma_api_address, self.alma_api_name, self.alma_api_version, _code, self.alma_api_key, self.alma_api_response_format)

    def get_PRS_list_API(self, _suffix):
        return '{}:{}{}'.format(self.get_PRS_list_address, self.get_PRS_list_port, self.get_PRS_list_routing + _suffix)

    def get_user_emotion_pic_API(self):
        return '{}:{}{}'.format(self.get_user_emotion_pic_address, self.get_user_emotion_pic_port, self.get_user_emotion_pic_routing)

    def get_run_chrome_cmd(self):
        return '"{}" --app={} --user-data-dir={} --start-fullscreen'.format(self.run_chrome_file_dir, self.run_chrome_prs_page, self.run_chrome_para_usr)

    # ALMA讀者帳號快取
    def load_usr_cache(self):
        if(not os.path.exists(self.usr_lib_account_cache_dir)):
            with open(self.usr_lib_account_cache_dir, 'a', encoding="utf-8") as f:
                f.write('{}')

        # 讀取過去登入過的帳號資訊
        with open(self.usr_lib_account_cache_dir, 'r', encoding="utf-8") as f:
            line = f.readline()
        print(line)
        self.usr_lib_account_cache = json.loads(line)

    # 儲存此次新增的ALMA讀者帳號
    def add_usr_cache(self, _code, _account):
        self.usr_lib_account_cache[_code] = _account
        with open(self.usr_lib_account_cache_dir, 'w', encoding="utf-8") as f:
            f.writelines(str(self.usr_lib_account_cache).replace("'", '"'))


def ParserXMLConfig(_xmldir):
    # 從檔案載入並解析 XML 資料
    tree = ET.parse(_xmldir)
    root = tree.getroot()
    xml = XMLConfig()
    xml.c01_api_ip = root.find('to_local/c01_api/ip').text
    xml.c01_api_port = root.find('to_local/c01_api/port').text
    xml.c01_lib_file_dir = root.find('to_local/c01_lib/file_dir').text + '\\'
    xml.c01_camera_save_pic = xml.c01_lib_file_dir + \
        root.find('to_local/c01_camera/save_pic').text
    xml.c01_camera_save_done_pic = xml.c01_lib_file_dir + \
        root.find('to_local/c01_camera/save_done_pic').text
    xml.run_chrome_file_dir = root.find('to_local/run_chrome/file_dir').text
    xml.run_chrome_prs_page = root.find('to_local/run_chrome/prs_page').text
    xml.run_chrome_para_usr = xml.c01_lib_file_dir + \
        root.find('to_local/run_chrome/para_usr').text
    xml.run_chrome_start_page = root.find(
        'to_local/run_chrome/start_page').text
    xml.usr_lib_account_cache_dir = xml.c01_lib_file_dir + \
        root.find('to_local/lib_account/file_dir').text
    xml.usrinfo_js_file_dir = xml.c01_lib_file_dir + \
        root.find('to_local/usrinfo_js/file_dir').text
    xml.prsresult_js_file_dir = xml.c01_lib_file_dir + \
        root.find('to_local/prsresult_js/file_dir').text
    xml.emotion_result_js_file_dir = xml.c01_lib_file_dir + \
        root.find('to_local/emotion_result_js/file_dir').text
    xml.usr_pic_file_dir = xml.c01_lib_file_dir + \
        root.find('to_local/usr_pic/file_dir').text
    xml.alma_api_protocol = root.find('to_server/alma_api/protocol').text
    xml.alma_api_address = root.find('to_server/alma_api/address').text
    xml.alma_api_name = root.find('to_server/alma_api/name').text
    xml.alma_api_version = root.find('to_server/alma_api/version').text
    xml.alma_api_key = root.find('to_server/alma_api/key').text
    xml.alma_api_response_format = root.find(
        'to_server/alma_api/response_format').text
    xml.get_PRS_list_address = root.find('to_server/get_PRS_list/address').text
    xml.get_PRS_list_port = root.find('to_server/get_PRS_list/port').text
    xml.get_PRS_list_routing = root.find('to_server/get_PRS_list/routing').text
    xml.get_user_emotion_pic_address = root.find(
        'to_server/get_user_emotion_pic/address').text
    xml.get_user_emotion_pic_port = root.find('to_server/get_user_emotion_pic/port').text
    xml.get_user_emotion_pic_routing = root.find('to_server/get_user_emotion_pic/routing').text
    return xml


def TransferToAlmaAccount(_alma_user_url):
    # 如果沒有內碼，就直接回傳Error
    UserAccount = 'Found Error'
    # 透過使用者的卡片內碼，組成查詢user的Alma api url
    # print(_alma_user_url)
    r = requests.get(_alma_user_url)

    # 解析Alma API回傳的讀者資訊
    TotalInfo = json.loads(r.text)
    ReaderArr = []
    for Info in TotalInfo['user']:
        DicExsist = Info.get('last_name', False)
        if(not DicExsist):
            Name = Info['first_name']
        else:
            Name = Info['last_name']
        ReaderArr.append(Info['primary_id'])
    UserAccount = ReaderArr[0]

    return UserAccount

# 設置c01的web server
# option, 0 = Device, 1 = Reboot, 2 = Shutdown


def SetURL(_ip, _port, _option):
    option = "ErrorMsg: plz enter correct option number!"
    if(_option == 0):
        option = 'Device'
    elif(_option == 1):
        option = 'Reboot'
    elif(_option == 2):
        option = 'Shutdown'
    else:
        return option
    return 'http://{}:{}/GeosatRobot/api/{}'.format(_ip, _port, option)

# 設定post的header


def SetURLHeader():
    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'}
    return headers

# 設定post的body


def SetURLBody(_eventDic):
    APITime = str(datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ'))
    APIRequestId = 'REQ' + \
        str(datetime.datetime.today().strftime('%Y%m%d%H%M'))
    Str = MergeTwoDicts(
        {"time": APITime, "requestId": APIRequestId}, _eventDic)
    paraString = json.dumps(Str, sort_keys=True, indent=1)
    data = {'paraString': paraString}
    return data

# 合併兩個字典


def MergeTwoDicts(_dic1, _dic2):
    for d in _dic2:
        _dic1[d] = _dic2[d]
    return _dic1


# 實際作發送post的動作
def SendPostToURL(_url, _header, _data):
    r = requests.post(_url, headers=_header, data=_data, verify=False)
    return r.status_code, r.json()

def ReadNFCCard():
    dic = {"action":"start","deviceId":"NFC"}
    return dic

def ParseAPIResult(_post_sc, _post_text):
    if(_post_sc == 200):
        APIResult = json.loads(_post_text)
        api_sc = APIResult['results'][0]['result']
        api_text = APIResult['results'][0]['content']
        if(api_sc == '0'):
            return api_text
        else:
            print('API returns fail response: "' + api_text + '"')
    else: 
        print('Sending post request fail, error code:' + str(_post_sc))

def CallResfulAPI(_url):
    # 先組成API Server的URL
    r = requests.get(_url)
    return r.text.replace('\n','').replace('  ','').replace(' ','')

def UpdateToJS(_file, _emotion): 
    # 讀取舊的檔案內容，並更新emotion的值
    content = ''
    with open(_file, 'r', encoding="utf-8") as f:
        line = f.readlines()
        for l in line:
            try:
                # str.index如果找不到目標字串，就會直接報錯
                keyword = "let result = "
                p = l.index(keyword)
                content += l[:p] + keyword + _emotion + ';\n'
            except Exception as e:
                content += l
                continue

    # 將新內容儲存至檔案當中
    with open(_file, "w",encoding="utf-8") as f:
        f.write(content)

def ShowTextOnCamera(img, text, left, top, textColor, textSize):
    if (isinstance(img, numpy.ndarray)):  #判斷是否OpenCV圖片類型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    
    fontFace = "Font/simsun.ttc"
    fontText = ImageFont.truetype(
        fontFace, textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)


def GetXYPosition(_centerX, _centerY, _radius, _angle):
    degree = -math.radians(_angle)
    x = (int) (_centerX + _radius * math.cos(degree))
    y = (int) (_centerY + _radius * math.sin(degree))
    return x, y
    
def SetSilhouette(_frame, _height, _width):
    
    # 文字
    color_rgb = (255, 255, 0)
    text = '請依照指示位置並點擊螢幕進行拍攝'
    _frame = ShowTextOnCamera(_frame, text, 50, 30, color_rgb, 32)

    # 畫人形
    radius = 100
    color_rgb = (0, 176, 80)
    center_point = (int(_width/2), int(_height/2))
    # 圓圈，圓心座標, 半徑, 顏色, 線條寬度
    cv2.circle(_frame, center_point, radius, color_rgb, 3)
    
    # 線條
    neck_length = 63
    line_left_start_point = GetXYPosition(center_point[0], center_point[1], radius, 240)
    line_left_end_point = (line_left_start_point[0], line_left_start_point[1]+neck_length)
    cv2.line(_frame, line_left_start_point, line_left_end_point, color_rgb, 5)

    line_right_start_point = GetXYPosition(center_point[0], center_point[1], radius, 300)
    line_right_end_point = (line_right_start_point[0], line_right_start_point[1]+neck_length)    
    cv2.line(_frame, line_right_start_point, line_right_end_point, color_rgb, 5)

    # 圓圈
    center_point = (center_point[0], center_point[1]+500)
    radius += 250
    cv2.circle(_frame, center_point, radius, color_rgb, 3)
    
    return _frame

def EncodePicToBase64(_img_path, _usr_acc):
    with open(_img_path, 'rb') as f:
        image_data = f.read()
        return {'usr_acc': _usr_acc, 'base64_data': str(base64.b64encode(image_data),'utf-8')}
            
def FlashOnCamera(_frame):
    cv2.rectangle(_frame, (10,10), (20,20), (0,255,0), 2)
    return _frame

def ClickOnMouseAction(event, x, y, flags, param):  
    if event == cv2.EVENT_LBUTTONDOWN: 
        # 回傳目前使用者拍的照片的full dir
        pic_dir = param.c01_camera_save_dir
        pic_name = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S%f'))
        global current_usr_pic
        current_usr_pic = pic_dir + '\\' + pic_name + '.png'
        cv2.imwrite(current_usr_pic, frame)

        # 關閉拍攝程式
        global program_life
        program_life = False
    

def ClearFolder(_dir):    
    # 在拍照之前，先清除資料夾內過去的照片
    dirlist = os.listdir(_dir)
    for f in dirlist:
        # print(f)
        os.remove(_dir + '\\' + f)

class C01Camera():
    def __init__(self, c01_camera_save_dir, c01_camera_frame):
        self.c01_camera_save_dir = c01_camera_save_dir
        self.c01_camera_frame = c01_camera_frame

def DecodeBase64ToPic(_pic_file, _base64_data):
    with open(_pic_file, 'wb') as file:
        jiema = base64.b64decode(_base64_data)  # 解碼
        file.write(jiema) 

#取得目前機器人的即時點位
def get_robot_current_position(_c01_api_url, _header):
    event = {"action": "start", "deviceId": "CURRENTPOSE"}
    post_sc, post_text = SendPostToURL(_c01_api_url, _header, SetURLBody(event))
    api_return_info = post_text['results'][0]
    c01_api_correct_check = api_return_info['result']
    if(c01_api_correct_check==0):
        pos_info = json.loads(api_return_info['content'])
        print('CurrentPose = ', pos_info['CurrentPose'])
        print('RobotPose = ', pos_info['RobotPose'])
    else:
        print(api_return_info['content'])

#操控機器人語音發聲
def control_robot_speak_text(_c01_api_url, _header, _text):
    event = {"action": "start", "deviceId": "SPEAKER", "content": _text}
    post_sc, post_text = SendPostToURL(_c01_api_url, _header, SetURLBody(event))

#取得目前機器人的⾃⾛點位
def get_robot_waypoints_list(_c01_api_url, _header):
    waypoints_list = []
    event = {"action": "start", "deviceId": "WAYPOINTLIST", "content": 'detail'}  
    post_sc, post_text = SendPostToURL(_c01_api_url, _header, SetURLBody(event))
    api_return_info = post_text['results'][0]
    c01_api_correct_check = str(api_return_info['result'])
    if(c01_api_correct_check == str(0)):
        pos_info = json.loads(api_return_info['content'])
        waypoints_list = pos_info['Waypoints']
    else:
        print(api_return_info['content'])
    return waypoints_list

#操控機器人前往某一個點位
def control_robot_go_to_waypoint(_c01_api_url, _header, _waypoint):
    event = {"action": "start", "deviceId": "NAVIGATION", "content": _waypoint}  
    post_sc, post_text = SendPostToURL(_c01_api_url, _header, SetURLBody(event))
    api_return_info = post_text['results'][0]
    print(api_return_info)

#操控機器人返回充電站
def control_robot_back_to_dock(_c01_api_url, _header):
    event = {"action": "start", "deviceId": "BACKTODOCK"}  
    post_sc, post_text = SendPostToURL(_c01_api_url, _header, SetURLBody(event))
    api_return_info = post_text['results'][0]
    print(api_return_info)
    
#操控機器人手部動作  
def control_robot_arm_movement(_c01_api_url, _header, _mode):
    content = 'arm/{}'.format(str(_mode))
    event = {"action": "start", "deviceId": "ROBOTARMCONTROL", "content": content}  
    post_sc, post_text = SendPostToURL(_c01_api_url, _header, SetURLBody(event))
    #api_return_info = post_text['results'][0]
    #print(api_return_info)


#操控機器人脖子動作
def control_robot_neck_movement(_c01_api_url, _header, _direction, _rotation):
    content = "{}/{}".format(_direction, _rotation)
    event = {"action": "start", "deviceId": "ROBOTNECKMOVE", "content": content}  
    post_sc, post_text = SendPostToURL(_c01_api_url, _header, SetURLBody(event))  
    print(post_sc)
    print(post_text)

#操控機器人表情
def control_robot_face_emotion(_c01_api_url, _header, _emotion):
    event = {"action": "start", "deviceId": "EMOTION", "content": _emotion}  
    post_sc, post_text = SendPostToURL(_c01_api_url, _header, SetURLBody(event))  
    print(post_sc)
    print(post_text)

#操控機器人自己旋轉

#開啟機器人麥克風(收音)
def control_robot_start_micphone(_c01_api_url, _header):
    event = {"action": "start", "deviceId": "AUDIO"}  
    post_sc, post_text = SendPostToURL(_c01_api_url, _header, SetURLBody(event))
    api_return_info = post_text['results'][0]
    print(api_return_info)  

#關閉機器人麥克風(收音)
def control_robot_stop_micphone(_c01_api_url, _header):
    event = {"action": "stop", "deviceId": "AUDIO"}  
    post_sc, post_text = SendPostToURL(_c01_api_url, _header, SetURLBody(event))
    api_return_info = post_text['results'][0]
    print(api_return_info) 
    
#取得目前機器人的電量資訊
def get_robot_battery(_c01_api_url, _header):
    event = {"action": "start", "deviceId": "BATTERY"}  
    post_sc, post_text = SendPostToURL(_c01_api_url, _header, SetURLBody(event))
    api_return_info = post_text['results'][0]
    print(api_return_info)

##取得目前機器人整體狀態資訊
def get_robot_status(_c01_api_url, _header):
    event = {"action": "start", "deviceId": "STATUS"}  
    post_sc, post_text = SendPostToURL(_c01_api_url, _header, SetURLBody(event))
    api_return_info = post_text['results'][0]
    print(api_return_info)  

         
# main
start_time = time.time()
print('Reading xmlconfig for c01...')

# 一開始Call C01的設定檔
main_dir = (os.path.dirname(os.path.realpath(__file__))) + '/'
XMLconfig = ParserXMLConfig(main_dir + 'c01_config.xml')
print('Setting c01 api header...')
# option, 0 = Device, 1 = Reboot, 2 = Shutdown
c01_api_url = SetURL(XMLconfig.c01_api_ip, XMLconfig.c01_api_port, 0)
header = SetURLHeader()


'''
# 讀卡片
print('Reading card and mapping reader info...')
event = ReadNFCCard()
body = SetURLBody(event)
post_sc, post_text = SendPostToURL(c01_api_url, header, body)
code = ParseAPIResult(post_sc, post_text)
print(code)

if(code == '15153F67'):
    usr_account = 'temp'
else:  
    # AEF8BD54
    usr_account = TransferToAlmaAccount(XMLconfig.get_alma_searching_user_API(code))
'''

'''
code = '15153F67'
usr_account = 'temp'
# 讀取圖書館帳號快取
XMLconfig.load_usr_cache()
usr_lib_dic = XMLconfig.usr_lib_account_cache
if(usr_lib_dic.get(code)==None):
    # usr_account = TransferToAlmaAccount(XMLconfig.get_alma_searching_user_API(code))
    XMLconfig.add_usr_cache(code, usr_account)
else:
    usr_account = usr_lib_dic.get(code)
'''

'''
# 把讀者帳號跟讀者登入的時間點紀錄下來
print('Recording user info to usrinfo.js...')

login_time = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
userinfo = json.dumps({'user_account':usr_account, 'login_time':login_time})
UpdateToJS(XMLconfig.usrinfo_js_file_dir, userinfo)

# 取得該讀者的推薦清單(API), 將結果JSON儲存至本機
print('Recording PRS list to prsresult.js...')
json_txt = CallResfulAPI(XMLconfig.get_PRS_list_API(usr_account))
# 儲存
UpdateToJS(XMLconfig.prsresult_js_file_dir, json_txt)

# 拍使用者的樣貌
print('Taking user picture...')
# 如果有上一次的使用者圖片，將其刪除
current_usr_pic = ''
ClearFolder(XMLconfig.usr_pic_file_dir)
# 載入設定檔案，取得路徑位置
window_name = 'webcam capture'
# 先抓鏡頭裝置序號為0的鏡頭
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# 先抓一幀，取得鏡頭長寬
ret, frame = cap.read()
height, width, pixels = frame.shape
# 先命名視窗，接著新增該視窗的事件監測
cv2.namedWindow(window_name)
# 由於cv2的事件只能設定callback跟一個參數，因此將儲存路徑跟當下畫面包成物件傳入
c01_camera = C01Camera(XMLconfig.usr_pic_file_dir, frame)
cv2.setMouseCallback(window_name, ClickOnMouseAction, c01_camera)
# 全域變數，開啟拍攝程式
program_life = True
while(program_life):

    # 刷新畫面
    ret, frame = cap.read()
    # 設置使用者提示文字於鏡頭畫面上    
    text_frame = SetSilhouette(frame, height, width)
    # 將抓到的影像顯示在視窗上面
    cv2.imshow(window_name, text_frame)
    # 按下ECS可以離開畫面
    k = cv2.waitKey(1)
    if k==27:
        break
# flash_frame = FlashOnCamera(frame)
# cv2.imshow(window_name, flash_frame)
# time.sleep(2)
cap.release()
cv2.destroyAllWindows()
# print(current_usr_pic)
'''
# usr_acc = '123591'
# current_usr_pic = main_dir + 'usr_test.png'
# #print(EncodePicToBase64(current_usr_pic))

# #上傳使用者照片, 更新本機檔案
# print('Uploading user image...')
# post_status_code, post_text = SendPostToURL(XMLconfig.get_user_emotion_pic_API(), SetURLHeader(), EncodePicToBase64(current_usr_pic, usr_acc))
# print(post_status_code)
# print(post_text)
# post_text = json.loads(post_text)

# if(post_status_code!=200):
#     print('Upload user picture fail.')
# else:
#     DecodeBase64ToPic(XMLconfig.c01_camera_save_done_pic + '\\usr_done.jpg', post_text['pic_done_file'])

# #將情緒分析API回傳的結果儲存至JS file，讓前端可以讀取結果
# usr_emotion = str({"emotion":post_text['emotion'], "img_dir":XMLconfig.c01_camera_save_done_pic + '\\usr_done.jpg'})
# UpdateToJS(XMLconfig.emotion_result_js_file_dir, usr_emotion)


# #自動打開瀏覽器(全螢幕) 顯示書單、情緒分析結果
# print('PRS page opening...')
# os.system(XMLconfig.get_run_chrome_cmd())
# print(XMLconfig.get_run_chrome_cmd())



#取得位置功能
#get_robot_current_position(c01_api_url, header)

#發話功能
text = '緊急通知，圖書館雲端自動化系統索引功能異常，已緊急處理中'
control_robot_speak_text(c01_api_url, header, text)

#取得自走點
#waypoints = get_robot_waypoints_list(c01_api_url, header)
#print(waypoints)
# control_robot_go_to_waypoint(c01_api_url, header, 'NAV1')

#返回充電站
#control_robot_back_to_dock(c01_api_url, header)

#動作跟doc上面的對不起來，需要日後自己編碼
#1 no /2 ok /3 here /4 look for /5 not sure /6 Go Straight /7 Happy /8 drumming /9 hi_1 /10 hi_2 /11 not sure to help /12 Please Wait /13 Go and Trun /14 bye_1 /15 bye_2
#control_robot_arm_movement(c01_api_url, header, 1)

#取得電池
#get_robot_battery(c01_api_url, header)

#取得整體狀態
#get_robot_status(c01_api_url, header)

#沒有用?
#速度值，範圍區間爲 -20 ~ 20 正負號表⽰低頭、抬頭，數值 0 表⽰停⽌
#速度值，範圍區間爲 -20 ~ 20 正負號表⽰逆時鐘、順時鐘⽅向旋轉，數值0 表⽰停⽌
#direction = 5
#rotation = 5
#control_robot_neck_movement(c01_api_url, header, direction, rotation)

#沒有用?
#control_robot_face_emotion(c01_api_url, header, "HAPPY")

#測試錄音功能
# control_robot_start_micphone(c01_api_url, header)
# time.sleep(5)
# control_robot_stop_micphone(c01_api_url, header)

print("\n--- {} seconds ---".format(round(time.time() - start_time,2)))
