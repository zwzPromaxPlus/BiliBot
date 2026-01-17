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

def funcs(oid: str, cod: str, root: str, uid: str) -> None:
    """功能列表 在这里添加你的功能

    Args:
        oid (str): 视频oid
        cod (str): 评论内容
        root (str): 评论id
        uid (str): 用户id
    """
    
    
    if cod.startswith("/今日运势"):
        luck = ch.dayLucky(uid)
        ev.sendComment(message=luck[0] ,oid=oid , root=root)
    elif cod.startswith("/test"):
        ev.sendComment(message=f"Hello World!{config['bot_name']}活的很好", oid=oid, root=root)
    else:
        # 寻求Deepseek
        if config["enable_ai"]:
            ev.sendComment(ev.getDeepAns(cod), oid, root=root)

def lookNew():
    try:
        undict = ev.unread()
        if undict["recv_reply"] == 0:
            return 
        logger.info(f"---------共发现{undict['recv_reply']}条新评论，开始处理---------")
        unHandled = ev.getReply(undict["recv_reply"])
        for comment in unHandled:
            cod = comment["data"]
            uid = comment["uid"]
            oid: str = ev.getOid(comment["vid"])
            root = comment["root"]
            funcs(oid, cod, root, uid)
            
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

