from linecache import cache
import requests
import json
import time
import datetime
import os
#import cv2
import math
#import numpy
#from PIL import Image, ImageDraw, ImageFont
import base64
from requests.api import post
import xml.etree.ElementTree as ET
from dataclasses import Field, dataclass, field
from enum import Enum, auto
from abc import abstractmethod, ABCMeta
from typing import List, Dict
from enum import Enum, auto
import time
import sys

@dataclass
class DirController:
    #定義該程式所需要用到的檔案及路徑
    current_dir: str = '/'.join(os.path.abspath(__file__).split('\\')[:-1])
    c01_config_file: str = current_dir + '/' + 'c01_config.xml'

class EventListener:
    def __init__(self) -> None:
        pass
    
    def exit_app(self, error_message: str) -> None:
        sys.exit(error_message)

class XMLParser:
    def __init__(self) -> None:
        self.root: ET = None
    
    #建立confing，讀取三層架構
    def create_config_map(self) -> Dict[str, str]:
        self.load_xml_file()
        config_map = {}
        for endpoint in self.root:
            for tag in endpoint:
                for sub_tag in tag:
                    xml_directory = '_'.join([endpoint.tag, tag.tag, sub_tag.tag])
                    config_map[xml_directory] = sub_tag.text
        return config_map
    
    #從指定xml檔案中讀取內容                              
    def load_xml_file(self) -> None:
        self.root = ET.parse(DirController().c01_config_file).getroot()

class RobotConfig:
    def __init__(self) -> None:
        self.robot_config_map = XMLParser().create_config_map()
        self.current_dir = DirController().current_dir
        
    def get_local_lib_dir(self) -> str:
        local_lib_dir = self.robot_config_map['to_local_c01_lib_lib_dir']
        return f'{self.current_dir}/{local_lib_dir}'       

    def get_static_dir(self) -> str:
        get_static_dir = self.robot_config_map['to_local_c01_lib_static_dir']
        return f'{self.current_dir}/{get_static_dir}' 

    def get_account_cache_dir(self) -> str:
        lib_dir = self.get_local_lib_dir()
        file_name = self.robot_config_map['to_local_account_cache_file_name']
        return f'{lib_dir}/{file_name}' 
               
    #取得機器人和ROS內部通訊用的API
    def get_ros_api(self) -> str:
        protocol = self.robot_config_map['to_ros_robot_api_protocol']
        ip = self.robot_config_map['to_ros_robot_api_ip']
        port = self.robot_config_map['to_ros_robot_api_port']
        route = self.robot_config_map['to_ros_robot_api_route']
        option1 = self.robot_config_map['to_ros_robot_api_option1']
        return f'{protocol}://{ip}:{port}/{route}/{option1}'
    
    #取得ALMA查找User的API
    def get_alma_api(self, card_internal_code: str ) -> str:
        protocol = self.robot_config_map['to_server_alma_api_protocol']
        address = self.robot_config_map['to_server_alma_api_address']
        name = self.robot_config_map['to_server_alma_api_name']
        version = self.robot_config_map['to_server_alma_api_version']
        key = self.robot_config_map['to_server_alma_api_key']
        response_format = self.robot_config_map['to_server_alma_api_response_format']
        return f'{protocol}://{address}/{name}/{version}/users?limit=50&q=identifiers~{card_internal_code}&apikey={key}&format={response_format}'
    
    #取得PRS查找推薦清單的API
    def get_prs_api(self, user_account: str) -> str:
        address = self.robot_config_map['to_server_get_PRS_list_address']
        port = self.robot_config_map['to_server_get_PRS_list_port']
        version = self.robot_config_map['to_server_get_PRS_list_version']
        routing = self.robot_config_map['to_server_get_PRS_list_routing']
        return f'{address}:{port}/{version}/{routing}/{user_account}'

    #取得讀者情緒辨識的API
    def get_face_emtion_api(self) -> str:
        address = self.robot_config_map['to_server_get_user_emotion_pic_address']
        port = self.robot_config_map['to_server_get_user_emotion_pic_port']
        version = self.robot_config_map['to_server_get_user_emotion_pic_version']
        routing = self.robot_config_map['to_server_get_user_emotion_pic_routing']
        return f'{address}:{port}/{version}/{routing}'

