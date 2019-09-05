import json
import hashlib
import logging
import requests
from .allin_utils import getRandomStr, createSign

_log = logging.getLogger()

# 统一支付接口地址
_PAY_URL = 'https://vsp.allinpay.com/apiweb/unitorder/pay'

class AllinPay(object):

    @staticmethod
    def DebugAllinPay():
        ''' 测试用的支付接口
        '''
        return AllinPay('100581048160005', '990440148166000', '00000003', 'a0ea3fa20dbd7bb4d5abf1d59d63bae8')

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
        self.values['paytype'] = 'A01'
        self.values['validtime'] = '15'
    
    def setPaytype(self, paytype):
        ''' 设置设置支付方式
        :param paytype: https://aipboss.allinpay.com/know/devhelp/main.php?pid=24
        '''
        self.values['paytype'] = paytype
        return self

    def setBody(self, body):
        ''' 订单标题
        '''
        self.values['body'] = body
        return self
    
    def setRemark(self, remark):
        ''' 设置备注信息
        '''
        self.values['remark'] = remark
        return self

    def noCredit(self):
        ''' 指定不能使用信用卡支付
        '''
        self.values['no_credit'] = 'no_credit'
        return self
    
    def setAcct(self, acct):
        ''' 微信支付-用户的微信openid; 支付宝支付-用户user_id; 微信小程序-用户小程序的openid
            小程序支付必填
        '''
        self.values['acct'] = acct
        return self
    
    def setNotifyUrl(self, notifyUrl):
        ''' 交易结果的回调地址
            支付宝支付，小程序支付必填
        '''
        self.values['notify_url'] = notifyUrl
        return self
    
    def setSubAppid(self, subAppid):
        ''' 交易APPID
            小程序支付必填
        '''
        self.values['sub_appid'] = subAppid
        return self

    def pay(self, money, reqsn, **kw):
        ''' 支付
        :param money: 支付金额，单位分
        :param reqsn: 订单号，全局唯一
        :param **kw: 其他支付信息
        '''
        self.values['randomstr'] = getRandomStr()
        self.values['trxamt'] = money
        self.values['reqsn'] = reqsn
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
            if all (k in self.values for k in ('orgid', 'cusid', 'appid', 'reqsn', 'trxamt', 'reqsn', 'paytype', 'randomstr', 'sign')):
                if self.values['paytype'] == 'A01':
                    if 'notify_url' in self.values:
                        return True
                    else:
                        return False
                if self.values['paytype'] == 'W06':
                    if 'acct' in self.values and 'notify_url' in self.values and 'sub_appid' in self.values:
                        return True
                    else:
                        return False
            
        return True

    def _post(self):
        ''' 发送post请求获取二维码
        '''
        r = requests.post(_PAY_URL, self.values)
        text = json.loads(r.text)
        _log.info('用户发起支付请求，请求参数：%s，请求结果：%s' % (self.values, text))
        return text

# if __name__ == "__main__":
#     allinpay = AllinPay.DebugAllinPay().setBody('支付信息').setNotifyUrl('').setRemark('备注信息')
#     res = allinpay.pay('1', '201909050004')
#     print(res)

#     import qrcode
#     img = qrcode.make(res['payinfo'])
#     img.save('D:\\aa.png')
