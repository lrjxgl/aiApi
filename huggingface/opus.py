from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from fastapi import FastAPI
from typing import Union
app = FastAPI()

tokenizer_zh2en = AutoTokenizer.from_pretrained(
    "G:/model/Helsinki-NLP/opus-mt-zh-en")
model_zh2en = AutoModelForSeq2SeqLM.from_pretrained(
    "G:/model/Helsinki-NLP/opus-mt-zh-en")


def zh2en(text):
    tokenized_text = tokenizer_zh2en([text], return_tensors='pt')
    translation = model_zh2en.generate(**tokenized_text, max_new_tokens=1024)
    return tokenizer_zh2en.batch_decode(translation, skip_special_tokens=True)[0]


tokenizer_en2zh = AutoTokenizer.from_pretrained(
    "G:/model/Helsinki-NLP/opus-mt-en-zh")
model_en2zh = AutoModelForSeq2SeqLM.from_pretrained(
    "G:/model/Helsinki-NLP/opus-mt-en-zh")


def en2zh(text):
    tokenized_text = tokenizer_en2zh([text], return_tensors='pt')
    translation = model_en2zh.generate(**tokenized_text, max_new_tokens=1024)
    return tokenizer_en2zh.batch_decode(translation, skip_special_tokens=True)[0]


@app.get('/')
async def hello_world():

    return 'Hello FastApi!'


@app.get('/zh2en')
async def r_zh2en(text: Union[str, None] = None):
    if text == None:
        text = "我是中国人民的儿子"
    str = zh2en(text)
    return {"error":0,"data":str}


@app.get('/en2zh')
async def r_en2zh(text :Union[str, None] = None):
    if text == None:
        text = "I am a Chinese person"    # 如果没有传递text参数，则使用中文作为内容作为
    str = en2zh(text)
    return {"error":0,"data":str}


 
