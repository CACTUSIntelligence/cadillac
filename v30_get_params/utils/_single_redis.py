import redis
from utils.log import logger
from conf.settings import REDIS_IP, REDIS_PORT


class SingleRedis():
    def __init__(self):
        self.params_redis = redis.StrictRedis(host=REDIS_IP,
                                               port=REDIS_PORT,
                                               decode_responses=True)
        self.session_redis = redis.StrictRedis(host=REDIS_IP,
                                               port=REDIS_PORT)

    @property
    def paramsRedis(self):
        return self.params_redis

    @property
    def sessionRedis(self):
        return self.session_redis


try: singleRedis = SingleRedis()
except Exception as e:
    logger.exception(e)
    raise Exception('<进程终止> redis ERROR')
