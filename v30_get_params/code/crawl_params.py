import time
import json
import pickle
import random
import hashlib
import w3lib.url
from lxml import etree
from copy import deepcopy
from datetime import datetime

from code.login import Login
from utils.log import logger
from utils.single_mongo import singleMongo
from conf.settings import (
    YEAR_TYPE_NAME,MAKE_TYPE_NAME,MODEL_TYPE_NAME,TRIM_TYPE_NAME, # 类型
    USERNAME, # 账号
    REQUEST_DELAY # 请求最大延时
)

class CrawlParams():
    """获取查询参数 make model trim year"""
    def __init__(self):
        """session：已登陆"""
        # self.param_redis = singleRedis.params_redis # 单例的redis操作对象
        self.param_mongo = singleMongo.paramsMongo # mongodb查询参数集合
        self.fp_mongo = singleMongo.fpMongo # mongodb请求对象指纹集合
        self.s = None # requests.session()
        self.url = 'https://www.manheim.com/members/powersearch/getRefinements.do?RefinementId={}'
        self.fail_request_nums = 0 # 失败请求总数: 对同一Request发送请求,最终失败的,算一次
        self.response_nums = 0 # 响应总数/成功请求总数: 对同一Request发送请求,最终成功,算一次
        self.params_json_nums = 0 # 获取参数文件的总数
        self.old_params_json_nums = 0 # 已存在的文件总数

    # def _readFile(self, file_name:str):
    #     """读文件,返回dict"""
    #     try:
    #         with open(file_name, 'r', encoding='utf8') as f:
    #             return json.load(f)
    #     except Exception as e:
    #         logger.exception(e)
    #         logger.error('<进程终止> file read ERROR:{}'.format(file_name))
    #         raise Exception('<进程终止> file read ERROR:{}'.format(file_name))
    #
    # def _writeFile(self, file_name:str, result_dict:dict):
    #     """将参数字典写入文件"""
    #     try:
    #         with open(file_name, 'w', encoding='utf8') as f:
    #             f.write(json.dumps(result_dict, ensure_ascii=False, indent=4))
    #         self.params_json_nums += 1
    #     except Exception as e:
    #         logger.exception(e)
    #         logger.error('<进程终止> file write ERROR:{}'.format(file_name))
    #         raise Exception('<进程终止> file write ERROR:{}'.format(file_name))

    def _saveParams(self, type_name:str, item:dict):
        """保存参数:redis and file"""
        if item != {}:
            update_item = deepcopy(item)
            update_item['update_time'] = datetime.utcnow() # 更新时间(utc)
            try: self.param_mongo.update_one(item, {'$set':update_item}, upsert=True)
            except Exception as e:
                logger.exception(e)
                logger.warn('没有写入的数据: {}'.format(item))
                logger.error('<进程终止>: mongodb ERROR')
                raise Exception('<进程终止>: mongodb ERROR')
        else: logger.info('<无数据>:{}'.format(type_name))

    @property
    def _data(self): # 发送post请求的postdata
        data = {
            'searchOperation': '',
            'sellerCompany': '',
            'newSort': 'false',
            'sortKeys': 'YEAR',
            'previousSortKeys': '',
            'sortIndicator': 'FORWARD',
            'recordOffset': '0',
            'fromYear': 'ALL',
            'toYear': 'ALL',
            'distance': '0',
            'distanceUnits': 'MILES',
            'zipCode': '43224',
            'saleDate': '',
            'certified': '',
            'searchTerms': '',
            'mmrRanges': 'ALL',
            'inventoryChannels': '',
            'listingFromTime': '',
            'listingToTime': '',
            'submittedFilters': '',
            'vehicleUniqueId': '',
            'detailPageUrl': '',
            'vin': '',
            'channel': '',
            'displayDistance': '',
            'saleId': '',
            'saleGroupId': '',
            'fromOdometer': '0',
            'toOdometer': 'ALL',
            'fromValuation': '0',
            'toValuation': 'ALL',
            'valuationType': 'MMR',
            'includeMissingValuations': 'on',
            'conditionGradeRefined': 'false',
            'fromConditionGrade': '0.0',
            'toConditionGrade': '5.0',
            'resultsPerPage': '25',
        }
        return [(k, v) for k,v in data.items()]

    def _to_bytes(self, string): # 转换为二进制
        if isinstance(string, str): return string.encode("utf-8")
        else: return string

    def _gen_fp(self, url, special_data:str, method='POST'):
        """生成request.fp,并保存到fp集合"""
        url = w3lib.url.canonicalize_url(url)
        method = method.upper()
        s1 = hashlib.sha1()
        s1.update(self._to_bytes(url))  # sha1计算的对象必须是字节类型
        s1.update(self._to_bytes(method))
        s1.update(self._to_bytes(special_data))
        return s1.hexdigest()

    def _check_fp(self, fp):
        """检查fp指纹是否存在,存在返回True,不存在则存入"""
        ret = self.fp_mongo.find_one({'fp':fp})
        if ret is None or ret['fp'] != fp:
            self.fp_mongo.insert({'fp': fp})
            return False
        else: return True

    def _sendPostRequest(self, url:str, data:list, special_data:str):
        """发送post请求,返回响应response or None;
        fp请求去重"""
        fp = self._gen_fp(url=url, special_data=special_data)
        if not self._check_fp(fp): # fp不存在
            try: # 在配置中已设置单次请求重试次数
                time.sleep(random.randint(1, REQUEST_DELAY))  # 随机延时发送请求
                resp = self.s.post(url, data=data)
                self.response_nums += 1
                logger.info('发送请求{} <POST {} {}>'.format(fp, special_data, url))
                return resp
            except Exception as e:
                logger.exception(e)
                logger.error('<请求丢失>{} send Request ERROR:<POST {}>'.format(fp, url))
                self.fail_request_nums += 1
                return None
        else: logger.info('<请求去重> 发现重复的请求{} <POST {} {}>'.format(fp, special_data, url))

    # 发送具体的一个请求,并提取参数,返回单层参数字典
    def _getParamsDict(self,
                       make_value:str=None,
                       model_value:str=None,
                       trim_value:str=None,
                       isgetyear=False):
        if not make_value and not model_value and not trim_value and not isgetyear:
            # 获取make字典 post RefinementId=101000000
            data = deepcopy(self._data)
            resp = self._sendPostRequest(self.url.format('101000000'), data=data, special_data='make')
        elif make_value is not None and not model_value and not trim_value:
            # 获取model字典 post RefinementId=102000000
            data = deepcopy(self._data)
            data.append(('refinements', 'MAKE|{}'.format(make_value))) # refinements: MAKE|101000005 # audi
            resp = self._sendPostRequest(self.url.format('102000000'), data=data, special_data='model:MAKE|{}'.format(make_value))
        elif make_value is not None and model_value is not None and not trim_value:
            # 获取trim字典 post RefinementId=103000000
            data = deepcopy(self._data)
            data.append(('refinements', 'MAKE|{}'.format(make_value)))  # refinements: MAKE|101000005 # audi
            data.append(('refinements', 'MODEL|{}'.format(model_value)))  # refinements: MODEL | 102000027 # A4
            resp = self._sendPostRequest(self.url.format('103000000'), data=data, special_data='trim:MAKE|{} MODEL|{}'.format(make_value, model_value))
        elif isgetyear:
            # 获取year字典 post RefinementId=10
            data = deepcopy(self._data)
            resp = self._sendPostRequest(self.url.format('10'), data=data, special_data='year')
            logger.info('抓取year_list <POST {}>'.format(self.url.format('10')))
        else:
            logger.exception('参数异常 make_value:{}, model_value:{}, trim_value:{}'.format(
                make_value, model_value, trim_value
            ))
            logger.error('<进程终止> 参数异常')
            raise Exception('<进程终止> 参数异常')

        # 提取key:value
        if resp != None:
            html = etree.HTML(resp.text)
            result_dict = {}
            for li in html.xpath('//li'):
                # 参数的xxx_name全部都为大写!
                result_name = li.xpath('.//input[1]/@id')[0].upper()
                result_value = li.xpath('.//input[1]/@value')[0]
                result_dict[result_name] = result_value
            return result_dict
        else: return {}

    def _getAllParams(self):
        """运行逻辑：抓取/刷新请求参数;先抓取,再替换"""
        # 获取year
        year_dict = self._getParamsDict(isgetyear=True)
        if year_dict != {}: # 如果为{}:请求已经发送过了,数据应该存在(数据库无删库操作的前提下)
            logger.info('获取year:{}'.format(year_dict))
            for year_name,year_value in year_dict.items():
                year_item = {'year_name': year_name,
                             'year_value': year_value,
                             'type': YEAR_TYPE_NAME}
                self._saveParams(YEAR_TYPE_NAME, year_item)

        # 获取make
        make_dict = self._getParamsDict()
        if make_dict != {}: # 如果为{}:请求已经发送过了,数据应该存在(数据库无删库操作的前提下)
            logger.info('获取make:{}'.format(make_dict))
            for make_name,make_value in make_dict.items():
                make_item = {'make_name': make_name,
                             'make_value': make_value,
                             'type': MAKE_TYPE_NAME}
                self._saveParams(MAKE_TYPE_NAME, make_item)
        else: # 从数据库获取make_dict
            make_dict = {i['make_name']:i['make_value']
                         for i in self.param_mongo.find({'type': 'make'}, {'_id': 0})}

        # 获取model
        for make_name,make_value in make_dict.items():
            model_dict = self._getParamsDict(make_value=make_value)
            if model_dict != {}: # 该请求已经发送过了 / 该make就不存在任何Model
                logger.info('获取model:{} FROM [make{}]'.format(model_dict,make_name))
                for model_name,model_value in model_dict.items():
                    model_item = {'model_name': model_name,
                                  'model_value': model_value,
                                  'make_name': make_name,
                                  'make_value': make_value,
                                  'type': MODEL_TYPE_NAME}
                    self._saveParams(MODEL_TYPE_NAME, model_item)
            else: # 从数据库获取该make的所有model(可能不存在该make的任何Model)
                model_dict = {i['model_name']:i['model_value']
                              for i in self.param_mongo.find({'type': 'model',
                                                              'make_name':make_name,
                                                              'make_value':make_value},
                                                             {'_id': 0})}

            # 获取trim
            for model_name, model_value in model_dict.items():
                trim_dict = self._getParamsDict(make_value=make_value, model_value=model_value)
                if trim_dict != {}:
                    logger.info('获取trim:{} FROM [make{}>model{}]'.format(trim_dict,make_name,model_name))
                    for trim_name,trim_value in trim_dict.items():
                        trim_item = {'trim_name': trim_name,
                                     'trim_value': trim_value,
                                     'make_name': make_name,
                                     'make_value': make_value,
                                     'model_name': model_name,
                                     'model_value': model_value,
                                     'type': TRIM_TYPE_NAME}
                        self._saveParams(TRIM_TYPE_NAME, trim_item)

    def _getSession(self):
        """获取已登录账号的requests.session对象"""
        try:
            session_mongo = singleMongo.sessionMongo
            session_dict = session_mongo.find_one({'_id':USERNAME}, {'_id':0, 'session_pyobj':1})
        except Exception as e:
            logger.exception(e)
            raise Exception('<进程终止> mongodb ERROR')
        if session_dict is not None: # redis中存在session
            self.s = pickle.loads(session_dict['session_pyobj'])
            logger.info('从mongodb获取账号{}的requests.session对象:{}'.format(USERNAME, self.s))
        else: # redis中不存在/报错 重新建立session
            logger.info('账号:{}的requests.session对象已过期,重新登录获取'.format(USERNAME))
            l = Login()
            self.s = l.session()
            try: l.saveSession(self.s)
            except: logger.warn('mongodb连接异常:无法保存账号{}的requests.session对象到mongodb中'.format(USERNAME, self.s))

    def getAllParams(self):
        """
        [API]重新抓取:先抓取,再删除redis,最后写入redis并覆盖写入file
        :return: None
        """
        logger.info('[ START ] 对参数进行<重新>抓取')
        start_time = datetime.now()
        logger.info('<进程开始> {}'.format(start_time))
        self._getSession()
        self._getAllParams()
        end_time = datetime.now()
        logger.info('<进程结束> {}'.format(end_time))
        logger.info("耗时：%s" % (end_time - start_time).total_seconds())
        logger.info("响应总数(成功请求)的总数：{}个".format(self.response_nums))
        logger.info("失败请求总数：{}个".format(self.fail_request_nums))
        logger.info("获取参数文件的总数：{}个".format(self.params_json_nums))
        logger.info('[ END ]')


if __name__ == '__main__':

    logger.warn('进程入口: api.py')