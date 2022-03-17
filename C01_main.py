from linecache import cache
from prompt_toolkit import application
import requests
import json
import time
import datetime
import os
import logging
import math
import base64
from requests.api import post
import xml.etree.ElementTree as ET
from dataclasses import Field, dataclass, field
from enum import Enum, auto
from abc import abstractmethod, ABCMeta
from typing import List, Dict
from enum import Enum, auto
import time
import traceback
import sys
import cv2
import numpy
from PIL import Image, ImageDraw, ImageFont
import shutil

class DirController:
    def __init__(self):
        self.current_os: str = sys.platform
        self.separation: str = self.get_separation()
        self.current_dir: str = '/'.join(os.path.abspath(__file__).split(self.separation)[:-1])
        self.config_file: str = self.current_dir + '/' + 'C01_config.xml'
        self.log_file: str = self.current_dir + '/log/error.log'
    
    def get_separation(self):
        return '\\' if self.current_os == 'win32' else '/'

class EventListener:
    def __init__(self) -> None:
        pass

    def exit_app(self, error_message: str) -> None:
        sys.exit(error_message)


class XMLParser:
    def __init__(self) -> None:
        self.root: ET = None

    # 建立confing，讀取三層架構
    def create_config_map(self) -> Dict[str, str]:
        self.load_xml_file()
        config_map = {}
        for endpoint in self.root:
            for tag in endpoint:
                for sub_tag in tag:
                    xml_directory = '_'.join(
                        [endpoint.tag, tag.tag, sub_tag.tag])
                    config_map[xml_directory] = sub_tag.text
        return config_map

    # 從指定xml檔案中讀取內容
    def load_xml_file(self) -> None:
        self.root = ET.parse(DirController().config_file).getroot()


class RobotConfig:
    def __init__(self) -> None:
        self.robot_config_map = XMLParser().create_config_map()
        self.current_dir = DirController().current_dir

    def get_local_lib_dir(self) -> str:
        local_lib_dir = self.robot_config_map['to_local_c01_lib_lib_dir']
        return f'{self.current_dir}/{local_lib_dir}'

    def get_static_dir(self) -> str:
        local_lib_dir = self.get_local_lib_dir()
        static_dir = self.robot_config_map['to_local_c01_lib_static_dir']
        return f'{local_lib_dir}/{static_dir}'

    def get_account_cache_dir(self) -> str:
        lib_dir = self.get_local_lib_dir()
        file_name = self.robot_config_map['to_local_account_cache_file_name']
        return f'{lib_dir}/{file_name}'

    # 取得機器人和ROS內部通訊用的API
    def get_ros_api(self) -> str:
        protocol = self.robot_config_map['to_ros_robot_api_protocol']
        ip = self.robot_config_map['to_ros_robot_api_ip']
        port = self.robot_config_map['to_ros_robot_api_port']
        route = self.robot_config_map['to_ros_robot_api_route']
        option1 = self.robot_config_map['to_ros_robot_api_option1']
        return f'{protocol}://{ip}:{port}/{route}/{option1}'

    # 取得ALMA查找User的API
    def get_alma_api(self, card_internal_code: str) -> str:
        protocol = self.robot_config_map['to_server_alma_api_protocol']
        address = self.robot_config_map['to_server_alma_api_address']
        name = self.robot_config_map['to_server_alma_api_name']
        version = self.robot_config_map['to_server_alma_api_version']
        key = self.robot_config_map['to_server_alma_api_key']
        response_format = self.robot_config_map['to_server_alma_api_response_format']
        return f'{protocol}://{address}/{name}/{version}/users?limit=50&q=identifiers~{card_internal_code}&apikey={key}&format={response_format}'

    # 取得PRS查找推薦清單的API
    def get_prs_api(self, user_account: str) -> str:
        address = self.robot_config_map['to_server_get_PRS_list_address']
        port = self.robot_config_map['to_server_get_PRS_list_port']
        version = self.robot_config_map['to_server_get_PRS_list_version']
        routing = self.robot_config_map['to_server_get_PRS_list_routing']
        return f'{address}:{port}/{version}/{routing}/{user_account}'

    # 取得讀者情緒辨識的API
    def get_face_emtion_api(self) -> str:
        address = self.robot_config_map['to_server_emotion_api_address']
        port = self.robot_config_map['to_server_emotion_api_port']
        version = self.robot_config_map['to_server_emotion_api_version']
        routing = self.robot_config_map['to_server_emotion_api_routing']
        return f'{address}:{port}/{version}/{routing}'

    # 取得問答系統的API
    def get_question_answer_api(self) -> str:
        address = self.robot_config_map['to_server_qa_api_address']
        port = self.robot_config_map['to_server_qa_api_port']
        version = self.robot_config_map['to_server_qa_api_version']
        routing = self.robot_config_map['to_server_qa_api_routing']
        return f'{address}:{port}/{version}/{routing}'

    # 取得語音檔儲存的來源目錄位置
    def get_audio_text_from_dir(self) -> str:
        from_dir = self.robot_config_map['to_local_audio_text_from_dir']
        return from_dir

    # 取得語音檔儲存的目的目錄位置
    def get_audio_text_to_dir(self) -> str:
        lib_dir = self.get_local_lib_dir()
        to_dir = self.robot_config_map['to_local_audio_text_to_dir']
        return f'{lib_dir}\{to_dir}'


