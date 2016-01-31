# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from . import security

_SERVICE = 'mobile.securitypay.pay'
_CHARSET = 'utf-8'
_SIGN_TYPE = 'RSA'
_PAYMENT_TYPE = '1'

class AliPayOrder(models.Model):
    out_trade_no = models.CharField(verbose_name=u'商户订单号', max_length=32, db_index=True, editable=False)
    subject = models.CharField(verbose_name=u'商品名称', max_length=128, editable=False)
    body = models.CharField(verbose_name=u'商品详情', max_length=512, editable=False)
    total_fee = models.DecimalField(verbose_name=u'总金额(单位:元)', max_digits=6, decimal_places=2, editable=False)
    it_b_pay = models.CharField(verbose_name=u'交易结束时间(yyyy-mm-dd HH:mm:ss)', max_length=19, editable=False)
    
    class Meta:
        verbose_name = u'支付宝订单'
        verbose_name_plural = u'支付宝订单'
        
    def __str__(self):
        return self.out_trade_no
        
    def _get_vlaue_dict(self):
        fieldsList = AliPayOrder._meta.get_fields()
        return {item.attname:getattr(self, item.attname) 
                for item in fieldsList 
                if not item.auto_created and getattr(self, item.attname)}
    
    def sign(self):
        # sign data
        data = self._compose_data()
        return '{}&sign_type="RSA"&sign="{}"'.format(data, security.sign(data))
    
    def _compose_data(self):
        valueDict = self._get_vlaue_dict()
        valueDict['service'] = _SERVICE
        valueDict['_input_charset'] = _CHARSET
        valueDict['payment_type'] = _PAYMENT_TYPE
        valueDict['partner'] = settings.ALIPAY['partner']
        valueDict['seller_id'] = settings.ALIPAY['seller_id']
        valueDict['notify_url'] = settings.ALIPAY['notify_url']
        
        temp = []
        for key in valueDict:
            if not valueDict[key]:
                continue
            temp.append('{}="{}"'.format(key, valueDict[key]))
        tempStr = '&'.join(temp)
        return tempStr
    
class AliPayResult(models.Model):
    order = models.OneToOneField(AliPayOrder,
                                 on_delete=models.CASCADE,
                                 primary_key=True,
                                 editable=False,
                                 related_name='pay_result')
    notify_time = models.CharField(verbose_name=u'通知时间', null=True, blank=True, max_length=19, editable=False)
    notify_type = models.CharField(verbose_name=u'通知类型', null=True, blank=True, max_length=50, editable=False)
    notify_id = models.CharField(verbose_name=u'通知校验ID', null=True, blank=True, max_length=50, editable=False)
    out_trade_no = models.CharField(verbose_name=u'商户订单号', null=True, blank=True, max_length=32, editable=False)
    subject = models.CharField(verbose_name=u'商品名称', null=True, blank=True, max_length=128, editable=False)
    trade_no = models.CharField(verbose_name=u'支付宝交易号', null=True, blank=True, max_length=64, editable=False)
    trade_status = models.CharField(verbose_name=u'交易状态', null=True, blank=True, max_length=16, editable=False)
    seller_id = models.CharField(verbose_name=u'卖家支付宝用户号', null=True, blank=True, max_length=30, editable=False)
    seller_email = models.CharField(verbose_name=u'卖家支付宝账号', null=True, blank=True, max_length=100, editable=False)
    buyer_id = models.CharField(verbose_name=u'买家支付宝用户号', null=True, blank=True, max_length=30, editable=False)
    buyer_email = models.CharField(verbose_name=u'买家支付宝账号  ', null=True, blank=True, max_length=100, editable=False)
    total_fee = models.DecimalField(verbose_name=u'总金额(单位:元)', null=True, blank=True, max_digits=6, decimal_places=2, editable=False)
    
    
    def __str__(self):
        fieldsList = AliPayResult._meta.get_fields()
        temp = []
        for field in fieldsList:
            if not field.auto_created:
                temp.append('{}:{}'.format(field.verbose_name, getattr(self, field.attname)))
        return ','.join(temp) 
        
