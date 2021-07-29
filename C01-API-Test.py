import requests
import json
import time
import datetime
import os
import xml.etree.ElementTree as ET
from imgurpython import ImgurClient
import cv2
import math
import numpy
from PIL import Image, ImageDraw, ImageFont


#從XML設定檔案中，讀取對內本地目錄以及對外API參數
class XMLConfig():
    def __init__(self):

        #to_local
        self.c01_api_ip = ''
        self.c01_api_port = ''
        self.c01_camera_save_pic = ''
        self.c01_lib_file_dir = ''
        self.run_chrome_file_dir = ''
        self.run_chrome_prs_page = ''
        self.run_chrome_para_usr = ''
        self.run_chrome_start_page = ''
        self.usrinfo_js_file_dir = ''
        self.prsresult_js_file_dir = ''
        self.emotion_result_js_file_dir = ''
        self.usr_pic_file_dir = ''

        #to_server
        self.alma_api_protocol = ''
        self.alma_api_address = ''
        self.alma_api_name = ''
        self.alma_api_version = ''
        self.alma_api_key = ''
        self.alma_api_response_format = ''
        self.get_imgur_config_address = ''
        self.get_imgur_config_port = ''
        self.get_imgur_config_routing = ''
        self.get_PRS_list_address = ''    
        self.get_PRS_list_port = '' 
        self.get_PRS_list_routing = '' 
        self.get_user_emotion_pic_address = ''
        self.get_user_emotion_pic_port = ''
        self.get_user_emotion_pic_routing = ''

    #透過卡片內碼(_code)，組成Alma查詢讀者API，進而查找讀者身分
    def get_alma_searching_user_API(self, _code):
        return '{}://{}/{}/{}/users?limit=50&q=identifiers~{}&apikey={}&format={}'.format(self.alma_api_protocol, self.alma_api_address, self.alma_api_name, self.alma_api_version, _code, self.alma_api_key, self.alma_api_response_format)

    def get_imgur_config_API(self):
        return '{}:{}{}'.format(self.get_imgur_config_address, self.get_imgur_config_port, self.get_imgur_config_routing)

    def get_PRS_list_API(self, _suffix):
        return '{}:{}{}'.format(self.get_PRS_list_address, self.get_PRS_list_port, self.get_PRS_list_routing + _suffix)

    def get_user_emotion_pic_API(self, _suffix):
        return '{}:{}{}'.format(self.get_user_emotion_pic_address, self.get_user_emotion_pic_port, self.get_user_emotion_pic_routing + _suffix)

    def get_run_chrome_cmd(self):
        return '"{}" --app={} --user-data-dir={} --start-fullscreen'.format(self.run_chrome_file_dir, self.run_chrome_prs_page, self.run_chrome_para_usr)

def ParserXMLConfig(_xmldir):
    # 從檔案載入並解析 XML 資料
    tree = ET.parse(_xmldir)
    root = tree.getroot()
    xml = XMLConfig()
    xml.c01_api_ip = root.find('to_local/c01_api/ip').text
    xml.c01_api_port = root.find('to_local/c01_api/port').text
    xml.c01_camera_save_pic = root.find('to_local/c01_camera/save_pic').text
    xml.c01_lib_file_dir = root.find('to_local/c01_lib/file_dir').text + '\\'
    xml.run_chrome_file_dir = root.find('to_local/run_chrome/file_dir').text
    xml.run_chrome_prs_page = root.find('to_local/run_chrome/prs_page').text
    xml.run_chrome_para_usr = root.find('to_local/run_chrome/para_usr').text
    xml.run_chrome_start_page = root.find('to_local/run_chrome/start_page').text
    xml.usrinfo_js_file_dir = xml.c01_lib_file_dir + root.find('to_local/usrinfo_js/file_dir').text
    xml.prsresult_js_file_dir = xml.c01_lib_file_dir + root.find('to_local/prsresult_js/file_dir').text
    xml.emotion_result_js_file_dir = xml.c01_lib_file_dir + root.find('to_local/emotion_result_js/file_dir').text
    xml.usr_pic_file_dir = xml.c01_lib_file_dir + root.find('to_local/usr_pic/file_dir').text
    xml.alma_api_protocol = root.find('to_server/alma_api/protocol').text
    xml.alma_api_address = root.find('to_server/alma_api/address').text
    xml.alma_api_name = root.find('to_server/alma_api/name').text
    xml.alma_api_version = root.find('to_server/alma_api/version').text
    xml.alma_api_key = root.find('to_server/alma_api/key').text
    xml.alma_api_response_format = root.find('to_server/alma_api/response_format').text
    xml.get_imgur_config_address = root.find('to_server/get_imgur_config/address').text
    xml.get_imgur_config_port = root.find('to_server/get_imgur_config/port').text
    xml.get_imgur_config_routing = root.find('to_server/get_imgur_config/routing').text
    xml.get_PRS_list_address = root.find('to_server/get_PRS_list/address').text    
    xml.get_PRS_list_port = root.find('to_server/get_PRS_list/port').text 
    xml.get_PRS_list_routing = root.find('to_server/get_PRS_list/routing').text 
    xml.get_user_emotion_pic_address = root.find('to_server/get_user_emotion_pic/address').text
    xml.get_user_emotion_pic_port = root.find('to_server/get_user_emotion_pic/port').text
    xml.get_user_emotion_pic_routing = root.find('to_server/get_user_emotion_pic/routing').text    
    return xml