class WebTransferHandler:
    # 取得連線Header設置
    def get_url_header(self) -> Dict[str, str]:
        header = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'}
        return header

    # 取得機器人Body格式設置
    def get_url_body(self, event: Dict[str, str]) -> Dict[str, str]:
        api_time = str(datetime.datetime.today().strftime(
            '%Y-%m-%dT%H:%M:%SZ'))
        api_request_id = 'REQ' + \
            str(datetime.datetime.today().strftime('%Y%m%d%H%M'))
        body = {**{"time": api_time, "requestId": api_request_id}, **event}
        body = {'paraString': json.dumps(body, sort_keys=True, indent=1)}
        return body

    # 發出Post請求
    def send_post(self, url: str, header: Dict[str, str], data: Dict[str, str]):
        r = requests.post(url, headers=header, data=data, verify=False)
        if(r.status_code == 200):
            return r.json()
        else:
            EventListener().exit_app('Post sending error has occurred.')


class RobotCamara:
    def __init__(self) -> None:
        self.config: RobotConfig = RobotConfig()
        self.life: bool = True
        self.height: int = 0
        self.width: int = 0
        self.frame: numpy.ndarray = None
        self.window_name: str = 'webcam window'
        self.camera_save_dir: str = self.get_camera_save_dir()
        self.font_face: str = "Font/simsun.ttc"
        self.guide_text: str = '請依照指示位置並點擊螢幕進行拍攝'

    # 取得儲存使用者照片目錄
    def get_camera_save_dir(self) -> str:
        lib_dir = self.config.get_local_lib_dir()
        pic_dir = self.config.robot_config_map['to_local_c01_camera_save_dir']
        camera_save_dir = f'{lib_dir}/{pic_dir}'
        return camera_save_dir

    # 開啟拍攝鏡頭
    def activate_shooting_window(self) -> None:
        len = self.select_equipment()
        cv2.namedWindow(self.window_name)
        self.height, self.width = self.get_frame_height_and_width(len)
        cv2.setMouseCallback(self.window_name, self.click_action_event, None)

        while(self.life):
            ret, self.frame = len.read()
            self.set_silhouette()
            cv2.imshow(self.window_name, self.frame)
            # 按下ECS可以離開畫面
            k = cv2.waitKey(1)
            if k == 27:
                break
        len.release()
        cv2.destroyAllWindows()

    # 拍攝裝置選擇
    def select_equipment(self) -> cv2.VideoCapture:
        len = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        return len

    # 取得畫面框的長寬
    def get_frame_height_and_width(self, len: cv2.VideoCapture) -> int:
        ret, frame = len.read()
        height, width, pixels = frame.shape
        return height, width

    # 掛載滑鼠點擊事件
    def click_action_event(self, event, x, y, flags, param) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            pic_name = str(
                datetime.datetime.today().strftime('%Y%m%d%H%M%S%f'))
            cv2.imwrite(self.camera_save_dir + '/' +
                        pic_name + '.png', self.frame)
            self.life = False

    # 顯示拍攝時的說明文字、人形引導
    def set_silhouette(self) -> None:
        # 文字說明
        YELLOW = (255, 255, 0)
        left = 50
        top = 30
        text_size = 32
        self.show_text_on_frame(self.guide_text, left, top, YELLOW, text_size)

        # 畫人形
        center_point = (int(self.width / 2), int(self.height / 2))
        radius = 100
        GREEN = (0, 176, 80)
        thickness = 3
        cv2.circle(self.frame, center_point, radius, GREEN, thickness)

        # 線條
        neck_length = 63
        line_left_start_point = self.get_x_y_position(
            center_point[0], center_point[1], radius, 240)
        line_left_end_point = (
            line_left_start_point[0], line_left_start_point[1] + neck_length)
        thickness = 5
        cv2.line(self.frame, line_left_start_point,
                 line_left_end_point, GREEN, thickness)
        line_right_start_point = self.get_x_y_position(
            center_point[0], center_point[1], radius, 300)
        line_right_end_point = (
            line_right_start_point[0], line_right_start_point[1] + neck_length)
        cv2.line(self.frame, line_right_start_point,
                 line_right_end_point, GREEN, thickness)

        # 圓圈
        center_point = (center_point[0], center_point[1] + 500)
        radius += 250
        thickness = 3
        cv2.circle(self.frame, center_point, radius, GREEN, thickness)

    # 顯示說明文字於拍攝畫面
    def show_text_on_frame(self, text, left, top, text_color, text_size) -> None:
        # 判斷是否OpenCV圖片類型
        if (isinstance(self.frame, numpy.ndarray)):
            self.frame = Image.fromarray(
                cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))

        draw = ImageDraw.Draw(self.frame)
        font_text = ImageFont.truetype(
            self.font_face, text_size, encoding="utf-8")
        draw.text((left, top), text, text_color, font=font_text)
        self.frame = cv2.cvtColor(numpy.asarray(self.frame), cv2.COLOR_RGB2BGR)

    # 取得x,y座標
    def get_x_y_position(self, centerX, centerY, radius, angle) -> int:
        degree = -math.radians(angle)
        x = (int)(centerX + radius * math.cos(degree))
        y = (int)(centerY + radius * math.sin(degree))
        return x, y


