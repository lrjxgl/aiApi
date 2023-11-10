import torch.cuda as cuda
import requests
import time
from modelscope.utils.constant import Tasks
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
#from modelscope.pipelines import pipeline
#from diffusers import StableDiffusionXLPipeline
import torch
import cv2
from PIL import Image
import base64
from io import BytesIO
import os
import platform
import taskcheck
import serviceConf
os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'
 
queueKey="aiapi_imgscale_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_imgscale&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
#pipe

pipe = pipeline(Tasks.image_super_resolution, model='damo/cv_rrdb_image-super-resolution')
while True:
    try:
        t=taskcheck.canTask()
        if t==False:
            print('执行其它任务');
            time.sleep(1)
            continue;
        taskcheck.addTask()    
        apiTime=serviceConf.apiTime();
        apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
        url = apiurl + '&a=get&apiTime='+apiTime+"&apiAccess="+apiAccess
        response = requests.get(url, timeout=5)
        res = response.json()
        if res["error"] == 1:
            print("imgscale还没任务")
            taskcheck.removeTask();
            time.sleep(3)
            os.system(clear_command)

        else:
            
            task = res["data"]                        
            imgurl=task["imgurl"]                   
            result = pipe(imgurl)
            #解除cuda占用
            cuda.empty_cache()
            t = time.time()
            f="./static/imgscale.png" 
            cv2.imwrite(f, result[OutputKeys.OUTPUT_IMG])
            with open(f,'rb') as f:
                con=f.read()
                image64=base64.b64encode(con).decode('utf-8')
           
            apiTime=serviceConf.apiTime();
            apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
            url = apiurl + '&a=finish&apiTime='+apiTime+"&apiAccess="+apiAccess
            rdata = task
            rdata["base64"] = image64
            taskcheck.removeTask();
            response = requests.post(url, data=rdata)
            print("生成成功")
            time.sleep(3)
            os.system(clear_command)
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        taskcheck.removeTask();
        time.sleep(1)
