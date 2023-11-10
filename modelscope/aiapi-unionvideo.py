import time
import requests
from urllib import request
from io import BytesIO
import base64
import os
import platform
import taskcheck
import serviceConf
#model
import cv2
from moviepy.editor import *
#接口
queueKey="aiapi_unionvideo_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_unionvideo&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
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
        apiTime=serviceConf.apiTime();
        apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
        url = apiurl + '&a=get&apiTime='+apiTime+"&apiAccess="+apiAccess
        response = requests.get(url, timeout=30)
         
        res = response.json()
        print(res)
        if res["error"] == 1:
            print("unionvideo还没任务")
            time.sleep(3)
            os.system(clear_command)

        else:
            
            task = res["data"]
            a=1
            if  a==1:
                videoList =task["videoList"]
                video_files=[]
                audioList=task["audioList"]
                audioClips=[]
                try:
                    i=0
                    for v in videoList:
                        file="./static/unionvideo"+str(i)+".mp4"
                        request.urlretrieve( v,file)
                        video_files.append(VideoFileClip(file))
                        i=i+1
                    i=0
                    for v in audioList:
                        file="static/unionvideo"+str(i)+".mp3"
                        request.urlretrieve( v,file)
                        audioClips.append(AudioFileClip(file))
                        i=i+1
                    mp4url = './static/unionvideo.mp4'
                    mp4url2 = './static/unionvideo_audio.mp4'
                    # 创建一个视频读取器对象

                    final_clip = concatenate_videoclips(video_files)
                    # 保存合并后的视频文件
                    final_clip.write_videofile(mp4url) 
                    # 合成语音
                    video_clip = VideoFileClip(mp4url)
                    concatenated_audio = concatenate_audioclips(audioClips)
                    final_clip = video_clip.set_audio(concatenated_audio)
                    final_clip.write_videofile(mp4url2) 


                    ##发布回复

                    rdata = task
                    with open(mp4url2,'rb') as f:
                        con=f.read()
                        rdata["base64"]=base64.b64encode(con).decode('utf-8')


                    apiTime=serviceConf.apiTime();
                    apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
                    url = apiurl + '&a=finish&apiTime='+apiTime+"&apiAccess="+apiAccess

                    response = requests.post(url, data=rdata)
                    print("生成成功")
                except:
                    print('运行Bug')

                
            else:    
                print("视频合成出错了")
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(1)