class RobotFunctions:
    def __init__(self) -> None:
        self.config = RobotConfig()
        self.web_handler = WebTransferHandler()
        self.camara = RobotCamara()
        self.file_builder = LocalFileBuilder()

    # 感應NFC卡片，讀取卡片中儲存的卡片內碼
    def read_nfc_card(self) -> str:
        url = self.config.get_ros_api()
        print(f'url = {url}')
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "NFC"}
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)
        result_text = json.loads(result_text)
        api_execute_result = result_text['results'][0]['result']

        if(api_execute_result != '0'):
            EventListener().exit_app('Loading card error has occurred.')

        card_internal_code = result_text['results'][0]['content']
        return card_internal_code

    # 查詢卡片內碼代表的Alma帳號
    def search_alma_account(self, card_internal_code: str) -> str:
        url = self.config.get_alma_api(card_internal_code)
        r = requests.get(url)
        result_text = json.loads(r.text)
        alma_account = [info['primary_id'] for info in result_text['user']][0]
        return alma_account

    # 操控機器人語音發聲
    def speak_text(self, text: str) -> None:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "SPEAKER", "content": text}
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)

    # 取得目前機器人的⾃⾛點位
    def get_waypoints_list(self) -> List[str]:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start",
                 "deviceId": "WAYPOINTLIST", "content": 'detail'}
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)

        waypoints_list = []
        api_return_info = result_text['results'][0]
        c01_api_correct_check = str(api_return_info['result'])
        if(c01_api_correct_check == str(0)):
            pos_info = json.loads(api_return_info['content'])
            waypoints_list = pos_info['Waypoints']
        else:
            print(api_return_info['content'])
        return waypoints_list

    # 操控機器人前往某一個點位
    def go_to_waypoint(self, waypoint: str) -> None:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start",
                 "deviceId": "NAVIGATION", "content": waypoint}
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)

    # 操控機器人返回充電站
    def back_to_dock(self) -> None:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "BACKTODOCK"}
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)

    # 操控機器人手部動作
    def change_arm_movement(self, mode: int) -> None:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "ROBOTARMCONTROL",
                 "content": f'arm/{str(mode)}'}
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)

    # 操控機器人脖子動作
    def change_neck_movement(self, direction: int, rotation: int):
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "ROBOTNECKMOVE",
                 "content": f'{direction}/{rotation}'}
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)

    # 操控機器人表情
    def change_face(self, emotion: str):
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "EMOTION", "content": emotion}
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)

    # 情緒識別
    def recognize_emotion(self, account: str) -> Dict[str, str]:
        # 取得情緒辨識的API
        url = self.config.get_face_emtion_api()
        url_header = self.web_handler.get_url_header()

        # 取得辨識前圖片檔案
        lib_dir = self.config.get_local_lib_dir()
        save_dir = self.config.robot_config_map['to_local_c01_camera_save_dir']
        full_save_dir = f'{lib_dir}/{save_dir}'
        file_name = [file for file in os.listdir(full_save_dir)][0]

        # 將辨識前圖片檔案編碼後，打API做辨識
        pic_base64 = self.file_builder.encode_pic_to_base64(
            f'{full_save_dir}/{file_name}', account)
        result_text = self.web_handler.send_post(url, url_header, pic_base64)

        # 回傳結果的base64，將其轉回識別後圖片並儲存
        save_done_pic = self.config.robot_config_map['to_local_c01_camera_save_done_dir']
        done_file = f'{lib_dir}/{save_done_pic}/{file_name}'
        self.file_builder.decode_base64_to_pic(
            done_file, result_text['usr_face_recogni_pic'])
        result_text['usr_face_recogni_pic'] = done_file
        return result_text

    def call_qa_system(self, question: str) -> List[str]:
        # 取得問答系統的API
        url = self.config.get_question_answer_api()
        url_header = self.web_handler.get_url_header()
        question = {'question': question}
        result_text = self.web_handler.send_post(url, url_header, question)
        return result_text['answer']

    # 開啟麥克風
    def activate_micphone(self):
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "start", "deviceId": "AUDIO"}
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)
        print(f'result_text = {result_text}')

    # 關閉麥克風，並取得檔案路徑
    def deactivate_micphone(self) -> str:
        url = self.config.get_ros_api()
        url_header = self.web_handler.get_url_header()
        event = {"action": "stop", "deviceId": "AUDIO"}
        url_body = self.web_handler.get_url_body(event)
        result_text = self.web_handler.send_post(url, url_header, url_body)
        record_file = result_text['results'][0]['content']
        return record_file

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
    NO: int = 1
    OK: int = 2
    HERE: int = 3
    LOOKFOR: int = 4
    NOTSURE: int = 5
    GOSTRAIGHT: int = 6
    HAPPY: int = 7
    DRUMMING: int = 8
    HI_1: int = 9
    HI_2: int = 10
    NOTSURETOHELP: int = 11
    PLEASEWAIT: int = 12
    GOANDTRUN: int = 13
    BYE_1: int = 14
    BYE_2: int = 15


