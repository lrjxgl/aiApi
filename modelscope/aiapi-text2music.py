import time
import requests
from io import BytesIO
import base64
import os
import platform
import taskcheck
import serviceConf
#model
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from audiocraft.data.audio import audio_write
import scipy
model_id = 'AI-ModelScope/musicgen-large'
pipe = pipeline(task=Tasks.text_to_speech, model=model_id, model_revision='v1.0.4')
#接口
queueKey="aiapi_text2music_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_text2music&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'
#载入模型

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
        response = requests.get(url, timeout=30)
         
        res = response.json()
        print(res)
        if res["error"] == 1:
            print("还没任务")
            taskcheck.removeTask();
            time.sleep(5)

        else:
           
            task = res["data"]
            a=1;
            if  a==1:
                output = pipe(input=task["prompt_en"], duration=16, sep=",")
                output_dict = output[OutputKeys.OUTPUT_WAV]
                wav = output_dict["wav"]
                sample_rate = output_dict["sample_rate"]
                mp3url = './static/text2music.wav'
 
                for idx, one_wav in enumerate(wav):
                    audio_write(f'./static/text2music', one_wav.cpu(), sample_rate, strategy="loudness")
                    break;
                
                rdata = task
                with open(mp3url,'rb') as f:
                    con=f.read()
                    rdata["base64"]=base64.b64encode(con).decode('utf-8')
                            
                ##发布回复
                apiTime=serviceConf.apiTime();
                apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
                url = apiurl + '&a=finish&apiTime='+apiTime+"&apiAccess="+apiAccess
                taskcheck.removeTask();
                response = requests.post(url, data=rdata)

                print("生成成功")
            else:    
                taskcheck.removeTask();
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        taskcheck.removeTask();
        time.sleep(5)
