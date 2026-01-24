import os
from writelog import HandleLog 
import sqlite3
import random
import json
from openai import OpenAI
from config import CONFIG
from EventHandler import ev

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

        if uid in lucky:
            return [f"你的今日运势为: {lucky[uid][0]}\n星级:{lucky[uid][1]}\n{lucky[uid][2]}\n(仅供娱乐、相信科学、请勿迷信)", randomPath]
        
        
        cursor = self.c.execute(f'SELECT * FROM `lucky` WHERE id={random.randint(1, 5)}')
        results = cursor.fetchall()
        logger.info(results)

        needStar = ""
        for i in range(0, int(results[0][2])):
            needStar = needStar + "★"
        lucky[uid] = [results[0][1], needStar, results[0][3]]
        
        return [f"你的今日运势为: {results[0][1]}\n星级:{needStar}\n {results[0][3]}(仅供娱乐、相信科学、请勿迷信)", randomPath]

    def cleanLuck(self):
        global lucky
        lucky = {}

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

    def deepAnsWithFunc(self, messages: list) -> str:
        tools = [{
            "type": "function",
            "function": {
                "name": "change_title",
                "description": "Change the name of the video.Do not use in situations that are not very, very important.This is very dangerous.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The new name of the video.",
                        }
                    },
                    "required": ["title"]
                },
            }
        }]
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools, # type: ignore
            tool_choice="auto",
            temperature=0.3
        )
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # 根据函数名调用模拟函数
            if function_name == "change_title":
                function_response = ev.changeVideoInfo(**function_args)
            
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
            logger.warning(second_response.choices[0].message.content)
            return str(second_response.choices[0].message.content)
        else:
            logger.info(f"用户失败, 模型响应: {response.choices[0].message.content}")
            return str(response.choices[0].message.content)

    def getDeepAns(self, messages: list) -> str:
        """普通版获取deepseek的回复

        Args:
            message (str): 用户消息
        """
        content = ""
        allAnswer = ""
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
            stream=True
        ) # type: ignore
        for chunk in response:
            for byteAnswer in chunk.choices[0].delta.content: # type: ignore
                allAnswer += byteAnswer
                if byteAnswer == "*":
                    logger.info(f"获取回复:{content}")
                    content = ""
                else:
                    content += byteAnswer
        return content
    