class LocalFileBuilder:
    def __init__(self) -> None:
        # self.robot_config_map = XMLParser().create_config_map()
        # function_name = self.robot_config_map['to_local_usrinfo_js_function_name']
        # file_dir = self.robot_config_map['to_local_usrinfo_js_file_dir']
        None

    # 將新的檔案內容，儲存至JS靜態檔案
    def save_js_static_file(self, writing_content: Dict[str, str], file_dir: str) -> None:
        keyword = "let result = "
        file_content = ''
        with open(file_dir, 'r', encoding="utf-8") as f:
            line = f.readlines()
            for l in line:
                try:
                    p = l.index(keyword)
                    file_content += l[:p] + keyword + \
                        str(writing_content) + ';\n'
                except Exception as e:
                    file_content += l
                    continue

        with open(file_dir, "w", encoding="utf-8") as f:
            f.write(file_content)

    # 初始化JS靜態檔案
    def initialize_js_static_file(self, function_name: str, file_dir: str) -> None:
        self.delete_existing_file(file_dir)
        content = f'function {function_name}()' + '{' + '\n'
        content += '  let result = {};' + '\n'
        content += '  return result' + '\n' + '}'

        with open(file_dir, "w", encoding="utf-8") as f:
            f.write(content)

    # 如果已經存在，將其刪除
    def delete_existing_file(self, file: str) -> None:
        if os.path.exists(file):
            os.remove(file)

    # 如果不存在，將其創建
    def create_file_if_existing(self, file: str, content: str) -> None:
        if not os.path.exists(file):
            with open(file, "a", encoding="utf-8") as f:
                f.write(content)

    # 讀取快取資訊
    def load_file_to_json(self, file: str) -> Dict[str, str]:
        with open(file, 'r', encoding="utf-8") as f:
            line = f.readline()
        account_cache = json.loads(line)
        return account_cache

    def add_account_to_cache(self, file: str, code: str, account: str) -> None:
        account_cache = self.load_file_to_json(file)
        account_cache[code] = account
        content = str(account_cache).replace("'", '"')
        with open(file, 'w', encoding="utf-8") as f:
            f.writelines(content)

    # 驗證檔案有無過期(超過一天)
    def validate_file_date(self, file: str) -> bool:
        file_date = time.ctime(os.path.getmtime(file))
        file_date = datetime.datetime.strptime(
            file_date, "%a %b %d %H:%M:%S %Y").date()
        now_date = datetime.datetime.now().date()
        return True if now_date > file_date else False

    # 圖片編碼成base64
    def encode_pic_to_base64(self, img_path, usr_acc):
        with open(img_path, 'rb') as f:
            image_data = f.read()
            return {'usr_acc': usr_acc, 'base64_data': str(base64.b64encode(image_data), 'utf-8')}

    # base64解碼成圖片
    def decode_base64_to_pic(self, img_path, base64_data):
        with open(img_path, 'wb') as file:
            jiema = base64.b64decode(base64_data)
            file.write(jiema)

    # 移動檔案到指定位置
    def move_file(self, from_dir: str, to_dir: str, file_name: str) -> None:
        source = f'{from_dir}\{file_name}'
        destination = f'{to_dir}\{file_name}'
        shutil.move(source, destination)