def TransferToAlmaAccount(_alma_user_url):
    #如果沒有內碼，就直接回傳Error
    UserAccount = 'Found Error'
    #透過使用者的卡片內碼，組成查詢user的Alma api url
    #print(_alma_user_url) 
    r = requests.get(_alma_user_url)

    #解析Alma API回傳的讀者資訊
    TotalInfo = json.loads(r.text)
    ReaderArr = []
    for Info in TotalInfo['user']:
        DicExsist = Info.get('last_name',False)
        if(not DicExsist):
            Name = Info['first_name']
        else:
            Name = Info['last_name']
        ReaderArr.append(Info['primary_id'])
    UserAccount = ReaderArr[0]

    return UserAccount

#設置c01的web server
#option, 0 = Device, 1 = Reboot, 2 = Shutdown
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

#設定post的header
def SetURLHeader():
    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'}
    return headers

#設定post的body
def SetURLBody(_eventDic):
    APITime = str(datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ'))
    APIRequestId = 'REQ' + str(datetime.datetime.today().strftime('%Y%m%d%H%M'))
    Str = MergeTwoDicts({"time" : APITime, "requestId" : APIRequestId}, _eventDic)
    paraString = json.dumps(Str, sort_keys=True, indent=1)
    data = {'paraString': paraString}
    
    return data

#合併兩個字典
def MergeTwoDicts(_dic1, _dic2):
    for d in _dic2:
        _dic1[d] = _dic2[d]
    return _dic1


#實際作發送post的動作
def SendPostToURL(_url, _header, _data):
    r = requests.post(_url, headers = _header, data = _data)    
    return r.status_code, r.text

#讓機器人發話
def SpeakToText(_text):
    dic = {"action":"start", "deviceId" : "SPEAKER" , "content" : _text}
    return dic
    
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

def upload(client_data, local_img_file, album): 
    #上傳圖片的名稱
    time = str(datetime.datetime.today().strftime('%Y%m%d%H%M'))
    name = 'co1_upload_name_' + time
    title = 'co1_upload_title_' + time
    
    config = {
        'album':  album,
        'name': name,
        'title': title,
        'description': f'test-{datetime.datetime.now()}'
    }
    image = client_data.upload_from_path(local_img_file, config=config, anon=False)
    return image

def UploadPicToImgur(_pic, _get_imgur_config_url):
    #呼叫NCCU Server取得Imgur設定參數
    r = requests.get(_get_imgur_config_url)
    ImgurPicConfig = json.loads(r.text)
    client = ImgurClient(ImgurPicConfig['client_id'], ImgurPicConfig['client_secret'], ImgurPicConfig['access_token'], ImgurPicConfig['refresh_token'])
    #上傳圖片至指定相簿，上傳成功後回傳其圖片ID
    image = upload(client, _pic, ImgurPicConfig['album'])
    return image['id']

def CallResfulAPI(_url):
    #先組成API Server的URL
    r = requests.get(_url)
    return r.text.replace('\n','').replace('  ','').replace(' ','')

def UpdateToJS(_file, _emotion): 
    #讀取舊的檔案內容，並更新emotion的值
    content = ''
    with open(_file, 'r', encoding="utf-8") as f:
        line = f.readlines()
        for l in line:
            try:
                #str.index如果找不到目標字串，就會直接報錯
                keyword = "let result = "
                p = l.index(keyword)
                content += l[:p] + keyword + _emotion + ';\n'
            except Exception as e:
                content += l
                continue

    #將新內容儲存至檔案當中
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
    
    #文字
    color_rgb = (255, 255, 0)
    text = '請依照指示位置並點擊螢幕進行拍攝'
    _frame = ShowTextOnCamera(_frame, text, 50, 30, color_rgb, 32)

    #畫人形
    radius = 100
    color_rgb = (0, 176, 80)
    center_point = (int(_width/2), int(_height/2))
    # 圓圈，圓心座標, 半徑, 顏色, 線條寬度
    cv2.circle(_frame, center_point, radius, color_rgb, 3)
    
    #線條
    neck_length = 63
    line_left_start_point = GetXYPosition(center_point[0], center_point[1], radius, 240)
    line_left_end_point = (line_left_start_point[0], line_left_start_point[1]+neck_length)
    cv2.line(_frame, line_left_start_point, line_left_end_point, color_rgb, 5)

    line_right_start_point = GetXYPosition(center_point[0], center_point[1], radius, 300)
    line_right_end_point = (line_right_start_point[0], line_right_start_point[1]+neck_length)    
    cv2.line(_frame, line_right_start_point, line_right_end_point, color_rgb, 5)

    #圓圈
    center_point = (center_point[0], center_point[1]+500)
    radius += 250
    cv2.circle(_frame, center_point, radius, color_rgb, 3)
    
    return _frame
    
def FlashOnCamera(_frame):
    cv2.rectangle(_frame, (10,10), (20,20), (0,255,0), 2)
    return _frame

def ClickOnMouseAction(event, x, y, flags, param):  
    if event == cv2.EVENT_LBUTTONDOWN: 
        #回傳目前使用者拍的照片的full dir
        pic_dir = param.c01_camera_save_dir
        pic_name = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S%f'))
        global current_usr_pic
        current_usr_pic = pic_dir + '\\' + pic_name + '.png'
        cv2.imwrite(current_usr_pic, frame)

        #關閉拍攝程式
        global program_life
        program_life = False
    

def ClearFolder(_dir):    
    #在拍照之前，先清除資料夾內過去的照片
    dirlist = os.listdir(_dir)
    for f in dirlist:
        #print(f)
        os.remove(_dir + '\\' + f)

class C01Camera():
    def __init__(self, c01_camera_save_dir, c01_camera_frame):
        self.c01_camera_save_dir = c01_camera_save_dir
        self.c01_camera_frame = c01_camera_frame

#main
start_time = time.time()
print('Reading xmlconfig for c01...')
xml_file_dir = r'C:\Users\admin\Desktop\c01\c01-prs\c01_config.xml'
XMLconfig = ParserXMLConfig(xml_file_dir)


#一開始Call C01的設定檔
print('Setting c01 api header...')
#option, 0 = Device, 1 = Reboot, 2 = Shutdown
c01_api_url = SetURL(XMLconfig.c01_api_ip, XMLconfig.c01_api_port, 0)
header = SetURLHeader()

'''
#讀卡片
print('Reading card and mapping reader info...')
event = ReadNFCCard()
body = SetURLBody(event)
post_sc, post_text = SendPostToURL(c01_api_url, header, body)
code = ParseAPIResult(post_sc, post_text)
print(code)

if(code == '15153F67'):
    usr_account = 'temp'
else:  
    #AEF8BD54
    usr_account = TransferToAlmaAccount(XMLconfig.get_alma_searching_user_API(code))

#把讀者帳號跟讀者登入的時間點紀錄下來
print('Recording user info to usrinfo.js...')

login_time = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
userinfo = json.dumps({'user_account':usr_account, 'login_time':login_time})
UpdateToJS(XMLconfig.usrinfo_js_file_dir, userinfo)

#取得該讀者的推薦清單(API), 將結果JSON儲存至本機
print('Recording PRS list to prsresult.js...')
json_txt = CallResfulAPI(XMLconfig.get_PRS_list_API(usr_account))
#儲存
UpdateToJS(XMLconfig.prsresult_js_file_dir, json_txt)

#拍使用者的樣貌
print('Taking user picture...')
#如果有上一次的使用者圖片，將其刪除
current_usr_pic = ''
ClearFolder(XMLconfig.usr_pic_file_dir)
#載入設定檔案，取得路徑位置
window_name = 'webcam capture'
#先抓鏡頭裝置序號為0的鏡頭
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#先抓一幀，取得鏡頭長寬
ret, frame = cap.read()
height, width, pixels = frame.shape
#先命名視窗，接著新增該視窗的事件監測
cv2.namedWindow(window_name)
#由於cv2的事件只能設定callback跟一個參數，因此將儲存路徑跟當下畫面包成物件傳入
c01_camera = C01Camera(XMLconfig.usr_pic_file_dir, frame)
cv2.setMouseCallback(window_name, ClickOnMouseAction, c01_camera)
#全域變數，開啟拍攝程式
program_life = True
while(program_life):

    #刷新畫面
    ret, frame = cap.read()
    #設置使用者提示文字於鏡頭畫面上    
    text_frame = SetSilhouette(frame, height, width)
    #將抓到的影像顯示在視窗上面
    cv2.imshow(window_name, text_frame)
    #按下ECS可以離開畫面
    k = cv2.waitKey(1)
    if k==27:
        break
# flash_frame = FlashOnCamera(frame)
# cv2.imshow(window_name, flash_frame)
# time.sleep(2)
cap.release()
cv2.destroyAllWindows()
#print(current_usr_pic)
'''

#上傳使用者照片, 更新本機檔案
current_usr_pic = r'C:\Users\admin\Desktop\c01\c01-prs\lib\usr-pic\20210714165227827826.png'
print('Uploading user image...')
img_id = UploadPicToImgur(current_usr_pic, XMLconfig.get_imgur_config_API())
usr_emotion = CallResfulAPI(XMLconfig.get_user_emotion_pic_API(img_id))

#將情緒分析API回傳的結果儲存至JS file，讓前端可以讀取結果
UpdateToJS(XMLconfig.emotion_result_js_file_dir, usr_emotion)

#自動打開瀏覽器(全螢幕) 顯示書單、情緒分析結果
print('PRS page opening...')
os.system(XMLconfig.get_run_chrome_cmd())
print(XMLconfig.get_run_chrome_cmd())
'''
#念書第一本書名
#event = SpeakToText('李商隱')
'''

print("\n--- {} seconds ---".format(round(time.time() - start_time,2)))