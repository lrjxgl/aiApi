import datetime
import hashlib
serviceId="10000002"
serviceToken="0e34e7713bb5721bd34dd2bc886f1788"
apiHost="http://api.huiwanai.com"
def apiTime():
    gmt_time=datetime.datetime.utcnow()
    return gmt_time.strftime("%Y-%m-%d %H:%M:%S")
def md5_encrypt(text):
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    encrypted_text = md5.hexdigest()
    return encrypted_text
def serviceAccess(serviceToken,apiTime):
    return md5_encrypt(serviceToken+apiTime)