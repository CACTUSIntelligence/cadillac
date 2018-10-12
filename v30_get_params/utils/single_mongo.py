import pymongo
from utils.log import logger
from conf.settings import MONGO_IP, MONGO_PORT, MONGO_DB_NAME, \
    MONGO_SESSION_SET_NAME, SESSION_EXTIME, \
    MONGO_PARAM_SET_NAME, MONGO_FP_SET_NAME


class SingleMongo():
    def __init__(self):
        self.mongo = pymongo.MongoClient(host=MONGO_IP, port=MONGO_PORT)

    @property
    def paramsMongo(self):
        return self.mongo[MONGO_DB_NAME][MONGO_PARAM_SET_NAME]

    @property
    def sessionMongo(self):
        return self.mongo[MONGO_DB_NAME][MONGO_SESSION_SET_NAME]

    @property
    def fpMongo(self):
        return self.mongo[MONGO_DB_NAME][MONGO_FP_SET_NAME]

    def initExtimeIndex(self):
        """初始化数据库:检查/创建控制过期时间的索引"""
        isindex = False
        # 判断集合以及过期时间索引是否存在
        for index in self.sessionMongo.list_indexes():
            if 'session_createtime' in index:
                isindex = True
        if not isindex: # 如果不存在 : 创建session集合的过期时间索引
            self.sessionMongo.create_index([('session_createtime', 1)],
                                       expireAfterSeconds=SESSION_EXTIME)
        logger.info('session_set过期时间设置成功, 过期时间:{}'.format(SESSION_EXTIME))


try: singleMongo = SingleMongo()
except Exception as e:
    logger.exception(e)
    raise Exception('<进程终止> redis ERROR')