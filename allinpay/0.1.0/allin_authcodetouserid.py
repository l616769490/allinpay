import json
import logging
import requests
from .allin_utils import getRandomStr, createSign

_log = logging.getLogger()

# 接口地址
_AUTH_CODE_TO_USERID_URL = 'https://vsp.allinpay.com/apiweb/unitorder/authcodetouserid'

class AllinAuthCode(object):

    @staticmethod
    def DebugAllinAuthCode():
        ''' 测试用的支付接口
        '''
        return AllinAuthCode('100581048160005', '990440148166000', '00000003', 'a0ea3fa20dbd7bb4d5abf1d59d63bae8')

    def __init__(self, orgid, cusid, appid, md5Key):
        ''' 统一支付接口
        :param orgid: 机构id
        :param cusid: 商户id
        :param appid: 应用id
        :param md5Key: 签名所用的key
        '''
        self.values = {}
        self.values['orgid'] = orgid
        self.values['cusid'] = cusid
        self.values['appid'] = appid
        self.md5Key = md5Key
        self.values['version'] = '11'

    def setAuthType(self, authtype):
        ''' 授权码类型
        '''
        self.values['authtype'] = authtype
        return self
    
    def setSubAppid(self, sub_appid):
        ''' 微信支付appid
        '''
        self.values['sub_appid'] = sub_appid
        return self

    def authcode(self, authcode, **kw):
        ''' 获取用户ID
        '''
        self.values['randomstr'] = getRandomStr()
        self.values['authcode'] = authcode
        self.values.update(kw)

        self.values['sign'] = createSign(self.values, self.md5Key)
        if self._checkValues():
            res = self._post()
            if self._checkValues(res):
                return res
            else:
                _log.error('用户请求支付被拦截，返回结果：%s' % res)
                return '返回参数校验不通过，可能是请求被恶意拦截!'
        else:
            return '参数不合法，请检查请求参数！'
    
    def _checkValues(self, values = None):
        ''' 检查参数是否合法
        :param values:如果为空检查请求参数，否则检查返回参数
        '''
        if values:
            if values['retcode'] == 'SUCCESS':
                v = values.copy()
                sign = v['sign']
                v.pop('sign')
                sign2 = createSign(v, self.md5Key)
                if sign2 == sign:
                    return True
                else:
                    return False
        else:
            if all (k in self.values for k in ('orgid', 'cusid', 'appid', 'authcode', 'authtype', 'randomstr', 'sign')):
                return True
            
        return False

    def _post(self):
        ''' 发送post请求
        '''
        r = requests.post(_AUTH_CODE_TO_USERID_URL, self.values)
        text = json.loads(r.text)
        _log.info('用户发起支付请求，请求参数：%s，请求结果：%s' % (self.values, text))
        return text