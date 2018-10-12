import logging, time

"""manheim账号密码"""
USERNAME = 'jamaal3238'
PASSWORD = 'pathfinder'
NICKNAME = 'ABDULKADIR FARAH'

"""日志"""
DEFAULT_LOG_LEVEL = logging.INFO    # 默认等级
DEFAULT_LOG_FMT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s'   # 默认日志格式
DEFUALT_LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'  # 默认时间格式
now = time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time()))
DEFAULT_LOG_FILENAME = './log/{}.log'.format(now)    # 默认日志文件名称


"""Request相关配置"""
# 默认请求头
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
# 默认单次请求重试次数
REQUEST_RETRY_NUMS = 3
# 默认单次请求最大等待时间,单位:秒
REQUEST_TIMEOUT = 30
# 随机延时请求的最大时间,单位:秒
REQUEST_DELAY = 5

"""Mongodb相关配置 mongodb操作只能覆盖/修改文档的字段"""
# 数据库配置
MONGO_IP = '127.0.0.1'
MONGO_PORT = 27017 # int
MONGO_DB_NAME = 'cac' # 数据库名
# 请求去重集合: {fp}
MONGO_FP_SET_NAME = 'requests_fp'
# 已登录账号的requests.session对象
"""数据格式: {
_id, 账号username
session_createtime, 生成时间(utc时间)
session_pyobj, requests.session对象序列化
}"""
# 集合名
MONGO_SESSION_SET_NAME = 'session_set'
# requests.session对象的过期时间,单位:秒,默认:30分钟
SESSION_EXTIME = 60*30

# 查询参数 :
"""数据格式 xxx_name都为大写
{
type: 'year',
year_name: '2001', 
year_value: '37', 
update_time: 更新时间(utc)
}
{
type: 'make', 制造商/品牌
make_name: 'AUDI',
make_value: '1050000000', 
update_time: 更新时间(utc)
}
{
type: 'model' 型号
make_name, 制造商/品牌
make_value,
model_name, 
model_value,
update_time, 更新时间(utc)
}
{
type: 'trim' 排量,
make_name, 制造商/品牌
make_value,
model_name, 型号
model_value,
trim_name,
trim_value,
update_time, 更新时间(utc)
}"""
# 参数集合名
MONGO_PARAM_SET_NAME = 'param_set'
# 数据文档类型 {type:XXX_TYPE_NAME}
YEAR_TYPE_NAME = 'year'
MAKE_TYPE_NAME = 'make'
MODEL_TYPE_NAME = 'model'
TRIM_TYPE_NAME = 'trim'

