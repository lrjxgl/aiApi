from gtts import gTTS
import os

text = "你好，这是一个使用Python进行文本到语音转换的示例。"
tts = gTTS(text, lang='zh-cn')  # lang参数可以设定为你的语言，例如'en'代表英文

filename = "output.mp3"  # 输出文件的名称
tts.save(filename)  # 保存为mp3文件

# 在默认的浏览器中播放音频文件
os.system(f"start {filename}")