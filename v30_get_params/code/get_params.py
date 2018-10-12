from utils._single_redis import singleRedis
from conf.settings import MAKE_REDIS_NAME, MODEL_REDIS_NAME, TRIM_REDIS_NAME, YEAR_REDIS_NAME


class GetParams():
    def __init__(self):
        self.redis = singleRedis.params_redis

    def getYearDict(self):
        """获取全部的year键值对:return: year_dict"""
        return self.redis.hgetall(YEAR_REDIS_NAME)

    def getMakeDict(self):
        """获取全部的make键值对:return: make_dict"""
        return self.redis.hgetall(MAKE_REDIS_NAME)

    def getModelDict(self, make_value:str=None):
        """根据make_value获取全部的Model键值对:return: Model_dict"""
        return self.redis.hgetall(MODEL_REDIS_NAME.format(make_value))

    def getTrimDict(self, make_value:str=None, model_value:str=None):
        """根据make_value and model_value获取全部的Trim键值对:return: Trim_dict"""
        return self.redis.hgetall(TRIM_REDIS_NAME.format(make_value, model_value))

    def returnParam(self,
                    make_name:str=None,
                    model_name:str=None,
                    trim_name:str=None,
                    year_name:str=None):
        """
        [API]入参可以忽略大小写,但是严格匹配空格!
        :param make_name:
        :param model_name:
        :param trim_name:
        :param year_name:
        :return: values_dict
        """
        values_dict = {'make_value': '',
                       'model_value': '',
                       'trim_value': '',
                       'year_value': '',}
        if year_name is not None:
            year_value = self.redis.hget(YEAR_REDIS_NAME, year_name.upper()) # 不存在将返回None
            values_dict['year_value'] = '' if not year_value else year_value.decode()
        if make_name is not None:
            make_value = self.redis.hget(MAKE_REDIS_NAME, make_name.upper()) # 不存在将返回None
            values_dict['make_value'] = '' if not make_value else make_value.decode()
            if model_name is not None:
                model_value = self.redis.hget(MODEL_REDIS_NAME.format(make_value), model_name.upper())
                values_dict['model_value'] = '' if not model_value else model_value.decode()
                if trim_name is not None:
                    trim_value = self.redis.hget(TRIM_REDIS_NAME.format(make_value, model_value), trim_name.upper())
                    values_dict['trim_value'] = '' if not trim_value else trim_value.decode()
        return values_dict

