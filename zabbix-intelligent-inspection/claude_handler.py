import json
import boto3
from datetime import datetime
import string
import base64
from botocore.exceptions import ClientError
import os.path
import configparser

#claude请求
def run_multi_modal_prompt(bedrock_client, system, messages, model_id):
    inf_params = {"maxTokens": max_tokens, "topP": top_p, "temperature": temperature}
    additionalModelRequestFields = {
    "inferenceConfig": {
         "topK": top_k
        }
    }
    
    response = bedrock_client.converse(
        modelId=model_id, 
        messages=messages, 
        system=system, 
        inferenceConfig=inf_params
    )

    return response

#识别图片信息
def getImagesInfo(content_image,system_prompt,user_prompt,assistant_content):
    messages = [{
        "role": "user",
        "content": [
            {
                "image":{
                    "format": "png",
                    "source":{
                        "bytes":content_image
                        }
                }
            },
            {
                "text": user_prompt
            }
            ]
        },
        {
        "role": "assistant",
        "content":[
            {
                "text": assistant_content
            }
            ]
        }]
        
    system = [{ "text": system_prompt}]
 
    response = run_multi_modal_prompt(bedrock_client, system, messages, img_model_id)
    print('getImagesInfo')
    print(response["usage"]["inputTokens"],response["usage"]["outputTokens"])
    # print(response["output"]["message"]["content"][0]["text"])
    return response["output"]["message"]["content"][0]["text"]

#获取信息见解
def getInfoInsight(system_prompt,user_prompt,assistant_content):
    messages = [{
        "role": "user",
        "content": [
            {
                "text": user_prompt
            }
            ]
        },
        {
        "role": "assistant",
        "content":[
            {
                "text": assistant_content
            }
            ]
        }]
        
    system = [{ "text": system_prompt}]

    response = run_multi_modal_prompt(bedrock_client, system, messages, txt_model_id)
    print('getInfoInsight')
    print(response["usage"]["inputTokens"],response["usage"]["outputTokens"])
    return f'巡检{response["output"]["message"]["content"][0]["text"]}'


bedrock_client = boto3.client(service_name='bedrock-runtime',region_name='us-west-2')
temperature = 0.1
top_k = 20
top_p = 0.1
max_tokens = 4096
txt_model_id = 'us.amazon.nova-pro-v1:0'
# txt_model_id = 'us.anthropic.claude-3-5-sonnet-20241022-v2:0'
img_model_id = 'us.amazon.nova-lite-v1:0'
# img_model_id = 'us.anthropic.claude-3-5-sonnet-20241022-v2:0'