
from utils.single_mongo import singleMongo
from code.crawl_params import CrawlParams


class GetParam():
    """参数查询接口类:查询一次就需要重新实例化一次"""
    def __init__(self,
                 make_name: str = '',
                 model_name: str = '',
                 trim_name: str = '',
                 year_name: str = ''):

        self.param_mongo = singleMongo.paramsMongo

        self.make_name = make_name
        self.model_name = model_name
        self.trim_name = trim_name
        self.year_name = year_name

        # [API] xxxx_value
        self.make_value = self.makeDict.get(self.make_name.upper(), '')
        self.model_value = self.modelDict.get(self.model_name.upper(), '')
        self.trim_value = self.trimDict.get(self.trim_name.upper(), '')
        self.year_value = self.yearDict.get(self.year_name.upper(), '')

    @property
    def paramDict(self):
        """
        [API]根据xxxx_name返回xxxx_value
        :param make_name:
        :param model_name:
        :param trim_name:
        :param year_name:
        :return: {}
        """
        return {'make_value': self.make_value,
                'model_value': self.model_value,
                'trim_value': self.trim_value,
                'year_value': self.year_value}

    @property
    def yearDict(self):
        """获取全部的year键值对:return: year_dict or None"""
        return {i['year_name']:i['year_value'] for i in self.param_mongo.find({'type':'year'}, {'_id':0})}

    @property
    def makeDict(self):
        """获取全部的make键值对:return: make_dict or None"""
        return {i['make_name']:i['make_value'] for i in self.param_mongo.find({'type':'make'}, {'_id':0})}

    @property
    def modelDict(self):
        """根据make_value获取全部的Model键值对:return: Model_dict or None"""
        return {i['model_name']:i['model_value']
                for i in self.param_mongo.find({'type':'model', 'make_value':self.make_value},
                                               {'_id':0, 'model_name':1, 'model_value':1})}
    @property
    def trimDict(self):
        """根据make_value and model_value获取全部的Trim键值对:return: Trim_dict or None"""
        return {i['trim_name']:i['trim_value']
                for i in self.param_mongo.find({'type':'trim',
                                                'make_value': self.make_value,
                                                'model_value': self.model_value},
                                               {'_id':0, 'trim_name':1, 'trim_value':1})}


class ParamSpider():
    def __init__(self):
        self.crawler = CrawlParams()

    def getAllParams(self):
        """
        [API]具有断点续爬功能的获取查询参数的接口
        :return:
        """
        self.crawler.getAllParams()


if __name__ == '__main__':
    """以下为接口测试"""
    # 抓取查询参数的接口
    spider = ParamSpider()
    spider.getAllParams()

    # 从mongodb中获取参数的接口
    # g = GetParam(make_name='audi', model_name='a4', trim_name='1.8T', year_name='2006')
    # ret = g.yearDict
    # print(ret)
    # ret = g.makeDict
    # print(ret)
    # ret = g.modelDict
    # print(ret)
    # ret = g.trimDict
    # print(ret)
    # ret = g.paramDict
    # print(ret)

    pass