class WebTransferHandler:
    def get_url_header(self):
        header = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'}
        return header
  
    def get_url_body(self, event):
        api_time = str(datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ'))
        api_request_id = 'REQ' + str(datetime.datetime.today().strftime('%Y%m%d%H%M'))
        body = {**{"time": api_time, "requestId": api_request_id}, **event}
        body = {'paraString': json.dumps(body, sort_keys=True, indent=1)}
        return body

    def send_post(self, url, header, data):
        r = requests.post(url, headers = header, data = data, verify=False)
        if(r.status_code == 200):
            return r.json()
        else:
            EventListener().exit_app('Post sending error has occurred.')
class RobotFunctionality:
    def __init__(self) -> None:  
        self.config = RobotConfig()
        self.web_handler = WebTransferHandler()
        
    #感應NFC卡片，讀取卡片中儲存的卡片內碼
    def read_nfc_card(self) -> str:
        url = self.config.get_ros_api()
        print(f'url = {url}')
        url_header = self.web_handler.get_url_header()
        event = {"action":"start","deviceId":"NFC"}
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)
        result_text = json.loads(result_text)
        api_execute_result  = result_text['results'][0]['result']
        
        if(api_execute_result != '0'):
            EventListener().exit_app('Loading card error has occurred.')
        
        card_internal_code = result_text['results'][0]['content']
        return card_internal_code

    #查詢卡片內碼代表的Alma帳號
    def search_alma_account(self, card_internal_code: str) -> str:
        url = self.config.get_alma_api(card_internal_code)
        r = requests.get(url)
        result_text = json.loads(r.text)
        alma_account = [info['primary_id'] for info in result_text['user']][0]
        return alma_account        
            
    #操控機器人語音發聲
    def speak_text(self, c01_api_url, text) -> None:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "SPEAKER", "content": text}
        url_body = self.web_handler.get_url_body(event)
        result_text  = self.web_handler.send_post(url, url_header, url_body)
    
    #取得目前機器人的⾃⾛點位
    def get_waypoints_list(self) -> List[str]:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "WAYPOINTLIST", "content": 'detail'}  
        url_body = self.web_handler.get_url_body(event)
        result_text  = self.web_handler.send_post(url, url_header, url_body)
        
        waypoints_list = []
        api_return_info = result_text['results'][0]
        c01_api_correct_check = str(api_return_info['result'])
        if(c01_api_correct_check == str(0)):
            pos_info = json.loads(api_return_info['content'])
            waypoints_list = pos_info['Waypoints']
        else:
            print(api_return_info['content'])
        return waypoints_list

    #操控機器人前往某一個點位
    def go_to_waypoint(self, waypoint) -> None:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "NAVIGATION", "content": waypoint}
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)
    
    #操控機器人返回充電站
    def back_to_dock(self) -> None:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "BACKTODOCK"}  
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)

    #操控機器人手部動作
    def change_arm_movement(self, mode) -> None:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "ROBOTARMCONTROL", "content": f'arm/{str(mode)}'}  
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)   
    
    #操控機器人脖子動作
    def change_neck_movement(self, direction, rotation):
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "ROBOTNECKMOVE", "content": f'{direction}/{rotation}'} 
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)
               
    #操控機器人表情
    def change_face(self, emotion):
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "EMOTION", "content": emotion} 
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)
   
@dataclass
class RobotFace:
    ANGRY: str = 'Angry'
    CHARGING: str = 'Charging'
    DOUBT: str = 'Doubt'
    EXCITED: str = 'Excited'
    HAPPY: str = 'Happy'
    LOVE: str = 'Love'
    NORMAL: str = 'Normal'
    SAD: str = 'Sad'
    SLEEPY: str = 'Sleepy'

@dataclass
class RobotArm:
    NO : int = 1
    OK : int = 2
    HERE : int = 3
    LOOKFOR : int = 4
    NOTSURE : int = 5
    GOSTRAIGHT : int = 6
    HAPPY : int = 7
    DRUMMING : int = 8
    HI_1 : int = 9
    HI_2 : int = 10
    NOTSURETOHELP : int = 11
    PLEASEWAIT : int = 12
    GOANDTRUN : int = 13
    BYE_1 : int = 14
    BYE_2 : int = 15

