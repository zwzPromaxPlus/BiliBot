import os
from writelog import HandleLog 
import sqlite3
import random
import json
from openai import OpenAI
from config import CONFIG
from EventHandler import ev
import datetime

logger = HandleLog()

class CommandHandler:
    def __init__(self):
        self.conn = sqlite3.connect('lucky.db')
        self.c = self.conn.cursor()
        self.lucky = {}
        self.remindList = []

    def dayLucky(self, uid: str) -> list:
        if not os.path.exists(os.getcwd() + "/pictures/"):
            logger.warning("pictures文件不存在,创建中...")
            os.mkdir(os.getcwd() + "/pictures/")
        
        randomPath = os.getcwd() + "/pictures/" + os.listdir("pictures")[random.randint(0, len(os.listdir("pictures")) - 1)]

        if uid in self.lucky:
            return [f"你的今日运势为: {self.lucky[uid][0]}\n星级:{self.lucky[uid][1]}\n{self.lucky[uid][2]}\n(仅供娱乐、相信科学、请勿迷信)", randomPath]
        
        
        cursor = self.c.execute(f'SELECT * FROM `lucky` WHERE id={random.randint(1, 5)}')
        results = cursor.fetchall()
        logger.info(results)

        needStar = ""
        for i in range(0, int(results[0][2])):
            needStar = needStar + "★"
        self.lucky[uid] = [results[0][1], needStar, results[0][3]]
        
        return [f"你的今日运势为: {results[0][1]}\n星级:{needStar}\n {results[0][3]}(仅供娱乐、相信科学、请勿迷信)", randomPath]

    def cleanLuck(self):
        self.lucky = {}

    def updateRemind(self, date, uid, data) -> None:
        self.c.execute('INSERT INTO "main"."remind" ("date", "wxid", data) VALUES (?,?,?)', (date, uid, data))
        self.conn.commit()
    
    def deleteRemind(self, delDate, uid) -> None:
        self.c.execute('UPDATE "main"."remind" SET "isDeleted" = 2 WHERE date=? AND wxid=?', (delDate, uid))
        self.conn.commit()
    
    def initRemind(self) -> list:
        selectTime = self.c.execute('SELECT * FROM "main"."remind" WHERE "isDeleted"=1')
        selectTimeResult = selectTime.fetchall()
        return selectTimeResult

class deepseek:
    def __init__(self):
        self.client = OpenAI(api_key=CONFIG.deepseek_api, base_url="https://api.deepseek.com") # 初始化deepseek的api

    def deepAnsWithFunc(self, messages: list, tools: list, tempera=0.3) -> list:
        """使用function calling的deepseek

        Args:
            messages (list): messages聊天记录
            tools (list): 工具列表
            tempera (float, optional): 温度. Defaults to 0.3.

        Returns:
            list: 0为str,模型响应文本, 1为bool是否调用函数
        """
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=tempera
        )
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # 根据函数名调用模拟函数
            match function_name:
                case "change_title":
                    function_response = ev.changeVideoInfo(**function_args)
                case "pass":
                    function_response = ev.changeVideoIntro(**function_args)
                case "note":
                    function_response = self.note(**function_args)
                case "get_user":
                    function_response = self.get_user(**function_args)
                
            # 将结果返回给模型（但不执行实际功能）
            messages.append(response.choices[0].message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(function_response)
            })
            second_response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )
            return [str(second_response.choices[0].message.content), True]
        else:
            return [str(response.choices[0].message.content), False]

    def getDeepAns(self, messages: list) -> str:
        """普通版获取deepseek的回复

        Args:
            message (str): 用户消息
        """
        content = ""
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
            stream=True
        ) # type: ignore
        for chunk in response:
            for byteAnswer in chunk.choices[0].delta.content: # type: ignore
                content += byteAnswer
        return content
    
    def note(self, message) -> str:
        logger.warning(f"需要被注意的事情{message}")
        with open ("notes.txt", "w+") as f:
            f.write(f"{datetime.datetime.now()} [note]: {message}")
        return "Successfully"

    def get_user(self, user_name=CONFIG.bot_name) -> str:
        re = ev.getUserByName(user_name)
        return f"用户名:{re['name']}, 简介: {re['introduction']}, 作品总数: {re['videoNum']}, 作品列表: {re['videos']}"
    