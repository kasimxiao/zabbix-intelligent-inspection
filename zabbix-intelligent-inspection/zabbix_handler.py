import http.cookiejar as cookielib
import json
import boto3
import os
import io
import base64
import sys
import urllib.error
import urllib.parse
import urllib.request
import requests
import configparser
import urllib
import ast
import datetime
from io import BytesIO
from PIL import Image
from claude_handler import getImagesInfo
from config import config


class ZabbixGraph:
    def __init__(self):
        self.zbx_host = config.zabbix_config.get('zbx_config','zbx_host')
        self.zbx_port = config.zabbix_config.get('zbx_config','zbx_port')
        
        self.graphurl = 'http://'+self.zbx_host+':'+self.zbx_port+'/'+'chart2.php'
        self.loginurl = 'http://'+self.zbx_host+':'+self.zbx_port+'/'+'index.php'

        self.username = config.zabbix_config.get('zbx_config','zbx_user')
        self.password = config.zabbix_config.get('zbx_config','zbx_pwd')
        
        self.bucket = config.zabbix_config.get('download_config','bucket')
        self.img_width = config.zabbix_config.get('download_config','imgWidth')
        self.img_height = config.zabbix_config.get('download_config','imgHeight')
        


    def getcookie(self):
        cookiejar = cookielib.CookieJar()
        urlOpener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))
        values = {
            "name": self.username,
            'password': self.password,
            'autologin': 1,
            "enter": 'Sign in'
        }
        data = urllib.parse.urlencode(values).encode(encoding='UTF8')
        request = urllib.request.Request(self.loginurl, data)
        try:
            urlOpener.open(request, timeout=10)
            self.urlOpener = urlOpener
        except urllib.error.HTTPError as e:
            print(e)

    def downGraph(self, hostIP, service, graphName, graphid, time_from, time_to):
        self.getcookie()
        if graphid == 0:
            print("graphid error")
            sys.exit(1)
 
        values = {
            "graphid": graphid,
            "from": time_from,
            "to": time_to,
            "width": self.img_width,
            "height": self.img_height,
            "profileIdx": "web.charts.filter"
        }
        data = urllib.parse.urlencode(values).encode(encoding='UTF8')
        request = urllib.request.Request(self.graphurl, data)
     
        url = self.urlOpener.open(request)
        image = url.read()

        img = Image.open(BytesIO(image))
        return img
        

