import pickle

from code.login import Login
from utils._single_redis import singleRedis
from code.crawl_params import GetParamsDicts

# s = Login()
# session = s.session()
# s.saveSession(session)
#
# session_str = singleRedis.get('login_cookies:jamaal3238')
# session_obj = pickle.loads(session_str)
#
# resp = session_obj.get('http://www.baidu.com')
# print(resp.content.decode())


# s = Login()
# session = s.session()
# s.saveSession(session)
#
# g = GetParamsDicts()
# session_str = singleRedis.get('login_cookies:jamaal3238')
# session_obj = pickle.loads(session_str)
#
# g.s = session_obj
# ret = g._getParamsDict(isgetyear=True)
# print(ret)