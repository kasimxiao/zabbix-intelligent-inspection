import json
import os
from typing import List
import traceback
from zabbix_handler import zabbixApi
from claude_handler import getInfoInsight
from ses_handler import EmailService
from models import HostMonitorData
from config import config

system_prompt = '你是一个资深运维工程师，对zabbix中的监控视图进行分析'
assistant_content = '巡检'

def lambda_handler(event, context):
    hosts_list = []
    if event.get('host'):
        host = event.get('host')
        hosts_list.append(host)
    else:
        # # 获取主机列表
        hosts_string = config.hosts_config.get('hosts', 'hosts_list')
        hosts_list = [host.strip() for host in hosts_string.split('\n') if host.strip()]

    # 收集所有主机的监控数据
    hosts_data = []
    image_list = []
    for host in hosts_list:
        try:
            # 提取监控视图信息并保存图片
            service, zabbix_info, output_path = zabbixApi().downloadGraphs(host)
            image_list.append(output_path)
            # 获取Claude分析见解
            insight_prompt = config.hosts_config.get(service, 'insight_prompt')
            insight_prompt = f'{insight_prompt}\n{zabbix_info}'
            analysis = getInfoInsight(system_prompt, insight_prompt, assistant_content)
            if  '巡检异常' in analysis:
                # 保存主机监控数据
                host_data = HostMonitorData(
                    name=host,
                    service=service,
                    image_path=output_path,
                    analysis=analysis
                )
                hosts_data.append(host_data)
            
        except Exception as e:
            print(f"处理主机 {host} 数据失败: {str(e)}")
            print(f"详细错误信息: {traceback.format_exc()}")
            continue

    if hosts_data:
        # 发送邮件通知
        email_service = EmailService()
        email_service.send_alert_email("ses", hosts_data)

    for i in image_list:
        # 删除lambda本地临时文件
        os.remove(i)

    return {
        'statusCode': 200,
        'body': '作业完成'
    }
    