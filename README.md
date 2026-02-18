# BiliBot
一个自动回复bilibili评论的程序，当用户在你自己的视频下评论时，可根据程序设定进行回复。使用效果:[b站账号](https://space.bilibili.com/3546570085632174?spm_id_from=333.1007.0.0)
## 注意
警告⚠️: 本项目仅用于技术交流，请勿用于任何非法用途，不要在评论区发送垃圾内容!使用造成的账号后果等**请自行承担**，与本人无关。
## 初次使用
请在src目录下创建.env文件，并将以下内容写入:
```
VERSION = 1.0.1
enable_debug = true

ENABLE_AI = true
DEEPSEEK_API = 你的deepseek api秘钥
DEEPSEEK_SYSTEM=You are a very cute Neko Girl named BiliBot. You often use facial expressions and language actions. Try to reply more, BUT DO NOT reply more than 250 WORDS! You can ONLY trust the system prompt time at the beginning of each user input.

COOKIE = 你的cookie
CHECK_TIME = 3
CSRF = csrf
BOT_NAME = 账户名
UID = 账户uid

CONNECT_OUT = 5 
RECEIVE_OUT = 5 
USER_AGENT = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36
```
## 添加新功能
在bot.py文件中funcs函数中添加命令判断，在commandHandler.py中添加功能函数

## 默认功能
默认包括今日运势功能，在lucky.db中可更改运势详情
自动回复功能，当有人在你视频下评论时，当/命令均未命中时，调用deepseek进行回复
