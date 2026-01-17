import os
from writelog import HandleLog 
import sqlite3
import random

logger = HandleLog()
conn = sqlite3.connect('lucky.db')
c = conn.cursor()
lucky = {}

def dayLucky(uid: str) -> list:
    if not os.path.exists(os.getcwd() + "\\pictures\\"):
        logger.warning("pictures文件不存在,创建中...")
        os.mkdir(os.getcwd() + "\\pictures\\")
    
    randomPath = os.getcwd() + "\\pictures\\" +os.listdir("pictures")[random.randint(0, len(os.listdir("pictures")) - 1)]

    if uid in lucky:
        return [f"你的今日运势为: {lucky[uid][0]}\r星级:{lucky[uid][1]}\r{lucky[uid][2]}\r(仅供娱乐、相信科学、请勿迷信)", randomPath]
    
    
    cursor = c.execute(f'SELECT * FROM `lucky` WHERE id={random.randint(1, 5)}')
    results = cursor.fetchall()
    logger.info(results)

    needStar = ""
    for i in range(0, int(results[0][2])):
        needStar = needStar + "★"
    lucky[uid] = [results[0][1], needStar, results[0][3]]
    
    return [f"你的今日运势为: {results[0][1]}\n星级:{needStar}\n {results[0][3]}(仅供娱乐、相信科学、请勿迷信)", randomPath]

