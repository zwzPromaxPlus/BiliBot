import os
from writelog import HandleLog 
import sqlite3
import random
from config import CONFIG

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

    def changeMod(self, mod: str, uid: str)->None:
        logger.debug(str(uid)+ mod)
        self.c.execute('UPDATE "main"."fans" SET "character"=? WHERE "uid" = ?', (mod, uid))
        self.conn.commit()

    def getMod(self, uid: str) -> str:
        selectFan = self.c.execute('SELECT "character" FROM "main"."fans" WHERE "uid"=?', (uid,))
        selectFanC: str = selectFan.fetchone()
        if len(selectFanC) == 0:
            logger.warning("没有找到用户")
            return "default"
        return selectFanC[0]

    def get_scp(self, name: str) -> str:
        selectSCP = self.c.execute('SELECT * FROM "main"."scps" WHERE "title"=?', (name,))
        selectSCPR = selectSCP.fetchone()
        if not selectSCP:
            return "你无权访问此文件,权限不足。"
        return selectSCPR