class RobotService:
    def __init__(self) -> None:
        self.robot_functions = RobotFunctions()
        self.file_builder = LocalFileBuilder()
        self.config = RobotConfig()
        self.text_processer = TextProcesser()

    # 識別讀者
    def identify_reader(self) -> str:
        card_internal_code = self.robot_functions.read_nfc_card()

        # 快取機制
        cache_file = self.config.get_account_cache_dir()
        self.file_builder.create_file_if_existing(cache_file, '{}')
        validate = self.file_builder.validate_file_date(cache_file)
        if(validate):
            account_cache = self.file_builder.load_file_to_json(cache_file)
            alma_account = account_cache.get(card_internal_code)

            if(alma_account == None):
                alma_account = self.robot_functions.search_alma_account(
                    card_internal_code)
        else:
            self.file_builder.delete_existing_file(cache_file)
            self.file_builder.create_file_if_existing(cache_file, '{}')
            alma_account = self.robot_functions.search_alma_account(
                card_internal_code)
        self.file_builder.add_account_to_cache(
            cache_file, card_internal_code, alma_account)

        return alma_account

    # 紀錄讀者帳號跟讀者登入時間
    def record_user_login_info(self, alma_account: str) -> None:
        login_time = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
        content = {'user_account': alma_account, 'login_time': login_time}

        # 儲存成JS靜態檔案
        static_dir = self.config.get_static_dir()
        file_name = self.config.robot_config_map['to_local_usrinfo_js_file_name']
        file_dir = f'{static_dir}/{file_name}'
        function_name = self.config.robot_config_map['to_local_usrinfo_js_function_name']
        self.file_builder.initialize_js_static_file(function_name, file_dir)
        self.file_builder.save_js_static_file(content, file_dir)

    # 進行讀者表情拍攝
    def take_user_photo(self, account: str) -> None:
        # 刪除上次的照片檔案
        lib_dir = self.config.get_local_lib_dir()
        pic_dir = self.config.robot_config_map['to_local_c01_camera_save_dir']
        file_list = [file for file in os.listdir(f'{lib_dir}/{pic_dir}')]
        if(len(file_list) != 0):
            self.file_builder.delete_existing_file(
                f'{lib_dir}/{pic_dir}/{file_list[0]}')
        self.robot_functions.camara.activate_shooting_window()

        # 將情緒辨識後的內容進行重組
        api_result = self.robot_functions.recognize_emotion(account)
        content = {}
        content['emotion'] = api_result['emotion_tag']
        content['img_dir'] = api_result['usr_face_recogni_pic']

        # 儲存成JS靜態檔案
        static_dir = self.config.get_static_dir()
        file_name = self.config.robot_config_map['to_local_emotion_result_js_file_name']
        file_dir = f'{static_dir}/{file_name}'
        function_name = self.config.robot_config_map['to_local_usrinfo_js_function_name']
        self.file_builder.initialize_js_static_file(function_name, file_dir)
        self.file_builder.save_js_static_file(content, file_dir)

    # 顯示視覺化介面
    def show_user_interface(self) -> None:
        current_dir = DirController().current_dir
        file_dir = self.config.robot_config_map['to_local_run_chrome_file_dir']
        prs_file = self.config.robot_config_map['to_local_run_chrome_prs_file']
        prs_dir = f'{current_dir}/{prs_file}'
        para_dir_name = self.config.robot_config_map['to_local_run_chrome_para_dir_name']
        lib_dir = self.config.get_local_lib_dir()
        para_dir = f'{lib_dir}/{para_dir_name}'
        cmd = f'"{file_dir}" --app={prs_dir} --user-data-dir={para_dir} --start-fullscreen'
        print(f'cmd = {cmd}')
        os.system(cmd)

    # 進行QA問答
    def C01_qa_ask_question(self) -> None:
        # 將語音辨識後的文字檔案移動至指定目錄
        from_dir = self.config.get_audio_text_from_dir()
        to_dir = self.config.get_audio_text_to_dir()
        audio_file = 'audio_text.txt'

        exist_flag = False
        while(not exist_flag):
            time.sleep(1)
            exist_flag = os.path.exists(f'{from_dir}/{audio_file}')
        self.file_builder.move_file(from_dir, to_dir, audio_file)

        # 讀取語音辨識後的文字內容
        with open(f'{to_dir}/{audio_file}', 'r', encoding="utf-8-sig") as f:
            question = f.readline()

        # 呼叫問答系統的API，取得該問題的答案
        answer = self.robot_functions.call_qa_system(question)
        word = "<br>".join(answer)

        # 若有超連結，將其組成<a></a>格式
        word = self.text_processer.add_a_tag_to_string(word)

        # 儲存成JS靜態檔案
        content = {'word': word}
        static_dir = self.config.get_static_dir()
        file_name = self.config.robot_config_map['to_local_audio_anwser_js_file_name']
        file_dir = f'{static_dir}/{file_name}'
        function_name = self.config.robot_config_map['to_local_audio_anwser_js_function_name']
        self.file_builder.initialize_js_static_file(function_name, file_dir)
        self.file_builder.save_js_static_file(content, file_dir)
        
        # 機器人反應
        time.sleep(5)
        # answer = answer[len(answer)-1]
        # self.robot_functions.speak_text(answer)
        # self.robot_functions.change_face(RobotFace.EXCITED)
        # self.robot_functions.change_arm_movement(RobotArm.LOOKFOR)
        
    # 進行卡片讀取
    def C01_promotion_tap_in_card(self):
        alma_account = self.identify_reader()
        self.record_user_login_info(alma_account)
        
