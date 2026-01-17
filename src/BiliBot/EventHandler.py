import requests
import re
from writelog import HandleLog
from openai import OpenAI
import os
from typing import Any
from ErrorHandler import ChatError
import tomllib
import time
import json


logger = HandleLog()

with open (os.getcwd() + "\\config.toml", "rb") as f:
    config = tomllib.load(f)


class EventHandler:
    def __init__(self):
        self.url = "https://www.bilibili.com/"
        self.headers = {
            "user-agent": config["user-agent"],
            "cookie": config["cookie"],
            "referer": "https://www.bilibili.com/",
            "origin": "https://message.bilibili.com"
        }
        self.client = OpenAI(api_key=config["deepseekAPI"], base_url="https://api.deepseek.com") # 初始化deepseek的api
        self.csrf = config["csrf"]
        self.timeout = (config["connectout"], config["receiveout"])
        self.uid = config["uid"]
    
    def getOid(self, bvid: str) -> str:
        """获取指定bvid视频的oid

        Args:
            bvid (str): bvid

        Returns:
            str: oid
        """
        response = requests.get(url=f"https://www.bilibili.com/video/{bvid}/?spm_id_from=333.1387.homepage.video_card.click&vd_source=bebcd016ed24b76ff6c1cc0f6096670a", headers=self.headers, timeout=self.timeout)
        assert response.status_code == 200
        response = response.text
        resu = re.search(r',"jump_url":"&oid=(\d+)"', response)
        if not resu: 
            logger.error("错误: 没有找到oid---getOid")
            raise ChatError("无oid")
        oid = resu.group(1)
        logger.debug(f"找到oid{oid}")
        return oid
    
    def uploadPic(self, file_path) -> dict[str, Any]:
        """上传图片

        Args:
            file_path (_type_): 文件目录

        Returns:
            dict[str, Any]: {"img_src": response["image_url"],"img_width": response["image_width"],"img_height": response["image_height"],"img_size": response["img_size"],"ai_gen_pic":0}
        """
        if not os.path.isfile(file_path):
            logger.error(f"{file_path}不存在")
            raise ChatError(f"{file_path}不存在")
        with open (file_path, "rb") as f:
            file_content = f.read()
            
        data = {
            "file_up": file_content,
            "biz": "new_dyn",
            "category": "daily",
            "csrf": self.csrf
        }
        response = requests.post(url="https://api.bilibili.com/x/dynamic/feed/draw/upload_bfs", headers=self.headers,data=data ,files={"file_up": file_content}, timeout=self.timeout)
        assert response.status_code == 200
        if response.json()["code"] != 0:
            logger.error(f"上传图片时发生错误,服务器端响应{response}")
            raise ChatError("")
        response = response.json()["data"]
        return {"img_src": response["image_url"],"img_width": response["image_width"],"img_height": response["image_height"],"img_size": response["img_size"],"ai_gen_pic":0}
        
    def sendComment(self, message: str, oid: str, pictures: list = [] ,root: str="None") -> None:
        """向指定视频的评论区回复一条评论

        Args:
            message (str): 评论内容
            oid (str): 视频的oid
            pictures (list): 携带图片(非必须)
            root (str): 回复目标(非必须)
        """
        url = "https://api.bilibili.com/x/v2/reply/add?dm_img_list=[%7B%22x%22:1338,%22y%22:-125,%22z%22:0,%22timestamp%22:12011,%22k%22:92,%22type%22:0%7D,%7B%22x%22:1615,%22y%22:364,%22z%22:101,%22timestamp%22:12112,%22k%22:108,%22type%22:0%7D,%7B%22x%22:1732,%22y%22:723,%22z%22:90,%22timestamp%22:12212,%22k%22:71,%22type%22:0%7D,%7B%22x%22:1645,%22y%22:637,%22z%22:0,%22timestamp%22:12317,%22k%22:89,%22type%22:0%7D,%7B%22x%22:1951,%22y%22:892,%22z%22:229,%22timestamp%22:12419,%22k%22:97,%22type%22:0%7D,%7B%22x%22:2154,%22y%22:1096,%22z%22:406,%22timestamp%22:12525,%22k%22:94,%22type%22:0%7D,%7B%22x%22:2006,%22y%22:895,%22z%22:256,%22timestamp%22:12626,%22k%22:67,%22type%22:0%7D,%7B%22x%22:2413,%22y%22:1280,%22z%22:683,%22timestamp%22:12727,%22k%22:85,%22type%22:0%7D,%7B%22x%22:1873,%22y%22:739,%22z%22:146,%22timestamp%22:12832,%22k%22:106,%22type%22:0%7D,%7B%22x%22:2552,%22y%22:1419,%22z%22:822,%22timestamp%22:12974,%22k%22:99,%22type%22:0%7D,%7B%22x%22:1927,%22y%22:941,%22z%22:147,%22timestamp%22:13074,%22k%22:69,%22type%22:0%7D,%7B%22x%22:2350,%22y%22:1418,%22z%22:546,%22timestamp%22:13174,%22k%22:84,%22type%22:0%7D,%7B%22x%22:2616,%22y%22:1684,%22z%22:812,%22timestamp%22:13504,%22k%22:77,%22type%22:0%7D,%7B%22x%22:1990,%22y%22:1058,%22z%22:186,%22timestamp%22:13608,%22k%22:64,%22type%22:0%7D,%7B%22x%22:1885,%22y%22:960,%22z%22:83,%22timestamp%22:13993,%22k%22:115,%22type%22:0%7D,%7B%22x%22:3141,%22y%22:2397,%22z%22:1371,%22timestamp%22:14093,%22k%22:68,%22type%22:0%7D,%7B%22x%22:3195,%22y%22:2635,%22z%22:1471,%22timestamp%22:14194,%22k%22:84,%22type%22:0%7D,%7B%22x%22:1943,%22y%22:1452,%22z%22:242,%22timestamp%22:14296,%22k%22:103,%22type%22:0%7D,%7B%22x%22:3564,%22y%22:3099,%22z%22:1877,%22timestamp%22:14400,%22k%22:94,%22type%22:0%7D,%7B%22x%22:2407,%22y%22:1941,%22z%22:723,%22timestamp%22:15257,%22k%22:67,%22type%22:0%7D,%7B%22x%22:3339,%22y%22:2749,%22z%22:1751,%22timestamp%22:15357,%22k%22:106,%22type%22:0%7D,%7B%22x%22:2236,%22y%22:1073,%22z%22:619,%22timestamp%22:15457,%22k%22:116,%22type%22:0%7D,%7B%22x%22:2219,%22y%22:120,%22z%22:512,%22timestamp%22:15558,%22k%22:74,%22type%22:0%7D,%7B%22x%22:3386,%22y%22:1290,%22z%22:1647,%22timestamp%22:16240,%22k%22:73,%22type%22:0%7D,%7B%22x%22:2990,%22y%22:1809,%22z%22:1312,%22timestamp%22:16341,%22k%22:92,%22type%22:0%7D,%7B%22x%22:2970,%22y%22:2039,%22z%22:1301,%22timestamp%22:16441,%22k%22:78,%22type%22:0%7D,%7B%22x%22:3805,%22y%22:3099,%22z%22:2128,%22timestamp%22:16542,%22k%22:83,%22type%22:0%7D,%7B%22x%22:2252,%22y%22:1619,%22z%22:586,%22timestamp%22:16643,%22k%22:103,%22type%22:0%7D,%7B%22x%22:4327,%22y%22:3750,%22z%22:2677,%22timestamp%22:16744,%22k%22:108,%22type%22:0%7D,%7B%22x%22:3786,%22y%22:3210,%22z%22:2133,%22timestamp%22:16858,%22k%22:88,%22type%22:0%7D,%7B%22x%22:1715,%22y%22:1151,%22z%22:26,%22timestamp%22:16959,%22k%22:110,%22type%22:0%7D,%7B%22x%22:2303,%22y%22:1741,%22z%22:608,%22timestamp%22:17060,%22k%22:96,%22type%22:0%7D,%7B%22x%22:2090,%22y%22:1529,%22z%22:392,%22timestamp%22:17162,%22k%22:98,%22type%22:0%7D,%7B%22x%22:1722,%22y%22:1170,%22z%22:20,%22timestamp%22:17267,%22k%22:106,%22type%22:0%7D,%7B%22x%22:4157,%22y%22:3627,%22z%22:2435,%22timestamp%22:17367,%22k%22:62,%22type%22:0%7D,%7B%22x%22:1755,%22y%22:1329,%22z%22:43,%22timestamp%22:17467,%22k%22:93,%22type%22:0%7D,%7B%22x%22:2223,%22y%22:1804,%22z%22:513,%22timestamp%22:17570,%22k%22:101,%22type%22:0%7D,%7B%22x%22:3234,%22y%22:2822,%22z%22:1526,%22timestamp%22:17744,%22k%22:61,%22type%22:0%7D,%7B%22x%22:2055,%22y%22:1650,%22z%22:349,%22timestamp%22:17852,%22k%22:113,%22type%22:0%7D,%7B%22x%22:6048,%22y%22:5634,%22z%22:4300,%22timestamp%22:17952,%22k%22:65,%22type%22:0%7D,%7B%22x%22:6202,%22y%22:5797,%22z%22:4404,%22timestamp%22:18054,%22k%22:95,%22type%22:0%7D,%7B%22x%22:4379,%22y%22:3976,%22z%22:2529,%22timestamp%22:18154,%22k%22:86,%22type%22:0%7D,%7B%22x%22:3775,%22y%22:3358,%22z%22:1829,%22timestamp%22:18255,%22k%22:97,%22type%22:0%7D,%7B%22x%22:4562,%22y%22:4131,%22z%22:2290,%22timestamp%22:18357,%22k%22:121,%22type%22:0%7D,%7B%22x%22:5305,%22y%22:4884,%22z%22:2451,%22timestamp%22:18458,%22k%22:116,%22type%22:0%7D,%7B%22x%22:6979,%22y%22:6564,%22z%22:4061,%22timestamp%22:18559,%22k%22:70,%22type%22:0%7D,%7B%22x%22:5451,%22y%22:5049,%22z%22:2494,%22timestamp%22:18660,%22k%22:122,%22type%22:0%7D,%7B%22x%22:3540,%22y%22:3159,%22z%22:566,%22timestamp%22:18761,%22k%22:87,%22type%22:0%7D,%7B%22x%22:5624,%22y%22:5251,%22z%22:2649,%22timestamp%22:18871,%22k%22:122,%22type%22:0%7D,%7B%22x%22:8178,%22y%22:7812,%22z%22:5205,%22timestamp%22:18981,%22k%22:123,%22type%22:0%7D]&dm_img_str=V2ViR0wgMS4wIChPcGVuR0wgRVMgMi4wIENocm9taXVtKQ&dm_cover_img_str=QU5HTEUgKEludGVsLCBJbnRlbChSKSBIRCBHcmFwaGljcyA1MzAgKDB4MDAwMDE5MUIpIERpcmVjdDNEMTEgdnNfNV8wIHBzXzVfMCwgRDNEMTEpR29vZ2xlIEluYy4gKEludGVsKQ&dm_img_inter=%7B%22ds%22:[%7B%22t%22:0,%22c%22:%22%22,%22p%22:[158,10,-914],%22s%22:[323,3379,1214]%7D],%22wh%22:[3999,5863,73],%22of%22:[3701,5268,500]%7D&w_rid=10f91f9599220f3c78c601ef189bbbb3&wts=1768033474"
        data = {
            "plat": 1,
            "oid": oid,
            "type": 1,
            "message": message,
            "at_name_to_mid": {},
            "gaia_source": "main_web",
            "csrf": self.csrf,
            "statistics": {"appId":100,"platform":5}
        }
        logger.debug(message)
        if root != "None":
            logger.debug(root)
            data["root"] = root
            data["parent"] = root
        if len(pictures) > 0:
            data["pictures"] = pictures
        if root != "None" and len(pictures) > 0:
            logger.error("无法带图片回复")
            raise ChatError("")
        response = requests.post(url=url, headers=self.headers, data=data, timeout=self.timeout)
        assert response.status_code == 200
        response = response.json()
        if response["code"] != 0:
            logger.debug(response)
            logger.error(f"上传图片发生错误,服务器端响应{response['code']}:  {response['message']}")
            raise ChatError("")
        logger.info(response["data"]["success_toast"])
    
    def unread(self) -> dict:
        """获取未读消息

        Returns:
            dict: "at": 0,"coin": 0,"danmu": 0,"favorite": 0,"like": 0,"recv_like": 0,"recv_reply": 0,"reply": 0,"sys_msg": 0,"sys_msg_style": 1,"up": 0}
        """
        response = requests.get(url="https://api.vc.bilibili.com/x/im/web/msgfeed/unread?build=0&mobi_app=web&web_location=333.40164", headers=self.headers, timeout=self.timeout)
        assert response.status_code == 200
        response = response.json()
        if response["code"] != 0:
            logger.debug(response)
            logger.error(f"服务器响应错误{response['code']}: {response['message']}")
            raise ChatError("")
        return response["data"]
    
    def getReply(self, unhandled: int) -> list[dict[str, str]]:
        """获取最新回复"""
        allData = []
        response = requests.get(url="https://api.bilibili.com/x/msgfeed/reply?platform=web&build=0&mobi_app=web&web_location=333.40164", headers=self.headers, timeout=self.timeout)
        assert response.status_code == 200
        response = response.json()
        unhandled = min(len(response["data"]["items"]), unhandled)
        for i in range(0, unhandled):
            comment: dict = response["data"]["items"][i]
            data: str = comment["item"]["source_content"]
            uri: str = comment["item"]["uri"].split("/")[-1]
            
            logger.info(f"收到“{comment['user']['nickname']}”的回复“{data}”,来自{uri}的“{comment['item']['title']}”")
            allData.append({"data": data, "uid": comment["user"]["mid"], "root": comment["item"]["source_id"], "vid": uri})
        return allData
    
    def getSession(self) -> list:
        """获取私信内容"""
        result = []
        deepseekMessages = []
        sessions = requests.get(url="https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions?session_type=1&group_fold=1&unfollow_fold=0&sort_rule=2&build=0&mobi_app=web&web_location=333.40164&w_rid=45cec6b43396ca8eddc9a838ffe483b7&wts=1768623400", timeout=self.timeout, headers=self.headers)
        assert sessions.status_code == 200
        sessions = sessions.json()
        if sessions["code"] !=0:
            logger.error(f"获取私信内容错误,服务器响应{sessions['message']}")
            raise ChatError("")
        index = 0
        for index, session in enumerate(sessions["data"]["session_list"]):
            deepseekMessages.append([{"role": "system", "content": config["deepseekSystem"]}])
            unread = session["unread_count"]
            if unread == 0: continue
            logger.info(f"---------发现新私信，开始处理---------")
            talker_id: str = session["talker_id"]
            response = requests.get(url=f"https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs?size=20&session_type=1&talker_id={talker_id}&begin_seqno=2229986950660096&end_seqno=&sender_device_id=1&build=0&mobi_app=web&web_location=333.40164&w_rid=ad034ce3f01d892320e6f76660b604da&wts=1768614059", timeout=self.timeout, headers=self.headers)
            assert response.status_code == 200
            response = response.json()
            if response["code"] !=0:
                logger.debug(response)
                logger.error(f"获取私信内容错误,服务器响应{response['message']},跳过本次消息回应")
                continue
            # 获取最新一条消息
            if response["data"]["messages"][0]["msg_type"] == 1:
                logger.debug(json.loads(response["data"]["messages"][0]["content"]))
                result.append({"uid": response["data"]["messages"][0]["sender_uid"], "content": json.loads(response["data"]["messages"][0]["content"])["content"], "receiver_id": response["data"]["messages"][0]["receiver_id"]})
            
            # 获取历史消息
            for message in reversed(response["data"]["messages"]):     
                
                if message["msg_type"] == 1:
                    # 是文字
                    try: content: str = json.loads(message["content"])["content"]
                    except: logger.error("不是合法json");logger.debug(message);raise ChatError("")
                    deepseekMessages[index].append({"role": f"{"assistant" if self.uid == message['sender_uid'] else "user"}", "content": content})
            
            self.update_ack(talker_id)
               
        return [result, deepseekMessages]
             
    def update_ack(self, talker: str) -> None:
        """消息已读

        Args:
            talker (str): 对话id
        """
        data = {
            "talker_id": talker,
            "session_type": 1,
            "ack_seqno": "2230369940434945",
            "build": 0,
            "mobi_app": "web",
            "csrf": self.csrf
        }
        response = requests.post(url="https://api.vc.bilibili.com/session_svr/v1/session_svr/update_ack", timeout=self.timeout, headers=self.headers, data=data).json()
        if response["code"] != 0:
            logger.error(f"已读错误,{response['message']}")
            raise ChatError("")
    
    def replyPrivate(self, sender: str, receiver: str, message: dict, msg_type: int):
        """回复私信

        Args:
            sender (str): 发送人Uid
            receiver (str): 接收人uid
            message (dict): 消息,字典格式,仅文字{"content":"12"},图片: {"url":"1.webp","width":1920,"height":1080,"imageType":"jpeg","size":91.694,"original":1}
            msg_type (int): 1为文字,2为图片
        """
        data = {
            "msg[sender_uid]": sender,
            "msg[receiver_type]": 1,
            "msg[receiver_id]": receiver,
            "msg[msg_type]": msg_type,
            "msg[msg_status]": 0,
            "msg[content]": json.dumps(message),
            "msg[new_face_version]": 0,
            "msg[dev_id]": "8948D064-FAE5-49B1-9465-32D36F2D5415",
            "msg[timestamp]": int(time.time()),
            "from_firework": 0,
            "build": 0,
            "mobi_app": "web",
            "msg[canal_token]": "",
            "csrf": self.csrf
        }
        response = requests.post(url=f"https://api.vc.bilibili.com/web_im/v1/web_im/send_msg?w_sender_uid={sender}&w_receiver_id={receiver}&w_dev_id=8948D064-FAE5-49B1-9465-32D36F2D5415&w_rid=dbdd5a6e3bdc3cd7c0625abb0f06e5df&wts={time.time()}", timeout=self.timeout, headers=self.headers, data=data)
        assert response.status_code == 200
        response = response.json()
        if response["code"] != 0: 
            logger.debug(message)
            logger.debug(response)
            logger.error(f"发送私信错误,服务器响应: {response['message']}")
            raise ChatError("")
        logger.debug(response)

    def getDeepAns(self, messages: list) -> str:
        """获取deepseek的回复

        Args:
            messages (list): 用户消息
        """
        content = ""
        allAnswer = ""
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
            stream=True
        ) 
        for chunk in response:
            for byteAnswer in chunk.choices[0].delta.content: # type: ignore
                allAnswer += byteAnswer
                if byteAnswer == "*":
                    logger.info(f"获取回复:{content}")
                    content = ""
                else:
                    content += byteAnswer
        return content
    
ev = EventHandler()

if __name__ == "__main__":
    ev.update_ack("1392280712")
    # ev.replyPrivate("3546570085632174", "1392280712", {"content":"你好"}, 1)