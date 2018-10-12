import json

def _readFile(file_name: str):
    """读文件,返回dict"""
    with open('../static_file/{}'.format(file_name), 'r', encoding='utf8') as f:
        return json.load(f)


result_dict = _readFile('make101000001_model102000004.trim')
print(type(result_dict))
print(result_dict)