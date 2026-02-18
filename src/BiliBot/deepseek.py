import json
from openai import OpenAI
from config import CONFIG
from EventHandler import EventHandler
from writelog import HandleLog
import datetime
from commandHandler import CommandHandler
import re

ev = EventHandler()
logger = HandleLog()
ch = CommandHandler()

class deepseek:
    def __init__(self):
        self.client = OpenAI(api_key=CONFIG.deepseek_api, base_url="https://api.deepseek.com") # 初始化deepseek的api

    def deepAnsWithFunc(self, messages: list, tools: list, tempera=0.3, user=None, videoIntro="") -> list:
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
                    function_response = "Successfully"
                    ev.changeVideoInfo(videoIntro)
                case "note":
                    function_response = self.note(**function_args)
                case "get_user":
                    function_response = self.get_user(**function_args, user=user)
                case "change_my_name":
                    function_response = ev.changeUserInfo(**function_args)
                case "get_scp":
                    function_response = ch.get_scp(**function_args)
            logger.info("运行结果: " + str(function_response))
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

    def getDeepAns(self, messages: list, model: str="deepseek-chat", extra_body: dict={}) -> str:
        """普通版获取deepseek的回复

        Args:
            message (str): 用户消息
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
            extra_body=extra_body
        )
        content= response.choices[0].message.content
        if content is None : return ""
        logger.debug(content)
        return content
    
    def note(self, message) -> str:
        logger.warning(f"需要被注意的事情{message}")
        with open ("notes.txt", "w+") as f:
            f.write(f"{datetime.datetime.now()} [note]: {message}")
        return "Successfully"

    def get_user(self, user, user_name="当前用户") -> str:
        logger.warning(f"正在查询用户{user}: {user_name}")
        byid=False
        if user_name == "当前用户" or len(user_name) == 0 or user_name=="user" or user_name == "用户": 
            byid = True
            user_name = user
        re = ev.getUser(str(user_name), byid=byid)
        if re["success"] != "成功": return "未查询到指定用户"
        return f"用户名:{re['name']}, 简介: {re['introduction']}, 作品总数: {re['videoNum']},粉丝数: {re['fans']}, 作品列表: {re['videos']}, 注意: 有小概率查询到错误的用户"

