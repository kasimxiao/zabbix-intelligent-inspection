import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import boto3
from datetime import datetime
from typing import List
from models import HostMonitorData
from config import config


class EmailService:
    def __init__(self):
        self.ses_client = boto3.client('ses')
        
    def _read_template(self) -> str:
        """读取HTML模板文件"""
        try:
            template_path = os.path.join(os.path.dirname(__file__), 'templates/email_template.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取邮件模板失败: {str(e)}")
            raise e
            
    def _generate_host_section(self, host: HostMonitorData, image_id: str) -> str:
        """生成单个主机的HTML部分"""
        return f"""
        <div style="margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px;">
            <div style="font-size: 18px; color: #444; margin-bottom: 15px; font-weight: bold;">主机: {host.name}</div>
            <div style="margin: 20px 0; text-align: center;">
                <img src="cid:{image_id}" style="max-width: 100%; height: auto; border: 1px solid #eee; border-radius: 4px;">
            </div>
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 10px; border-left: 4px solid #007bff;">
                <h3 style="margin-top: 0;">异常分析:</h3>
                <p style="margin-bottom: 0;white-space: pre-wrap;">{host.analysis}</p>
            </div>
        </div>
        """
            
    def send_alert_email(self, task_name: str, hosts_data: List[HostMonitorData]):
        try:
            # 获取邮件配置
            email_config = config.get_email_config()
            msg = MIMEMultipart('mixed')
            msg['Subject'] = f"Zabbix监控异常提醒 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            msg['From'] = email_config['sender']
            
            # 处理收件人
            recipients = email_config.get('recipients', [])
            if isinstance(recipients, str):
                recipients = [recipients]
            msg['To'] = ', '.join(recipients)
            
            # 读取模板并准备数据
            template = self._read_template()
            host_sections = []
            
            for idx, host in enumerate(hosts_data):
                try:
                    # 处理图片附件
                    image_id = f'host_image_{idx}'
                    with open(host.image_path, 'rb') as f:
                        img = MIMEImage(f.read())
                        img.add_header('Content-ID', f'<{image_id}>')
                        msg.attach(img)
                    
                    # 生成主机部分的HTML
                    host_sections.append(self._generate_host_section(host, image_id))
                except Exception as e:
                    print(f"处理主机 {host.name} 数据失败: {str(e)}")
                    continue

            # 生成完整的HTML内容
            html_content = template.format(
                datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                host_sections='\n'.join(host_sections)
            )
            
            # 创建HTML部分
            html_part = MIMEText(html_content.encode('utf-8'), 'html', 'utf-8')
            msg_alt = MIMEMultipart('alternative')
            msg_alt.attach(html_part)
            msg.attach(msg_alt)
            
            # 发送邮件
            response = self.ses_client.send_raw_email(
                Source=email_config['sender'],
                Destinations=recipients,
                RawMessage={'Data': msg.as_string()}
            )
            return response
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
            raise e
