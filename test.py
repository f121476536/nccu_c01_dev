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

@dataclass
class DirController:
    #定義該程式所需要用到的檔案及路徑
    current_dir: str = '\\'.join(os.path.abspath(__file__).split('\\')[:-1])
    c01_config_file: str = current_dir + '\\' + 'c01_config.xml'

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

class C01RobotConfig:
    def __init__(self) -> None:
        self.robot_config_map = XMLParser().create_config_map()
        
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
  
    def get_url_body(event):
        api_time = str(datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ'))
        api_request_id = 'REQ' + str(datetime.datetime.today().strftime('%Y%m%d%H%M'))
        body = {**{"time": api_time, "requestId": api_request_id}, **event}
        body = {'paraString': json.dumps(body, sort_keys=True, indent=1)}
        return body

    def send_post(url, header, data):
        r = requests.post(url, headers = header, data = data, verify=False)
        return r.status_code, r.json()
    
class C01RobotFunctionality:
    def __init__(self) -> None:  
        self.config = C01RobotConfig()
        self.web_handler = WebTransferHandler()
        
    #感應NFC卡片，讀取卡片中儲存的卡片內碼
    def read_nfc_card(self) -> str:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action":"start","deviceId":"NFC"}
        url_body = self.web_handler.get_url_body(event)
        status_code, result_text = self.web_handler.send_post(url, url_header, url_body)
        
        if(status_code == 200):
            result_text = json.loads(result_text)
            api_execute_result  = result_text['results'][0]['result']
            api_execute_content = result_text['results'][0]['content']
            if(api_execute_result == '0'):
                card_internal_code = api_execute_content
                return card_internal_code
            else:
                print('API returns fail response: "' + api_execute_content + '"')
        else: 
            print('Sending post request fail, error code:' + str(status_code))    

    #查詢卡片內碼代表的Alma帳號
    def search_alma_account(self, card_internal_code: str) -> str:
        url = self.config.get_alma_api(card_internal_code)
        r = requests.get(url)
        result_text = json.loads(r.text)
        account = [info['primary_id'] for info in result_text['user']][0]
        return account        
            
    #操控機器人語音發聲
    def speak_text(self, c01_api_url, text) -> None:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "SPEAKER", "content": text}
        url_body = self.web_handler.get_url_body(event)
        status_code, result_text  = self.web_handler.send_post(url, url_header, url_body)
    
    #取得目前機器人的⾃⾛點位
    def get_waypoints_list(self) -> List[str]:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "WAYPOINTLIST", "content": 'detail'}  
        url_body = self.web_handler.get_url_body(event)
        status_code, result_text  = self.web_handler.send_post(url, url_header, url_body)
        
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
        status_code, result_text = self.web_handler.send_post(url, url_header, url_body)
    
    #操控機器人返回充電站
    def back_to_dock(self) -> None:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "BACKTODOCK"}  
        url_body = self.web_handler.get_url_body(event)
        status_code, result_text = self.web_handler.send_post(url, url_header, url_body)

    #操控機器人手部動作
    def change_arm_movement(self, mode) -> None:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "ROBOTARMCONTROL", "content": f'arm/{str(mode)}'}  
        url_body = self.web_handler.get_url_body(event)
        status_code, result_text = self.web_handler.send_post(url, url_header, url_body)   
    
    #操控機器人脖子動作
    def change_neck_movement(self, direction, rotation):
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "ROBOTNECKMOVE", "content": f'{direction}/{rotation}'} 
        url_body = self.web_handler.get_url_body(event)
        status_code, result_text = self.web_handler.send_post(url, url_header, url_body)
               
    #操控機器人表情
    def change_face(self, emotion):
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "EMOTION", "content": emotion} 
        url_body = self.web_handler.get_url_body(event)
        status_code, result_text = self.web_handler.send_post(url, url_header, url_body)
   
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

class C01RobotLocalFileBuilder:
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
        content = f'function {function_name}()' +  '{' + '\n'
        content += '  let result = {};' + '\n'
        content += '  return result' + '\n' + '}'
        
        with open(file_dir, "w",encoding="utf-8") as f:
            f.write(content)

    #如果已經存在，將其刪除
    def delete_existing_file(self, file: str) -> None:
        if os.path.exists(file):
            os.remove(file)
            
    #驗證檔案有無過期(超過一天)
    def validate_file_date(self, file: str) -> bool:
        file_date = time.ctime(os.path.getmtime(file))
        file_date = datetime.datetime.strptime(file_date, "%a %b %d %H:%M:%S %Y").date()
        now_date = datetime.datetime.now().date()
        return True if now_date > file_date else False
    
def main() -> None:
    f = r'D:\hanwen\git-repos\nccu_c01_dev\lib\api-result\新文字文件.txt'
    c01 = C01RobotLocalFileBuilder()
    print(c01.initialize_file(f))
    
if __name__ == "__main__":
    main()