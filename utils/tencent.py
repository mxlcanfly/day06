from tencentcloud.common import credential
from tencentcloud.sms.v20210111 import sms_client, models


def send_sms(mobile, sms_code):
    mobile = '86{}'.format(mobile)
    try:
        cred = credential.Credential('','')
        client = sms_client.SmsClient(cred, "ap-guangzhou")

        req = models.SendSmsRequest()

        req.SmsSdkAppId = ''
        req.SignName = 'Python之路'
        req.TemplateId = ''
        req.TrmplateParamSet = [mobile, sms_code]
        resp = client.SendSms(req)
        data_dict = resp.SendStatusSet[0]
        if data_dict.Code == 'OK':
            return True
    except Exception as e:
        print(e)