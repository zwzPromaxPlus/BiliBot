import schedule
from EventHandler import EventHandler
from writelog import HandleLog
import commandHandler as ch
import time
from ErrorHandler import ChatError
import os
import tomllib

# ----初始化-----
ev = EventHandler() # 初始化事件处理器
logger = HandleLog()

logger.info("欢迎使用BiliBot1.0版本,作者: 猜猜我是谁")

if not os.path.exists(os.getcwd() + "\\config.toml"):
    logger.error("配置文件不存在,请创建配置文件后再次运行")
    exit(0)


with open (os.getcwd() + "\\config.toml", "rb") as f:
    config = tomllib.load(f)

def funcs(cod: str,uid: str,deepseekMessages,target=1 ) -> str:
    """功能列表 在这里添加你的功能

    Args:
        cod (str): 评论内容
        uid (str): 用户id
        deepseekMessages (list): 聊天记录
        target (int):1为视频,2为私信
    """
    
    if cod.startswith("/今日运势"):
        luck = ch.dayLucky(uid)
        if target == 2:
            pic = ev.uploadPic(luck[1])
            ev.replyPrivate(config["uid"], uid, message={"url": pic["img_src"],"width": pic["img_width"],"height": pic["img_height"],"imageType": "jpeg","size": pic["img_size"],"original":1}, msg_type=2)
        return luck[0]
    elif cod.startswith("/test"):
        return f"Hello World!{config['bot_name']}活的很好"
    else:
        # 寻求Deepseek
        if config["enable_ai"]:
            deepseekAns = ev.getDeepAns(deepseekMessages)
            return deepseekAns
    return ""

def lookNew():
    try:
        undict = ev.unread()
        if undict["recv_reply"] != 0:
            logger.info(f"---------共发现{undict['recv_reply']}条新评论，开始处理---------")
            unHandled = ev.getReply(undict["recv_reply"])
            for comment in unHandled:
                cod = comment["data"]
                uid = comment["uid"]
                oid: str = ev.getOid(comment["vid"])
                root = comment["root"]
                ev.sendComment(funcs(cod, uid, deepseekMessages=[{"role": "system", "content": config["deepseekSystem"]}, {"role": "user", "content": cod}]), oid=oid, root=root)

        unHandled = ev.getSession()
        for index, infor in enumerate(unHandled[0]):
            ev.replyPrivate(sender=infor["receiver_id"], receiver=infor["uid"], message={"content": funcs(infor["content"], infor["uid"],target=2, deepseekMessages=unHandled[1][index])}, msg_type=1)
        
            
    except (TimeoutError, ConnectionAbortedError, ConnectionRefusedError, ConnectionError, ConnectionResetError) as te:
        logger.warning(f"发生请求错误{te}")
    except AssertionError as asert:
        logger.error(f"服务器连接错误{asert}")
    except ChatError:
        pass
    except Exception as e:
        logger.critical(f"未知错误，{e}", stack_info=True)

schedule.every(config["checkTime"]).seconds.do(lookNew)

while True:
    schedule.run_pending()
    time.sleep(1)

