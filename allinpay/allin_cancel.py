import json
import hashlib
import logging
import requests
from .allin_utils import getRandomStr, createSign

_log = logging.getLogger()

# 交易撤销接口
_CANCEL_URL = 'https://vsp.allinpay.com/apiweb/unitorder/cancel'

class AllinCancel(object):

    @staticmethod
    def DebugAllinCancel():
        ''' 测试用的接口
        '''
        return AllinCancel('990440148166000', '00000003', 'a0ea3fa20dbd7bb4d5abf1d59d63bae8')

    def __init__(self, cusid, appid, md5Key):
        ''' 交易撤销，全额退款接口
        :param cusid: 商户id
        :param appid: 应用id
        :param md5Key: 签名所用的key
        '''
        self.values = {}
        self.values['cusid'] = cusid
        self.values['appid'] = appid
        self.md5Key = md5Key
        self.values['version'] = '11'


    def setOldreqsn(self, oldreqsn):
        ''' 设置原交易单号
        '''
        self.values['oldreqsn'] = oldreqsn
        return self
    
    def setOldtrxid(self, oldtrxid):
        ''' 原交易流水 oldreqsn和oldtrxid必填其一;建议:商户如果同时拥有oldtrxid和oldreqsn,优先使用oldtrxid 
        '''
        self.values['oldtrxid'] = oldtrxid
        return self

    def cancel(self, money, reqsn, **kw):
        ''' 撤销
        :param money: 支付金额，单位分
        :param reqsn: 订单号，全局唯一
        :param **kw: 其他支付信息
        '''
        self.values['randomstr'] = getRandomStr()
        self.values['trxamt'] = str(money)
        self.values['reqsn'] = str(reqsn)
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
            if all (k in self.values for k in ('cusid', 'appid', 'reqsn', 'trxamt', 'randomstr', 'sign')):
                return True
            
        return False

    def _post(self):
        ''' 发送post请求获取二维码
        '''
        r = requests.post(_CANCEL_URL, self.values)
        text = json.loads(r.text)
        _log.info('用户发起支付取消请求，请求参数：%s，请求结果：%s' % (self.values, text))
        return text

# if __name__ == "__main__":
#     allinCancel = AllinCancel.DebugAllinCancel().setOldtrxid('111994120000928109')
#     res = allinCancel.cancel('1','201909051005')
#     print(res)