class LocalFileBuilder:
    def __init__(self) -> None:
        # self.robot_config_map = XMLParser().create_config_map()        
        # function_name = self.robot_config_map['to_local_usrinfo_js_function_name']
        # file_dir = self.robot_config_map['to_local_usrinfo_js_file_dir']
        None
     
    #將新的檔案內容，儲存至JS靜態檔案
    def save_js_static_file(self, content: Dict[str, str], file_dir: str) -> None:
        content = ''
        with open(file_dir, 'r', encoding = "utf-8") as f:
            line = f.readlines()
            for l in line:
                try:
                    keyword = "let result = "
                    p = l.index(keyword)
                    content += l[:p] + keyword + content + ';\n'
                except Exception as e:
                    content += l
                    continue
                
        with open(file_dir, "w", encoding="utf-8") as f:
            f.write(content)
    
    #初始化JS靜態檔案
    def initialize_js_static_file(self, function_name: str, file_dir: str) -> None:      
        self.delete_existing_file(file_dir)
        content = f'function {function_name}()' +  '{' + '\n'
        content += '  let result = {};' + '\n'
        content += '  return result' + '\n' + '}'
        
        with open(file_dir, "w",encoding = "utf-8") as f:
            f.write(content)

    #如果已經存在，將其刪除
    def delete_existing_file(self, file: str) -> None:
        if os.path.exists(file):
            os.remove(file)
    
    #如果不存在，將其創建        
    def create_file_if_existing(self, file: str, content: str) -> None:
        if not os.path.exists(file):
            with open(file, "a",encoding = "utf-8") as f:
                f.write(content)
    
    #讀取快取資訊
    def load_account_cache(self, file: str) -> Dict[str, str]:
        with open(file, 'r', encoding="utf-8") as f:
            line = f.readline()
        account_cache = json.loads(line)
        return account_cache
        
    def add_account_to_cache(self, file: str, code: str, account: str) -> None:
        account_cache = self.load_account_cache(file)
        account_cache[code] = account
        content = str(account_cache).replace("'", '"')
        with open(file, 'w', encoding = "utf-8") as f:
            f.writelines(content)
            
    #驗證檔案有無過期(超過一天)
    def validate_file_date(self, file: str) -> bool:
        file_date = time.ctime(os.path.getmtime(file))
        file_date = datetime.datetime.strptime(file_date, "%a %b %d %H:%M:%S %Y").date()
        now_date = datetime.datetime.now().date()
        return True if now_date > file_date else False
    
class RobotService:
    def __init__(self) -> None:
        self.robot_function = RobotFunctionality()
        self.file_builder = LocalFileBuilder()
        self.config = RobotConfig()
    
    #識別讀者    
    def identify_reader(self) -> str:
        card_internal_code = self.robot_function.read_nfc_card()
        
        #快取機制
        cache_file = self.config.get_account_cache_dir()
        self.file_builder.create_file_if_existing(cache_file, '{}')
        validate = self.file_builder.validate_file_date(cache_file)
        if(validate):
            account_cache = self.file_builder.load_account_cache(cache_file)
            alma_account = account_cache.get(card_internal_code)
            
            if(alma_account == None):
                alma_account = self.robot_function.search_alma_account(card_internal_code)
        else:
            self.file_builder.delete_existing_file(cache_file)
            self.file_builder.create_file_if_existing(cache_file, '{}')
            alma_account = self.robot_function.search_alma_account(card_internal_code)
        self.file_builder.add_account_to_cache(cache_file, card_internal_code, alma_account)
        
        return alma_account

    #紀錄讀者帳號跟讀者登入時間
    def record_user_login_info(self, alma_account: str) -> None:
        login_time = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
        content = json.dumps({'user_account': alma_account, 'login_time': login_time})
        
        static_dir = self.config.get_static_dir()
        file_name = self.config.robot_config_map['to_local_usrinfo_js_file_name']
        file_dir = f'{static_dir}/{file_name}'
        
        function_name = self.config.robot_config_map['to_local_usrinfo_js_function_name']
        self.file_builder.initialize_js_static_file(function_name, file_dir)
        self.file_builder.save_js_static_file(content, file_dir)
    
    def take_user_photo(self) -> None:
        #刪除上次的照片
        lib_dir = self.config.get_local_lib_dir()
        pic_dir = self.config.robot_config_map['to_local_usr_pic_pic_dir']
        file_list = [file for file in os.listdir(f'{lib_dir}/{pic_dir}')]
        if(len(file_list) != 0):
            self.file_builder.delete_existing_file(f'{lib_dir}/{pic_dir}/{file_list[0]}')

class RobotCamara:
    def __init__(self) -> None:
        pass
    
    def initializer(self) -> None:
        window_name = 'webcam capture'
        #cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
    
def main() -> None:
    # robot_service = RobotService()
    # #alma_account = robot_service.identify_reader()
    # #robot_service.record_user_login_info(alma_account)
    # robot_service.take_user_photo()
    
    #RobotFunctionality().change_face(RobotFace.ANGRY)
    RobotFunctionality().change_arm_movement(RobotArm.HI_1)
    print('done')
    
if __name__ == "__main__":
    main()