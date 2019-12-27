import datetime
import hashlib
from random import Random 

_chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
def getDatetime(h = -8):
    ''' 获取日期时间，格式 Wed, 04 Sep 2019 01:40:18 GMT
    :param h: 时差，默认减8小时
    '''
    return (datetime.datetime.now() + datetime.timedelta(hours=h)).strftime("%a, %d %b %Y %H:%M:%S GMT")   

def getDate():
    ''' 获取当前日期,格式 1970-01-01
    '''
    return datetime.datetime.now().strftime("%Y-%m-%d") 

def getRandomStr(length = 10):
    ''' 获取随机字符串
    '''
    salt = ''
    len_chars = len(_chars) - 1  
    random = Random()  
    for i in range(length):  
        # 每次从chars中随机取一位
        salt += _chars[random.randint(0, len_chars)]  
    return salt

def createSign(values, md5Key):
    ''' 生成签名
    '''
    # 把key加进去
    values.update({'key': md5Key})
    # 字典序
    sortArr = sorted(values.items(), key = lambda item : item[0])
    signStr = ''
    # 拼接
    for i in sortArr:
        if i[1] != '':
            signStr += str(i[0]) + '=' + str(i[1]) + '&'
    signStr = signStr.strip('&')
    # MD5
    m2 = hashlib.md5()   
    m2.update(signStr.encode('utf-8'))
    # 去掉key
    values.pop('key')
    return m2.hexdigest().upper()