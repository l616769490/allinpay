import json
import hashlib
import logging
import requests
from .allin_utils import getRandomStr, createSign

_log = logging.getLogger()

# 交易接口
_QUERY_URL = 'https://vsp.allinpay.com/apiweb/unitorder/query'

class AllinQuery(object):

    @staticmethod
    def DebugAllinQuery():
        ''' 测试用的接口
        '''
        return AllinQuery('100581048160005', '990440148166000', '00000003', 'a0ea3fa20dbd7bb4d5abf1d59d63bae8')

    def __init__(self, orgid, cusid, appid, md5Key):
        ''' 查询接口
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
    
    def setReqsn(self, reqsn):
        ''' 交易流水 reqsn和trxid必填其一;建议:商户如果同时拥有oldtrxid和oldreqsn,优先使用oldtrxid 
        '''
        self.values['reqsn'] = reqsn
        return self
    
    def setTrxid(self, trxid):
        ''' 交易流水 reqsn和trxid必填其一;建议:商户如果同时拥有oldtrxid和oldreqsn,优先使用oldtrxid 
        '''
        self.values['trxid'] = trxid
        return self

    def query(self, **kw):
        ''' 查询
        :param **kw: 其他支付信息
        '''
        self.values['randomstr'] = getRandomStr()
        self.values.update(kw)

        self.values['sign'] = createSign(self.values, self.md5Key)
        if self._checkValues():
            res = self._post()
            if self._checkValues(res):
                return res
            else:
                _log.error('用户请求查询被拦截，返回结果：%s' % res)
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
            if all (k in self.values for k in ('orgid', 'cusid', 'appid', 'randomstr', 'sign')):
                return True
            
        return False

    def _post(self):
        ''' 发送post请求获取二维码
        '''
        r = requests.post(_QUERY_URL, self.values)
        text = json.loads(r.text)
        _log.info('用户发起退款请求，请求参数：%s，请求结果：%s' % (self.values, text))
        return text

# if __name__ == "__main__":
#     allinQuery = AllinQuery.DebugAllinQuery().setTrxid('111994120000928109')
#     res = allinQuery.query()
#     print(res)