class TextProcesser():
    def find_char_position_in_string(self, string: str, char: str) -> List[int]:
        position = []
        n = 0
        while(n != -1):
            n = string.find(char, n + 1)
            if(n != -1):
                position.append(n)
        return position

    def add_a_tag_to_string(self, string: str):
        start_tag = '<a>'
        end_tag = '</a>'
        start_tag_position = self.find_char_position_in_string(
            string, start_tag)
        end_tag_position = self.find_char_position_in_string(string, end_tag)
        tag_num = len(start_tag_position)
        replace_ele = {}
        if(tag_num != len(end_tag_position)):
            raise ValueError("<a>與</a>的數量不一致!")
        else:
            for i in range(0, tag_num):
                sub_string = string[start_tag_position[i] +
                                    len(start_tag):end_tag_position[i] - 1]
                sub_string_list = sub_string.split('(')
                link_word = sub_string_list[0]
                link_url = sub_string_list[1]
                replace_ele[f'{start_tag + sub_string}' + ')' +
                            f'{end_tag}'] = f'<a href="{link_url}">{link_word}</a>'

        for key in replace_ele:
            value = replace_ele[key]
            string = string.replace(key, value)
        return string

class TimeHandler():
    def __init__(self) -> None:
        pass

    def get_now(self) -> str:
        return str(datetime.date.today())
    
    # 比較兩個日期早晚
    def compare_two_date(self, date1: str, date2: str) -> bool:
        formatted_date1 = time.strptime(date1, "%Y-%m-%d")
        formatted_date2 = time.strptime(date2, "%Y-%m-%d")
        return True if formatted_date1 > formatted_date2 else False

    def get_time(self) -> float:
        return time.time()

