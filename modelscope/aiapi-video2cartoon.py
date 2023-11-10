import time
import requests
from io import BytesIO
import base64
import os
import platform
import taskcheck
import serviceConf
#model
import imageio
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from tqdm import tqdm
import numpy as np
from moviepy.editor import *
from urllib import request
model='damo/cv_unet_person-image-cartoon_compound-models'
#model='damo/cv_unet_person-image-cartoon-3d_compound-models'

img_cartoon = pipeline(Tasks.image_portrait_stylization,model=model)

#接口
queueKey="aiapi_video2cartoon_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_video2cartoon&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
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
            a=1
            if  a==1:
                print("开始视频任务")
                omp4url=task["omp4url"]
                filepath='./static/video2cartoon/input.mp4'
                outpath = './static/video2cartoon/output.mp4'
                request.urlretrieve(omp4url, filepath)
                inputmp3='./static/video2cartoon/input.mp3'
                #提取音频
                video = VideoFileClip(filepath)
                audio = video.audio
                audio.write_audiofile(inputmp3)

                #生成视频 
                reader = imageio.get_reader(filepath)
                fps = reader.get_meta_data()['fps']
                writer = imageio.get_writer(outpath, mode='I', fps=fps, codec='libx264')

                for _, img in tqdm(enumerate(reader)):
                    result = img_cartoon(img[..., ::-1])
                    res = result[OutputKeys.OUTPUT_IMG]
                    writer.append_data(res[..., ::-1].astype(np.uint8))
                writer.close()
                #合并音频视频
                # 加载视频和音频文件
                video = VideoFileClip(outpath)
                audio = AudioFileClip(inputmp3)

                # 确保音频和视频的持续时间匹配
                audio = audio.set_duration(video.duration)

                # 将音频添加到视频中
                video = video.set_audio(audio)

                # 输出合成的视频文件
                mp4url='./static/video2cartoon/mp4url.mp4'
                video.write_videofile(mp4url)
                                #视频完成
                rdata = task
                with open(mp4url,'rb') as f:
                    con=f.read()
                    rdata["base64"]=base64.b64encode(con).decode('utf-8')
                            
                ##发布回复
                apiTime=serviceConf.apiTime();
                apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
                url = apiurl + '&a=finish&apiTime='+apiTime+"&apiAccess="+apiAccess
                taskcheck.removeTask();
                print("视频生成成功，反馈finish")
                response = requests.post(url, data=rdata)

                print("视频任务完成")
            else:    
                taskcheck.removeTask();
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        taskcheck.removeTask();
        time.sleep(5)
