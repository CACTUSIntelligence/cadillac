import requests, re, pickle
from datetime import datetime
from requests.adapters import HTTPAdapter

from utils.log import logger
# from utils._single_redis import singleRedis
from utils.single_mongo import singleMongo
from conf.settings import (
    USERNAME, PASSWORD, NICKNAME,
    HEADERS, REQUEST_RETRY_NUMS, REQUEST_TIMEOUT,
)

"""登陆 Buy-Search页面 的session 保存到redis/直接返回"""
class Login():
    def __init__(self):
        self.s = requests.session()
        self.s.mount('http://', HTTPAdapter(max_retries=REQUEST_RETRY_NUMS))
        self.s.mount('https://', HTTPAdapter(max_retries=REQUEST_RETRY_NUMS))
        self.s.headers = HEADERS

    def _getAfterLoginSession(self):
        """首页-->登陆-->BUY-Search条件选择页"""
        self.s.get('https://www.manheim.com/', timeout=REQUEST_TIMEOUT) # 首页
        self.s.get('https://publish.manheim.com/en/locations/international.html', timeout=REQUEST_TIMEOUT)
        self.s.get('https://manheim.demdex.net/dest5.html?d_nsid=0', timeout=REQUEST_TIMEOUT)
        self.s.get('https://publish.manheim.com/en/locations/us-locations.html?WT.svl=m_uni_hdr', timeout=REQUEST_TIMEOUT)
        resp = self.s.get('https://www.manheim.com/login?WT.svl=m_uni_hdr', timeout=REQUEST_TIMEOUT)
        self.s.get('https://manheim.demdex.net/dest5.html?d_nsid=0', timeout=REQUEST_TIMEOUT)
        authenticity_token = re.search('name="authenticity_token" type="hidden" value="(.*?)" />', resp.text).group(1)
        login_url = 'https://www.manheim.com/login/authenticate'
        data = {
            'utf8': '✓',
            'authenticity_token': authenticity_token,
            'user[username]': USERNAME,
            'user[password]': PASSWORD,
            'submit': 'Login',
        }
        self.s.post(login_url, data=data, timeout=REQUEST_TIMEOUT) # 登陆
        self.s.get('https://www.manheim.com/members/mymanheim/', timeout=REQUEST_TIMEOUT)
        self.s.get('https://www.manheim.com/members/powersearch/?WT.svl=m_uni_hdr', timeout=REQUEST_TIMEOUT) # BUY-Search页
        # 这个url特殊,咱们多等一会儿 4*REQUEST_TIMEOUT
        resp = self.s.get('https://loginservice-prod.aws.manheim.com/loginservice/issues?username={}&refresh=false'.format(USERNAME), timeout=REQUEST_TIMEOUT*4) # personId?
        logger.info('登录状态检查,返回响应内容:{}'.format(resp.text))
        contactName = re.search('"contactName" : "(.*?)"', resp.text).group(1)
        if contactName == NICKNAME:
            logger.info('账号: {} 登陆成功'.format(USERNAME))
            return self.s
        else:
            raise Exception('login ERROR! 账号异常!')

    def session(self):
        """Login().session()"""
        try: return self._getAfterLoginSession()
        except Exception as e: logger.exception(e)
        raise Exception('login ERROR!')

    def saveSession(self, s:requests.session()):
        """将requests.session对象保存到mongodb"""
        try:
            singleMongo.initExtimeIndex() # 过期时间的索引操作
            session_set = singleMongo.sessionMongo
            # {_id,username账号,session_createtime生成时间(utc时间),session_pyobj,requests.session对象序列化}
            session_item = {
                '_id':USERNAME,
                'session_createtime': datetime.utcnow(),
                'session_pyobj': pickle.dumps(s)
            }
            session_set.update_one({'_id':USERNAME}, {'$set':session_item}, upsert=True)
            logger.info('向mongo中更新写入账号{}的已登录requests.session对象'.format(USERNAME))
        except Exception as e:
            logger.exception(e)
            raise Exception('<进程终止> redis ERROR')


