# from code.login import InsertUser
# InsertUser('jamaal3238','pathfinder')

# 过期时间
# from pymongo import MongoClient
# from datetime import datetime
# col = MongoClient().cac.test
# col.create_index([("timer2", 1)], expireAfterSeconds=10)
# col.insert({"timer2": datetime.utcnow(), "user": "haha"})
# import time
# time.sleep(11)
# col.find({'user':'haha'})

# 判断索引是否存在
# from pymongo import MongoClient
# col = MongoClient().cac.test
# for i in col.list_indexes():
#     if 'expireAfterSeconds' in i:
#         print(i)

# 指定更新 没有则创建
# from pymongo import MongoClient
# col = MongoClient().cac.test
# col.update_one({'a':456}, {'$set':{'a':456}}, upsert=True)
# print(col.find({'a':456}))
# from pymongo import MongoClient
# col = MongoClient().cac.test
# col.update_one({'_id':'asd'}, {'$set':{'a':4567, '_id':'asd'}}, upsert=True)
# print(col.find_one({'_id':'asd'}))

# import pickle
# from pymongo import MongoClient
# from conf.settings import USERNAME
# col = MongoClient().cac.session_set
# session = pickle.loads(col.find_one({'_id':USERNAME})['session_pyobj'])
# resp = session.get('http://www.baidu.com')
# print(resp.content.decode())

# from pymongo import MongoClient
# from conf.settings import USERNAME
# col = MongoClient().cac.session_set
# print(col.find_one({'_id':USERNAME}, {'_id':0, 'session_pyobj':1}))


# from pymongo import MongoClient
# col = MongoClient().cac.requests_fp
# ret = col.find_one({'fp':'a7872a5ef2beb5700723cf5e11c9b2c5e9db6637ccc'})
# if ret is None or ret['fp'] != 'a7872a5ef2beb5700723cf5e11c9b2c5e9db6637':
#     print(111)
#     print(333)
# else: print(222)

from pymongo import MongoClient
col = MongoClient().cac.param_set
# cursor_obj = col.find({'type': 'makexx'}, {'_id': 0})
# # cursor_obj = col.find({'type': 'make'}, {'_id': 0})
# ret = {i['make_name']:i['make_value'] for i in cursor_obj}
# print(ret)
# ret = {i['model_name']:i['model_value']
#       for i in col.find({'type': 'model', 'make_name':'ACURA'}, {'_id': 0})}
# print(ret)

ret = {i['year_name']: i['year_value'] for i in col.find({'type': 'year'}, {'_id': 0})}
print(ret)