class SystemMonitor():
    def __init__(self) -> None:
        self.time_handler = TimeHandler()  
        self.dirs = DirController()
    
    def get_message_of_excu_time(self, start_time: float) -> str:
        message = f"executing {round(self.time_handler.get_time() - start_time, 2)} seconds"
        return message
    
    def log_event(self, message: str) -> None:
        app_logger = logging.getLogger()
        file_handler = logging.FileHandler(filename = self.dirs.log_file , mode = 'a', encoding = "utf-8")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        app_logger.addHandler(file_handler)
        logging.error(message)
    
if __name__ == "__main__":
    try:
        file_builder = LocalFileBuilder()
        robot_services = RobotService()
        
        application = sys.argv[1]
        if(application == 'C01-qa-ask-question'):
            robot_services.C01_qa_ask_question()            
        elif(application == 'C01-promotion-tap-in-card'):
            robot_services.C01_promotion_tap_in_card()        
    except Exception as e:
        error_class = e.__class__.__name__
        detail = e.args[0]
        cl, exc, tb = sys.exc_info()
        last_call_stack = traceback.extract_tb(tb)[-1]
        file_name = last_call_stack[0]
        line_number = last_call_stack[1]
        function_name = last_call_stack[2]
        error_message = "File \"{}\", line {}, in {}: [{}] {}".format(file_name, line_number, function_name, error_class, detail)
        monitor = SystemMonitor()
        monitor.log_event(error_message)