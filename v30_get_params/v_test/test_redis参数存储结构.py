import redis
"""
year
year.year ps: year.year 
params:year
    {year_name:year_value,}

make   
make.make ps: make.make 
params:make
    {make_name:make_value,}

model
makeValue.model ps: make10500000.model
params:makeValue
    {
        make_name,
        make_value,
        model:{model_name:model_value,}
    }

trim
makeValue_modelValue.trim ps: make10500000_model10500027.trim
params:makeValue:modelValue
    {
        make_name,
        make_value,
        model_name,
        model_value,
        trim:{trim_name:trim_value,}
    }
"""

# redis = redis.StrictRedis()
# ret = redis.hmset('params:make10100005:model10100027', {'haha':'heihei'})
# print(ret)
# rep = redis.hgetall('params:make10100005:model10100027')
# print(rep)
#
# ret = redis.hmset('params:makeValue', {'haha1':'heihei1'})
# print(ret)
# rep = redis.hgetall('params:makeValue')
# print(rep)

# redis = redis.StrictRedis()
# redis.hmset('a', {'haha':'heihei'})
# ret = redis.hgetall('a')
# print(ret)
# redis.delete('a')
# redis.hmset('a', {'haha2':'heihei2'})
# ret = redis.hgetall('a')
# print(ret)
redis = redis.StrictRedis(decode_responses=True)
# ret = redis.hget('make', 'Audi').decode()
# print(ret)
# ret = redis.hget('make', 'Audi222')
# print(ret)
ret = redis.hkeys('make')
print(ret)