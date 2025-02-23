import json
import boto3
import time

def lambda_handler(event, context):
    lambda_client = boto3.client('lambda')
    function_name = 'arn:aws:lambda:{AWS-REGION}:{AWS-ACCOUNT}:function:zabbix-intelligent-inspection'

    #监控主机
    host_list = ['EC2-10.100.11.89','EC2-10.100.11.89']
    #或者自行调用外部接口动态的获取监控主机

    for host in host_list:
        payload = {
                'host': host
            }
        # 异步调用Lambda函数
        lambda_client.invoke_async(FunctionName=function_name,InvokeArgs=json.dumps(payload))
        # 设置一个等待时间，防止限流
        time.sleep(5)

    return {
        'statusCode': 200,
        'body': '调用完成'
    }