class zabbixApi(ZabbixGraph):
    def __init__(self):
        super().__init__()
        self.token = None
        self.post_header = {'Content-Type': 'application/json'}
        self.excel_serial = 1
        self.writeToExcelList_warning = []
        
        self.zbx_host = config.zabbix_config.get('zbx_config','zbx_host')
        self.zbx_port = config.zabbix_config.get('zbx_config','zbx_port')
        self.zbx_url = 'http://'+self.zbx_host+':'+self.zbx_port+'/'+'api_jsonrpc.php'
        self.username = config.zabbix_config.get('zbx_config','zbx_user')
        self.password = config.zabbix_config.get('zbx_config','zbx_pwd')

    # 调用zabbix api需要身份令牌auth
    def get_token(self):
        post_data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "username": self.username,
                "password": self.password
            },
            "id": "1"
        }
        ret = requests.post(self.zbx_url, data=json.dumps(post_data), headers=self.post_header)
        zbx_ret = json.loads(ret.text)
        try:
            self.token = zbx_ret.get('result')
        except Exception as e:
            print('''zabbix登录错误，请检查登录信息是否正确!
                     本次登录退出!
                     zbx_url: %s
                     zbx_user: %s
                     zbx_pwd: %s
                     错误信息: %s''' % (self.zbx_url, self.username, self.password, e))

    #接口请求
    def getResponse(self, dataJson):

        resDataJson = requests.post(self.zbx_url, data=json.dumps(dataJson), headers=self.post_header)
        
        try:
            responseData = resDataJson.json()['result']
            return responseData
        except Exception as e:
            print('获取API接口失败！,%s' % e)

    #获取监控视图id
    def getGraphId(self, hostid, graphList):
        # 通过组名取货去到组的ID，返回给下个调用函数
        filterlist = list(graphList.values())
        reqHostJson = {
            "jsonrpc": "2.0",
            "method": "graph.get",
            "params": {
                "output": ["graphid", "name"],
                "hostids": hostid,
                "filter": {
                    "name": filterlist
                }
            },
            "auth": self.token,
            "id": 1
        }
        graphidInfo = self.getResponse(reqHostJson)
        for item in graphidInfo:
            # 获取当前字典的name值
            name = item['name']
            # 在info_dict中查找对应的键
            for key, value in graphList.items():
                if value == name:
                    # 将键值对添加到当前字典中
                    item['type'] = key
                    break
        return graphidInfo

    #获取主机id
    def getHostID(self, ip):
        reqHostJson = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["host"],
                "filter": {
                    "ip": ip
                }
            },
            "auth": self.token,
            "id": 1
        }
        result = self.getResponse(reqHostJson)
        if result:
            return result[0]["hostid"]
        else:
            return ""

    # 从文件读入ip
    def readHostsToGraphListInfoList(self,host):
        ip = host.split('-')[1]
        service = host.split('-')[0]

        graphListInfoList = []        
        #graphlist = ast.literal_eval(self.itemlist)
        graphlist = ast.literal_eval(config.hosts_config.get(service,'itemNameList'))
        hostid = self.getHostID(ip)
        if hostid != "":
            graphListInfoList.append({"hostip": ip, "hostid": hostid,  "service": service,  "itemNameList": graphlist})
        return graphListInfoList
    

    # 下载图片
    def downloadGraphs(self,host):  
        self.get_token()
        
        for graphListInfo in self.readHostsToGraphListInfoList(host):
            zabbix_info = ''
            hostip = graphListInfo['hostip']
            hostid = graphListInfo['hostid']
            service = graphListInfo['service']
            itemNameList = graphListInfo['itemNameList']
            graphInfoList = self.getGraphId(hostid, itemNameList)
            images = []
            for graphInfo in graphInfoList:
                if zabbix_info:
                    zabbix_info = f'{zabbix_info},'
                graphid = graphInfo['graphid']
                name = graphInfo['name'].replace(' ', '_').replace(':', '').replace('/','~')  # 由于监控名称存在特殊符号，这里需要进行处理，不然会报异常
                type = graphInfo['type']

                try:
                    time_from = config.hosts_config.get(service,'timeFrom')
                    time_to = config.hosts_config.get(service,'timeTo')
                except Exception as e:
                    time_from = config.zabbix_config.get('metric_config','timeFrom')
                    time_to = config.zabbix_config.get(service,'timeTo')
                    
                down_image = self.downGraph(hostip, service, name, graphid, time_from, time_to)

                try:
                    rek_prompt = config.hosts_config.get(service,f'{type}_prompt')
                except Exception as e:
                    rek_prompt = "识别监控图中指标，包括监控图名称、指标名称，以及指标的值（last、min、avg、max），以json格式英文输出,需要仔细核对数值，不要出现错行，或者不合理的数值" 
                

                response = getImagesInfo(image_to_base64(down_image),system_prompt,rek_prompt,assistant_content)
                zabbix_info = f'{zabbix_info}{{{response}'

                images.append(down_image)

            
            max_width = max(img.width for img in images)
            total_height = sum(img.height for img in images)
            
            # 创建新图片
            merged_image = Image.new('RGB', (max_width, total_height))
            
            # 粘贴图片
            y_offset = 0
            for img in images:
                merged_image.paste(img, (0, y_offset))
                y_offset += img.height
                            
            img_byte_arr = BytesIO()
            merged_image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            now = datetime.datetime.now()
            formatted_date = now.strftime("%Y%m%d")
            formatted_time = now.strftime("%Y%m%d%H%M%S")
            object_key = 'v2/{}/{}/{}/{}.png'.format(hostip, service, formatted_date, hostip+'-'+service +'-'+ formatted_time)

            #本地存一份
            output_path = f'/tmp/{host}-{formatted_time}.png'  # 指定保存路径和文件名
            # 将字节数据写入文件
            with open(output_path, 'wb') as f:
                f.write(img_byte_arr)
                
            #上传S3
            s3_client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=img_byte_arr)

            return service,zabbix_info,output_path


def image_to_base64(pil_image):
    buffer = io.BytesIO()
    # 将图片保存到字节流缓冲区，格式为PNG
    pil_image.save(buffer, format='PNG')
    # 获取字节流数据
    img_byte = buffer.getvalue()
    # 将字节流数据转换为base64字符串
    # img_base64 = base64.b64encode(img_byte).decode('utf-8')
    # aws bedrock converse 接口图片不用base64
    return img_byte

s3_client = boto3.client('s3')
system_prompt = '你是一个资深运维工程师，对zabbix中的监控视图进行解析'
assistant_content = '{'


