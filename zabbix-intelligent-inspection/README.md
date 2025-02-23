# Zabbix Intelligent Inspection 核心模块

这是Zabbix智能巡检系统的核心实现模块。

## 文件结构

```
zabbix-intelligent-inspection/  # 核心实现目录
├── claude_handler.py    # 大语言模型处理
├── config.py            # 配置管理
├── hosts_conf.ini       # 主机配置
├── lambda_function.py   # 主程序入口
├── models.py            # 数据模型
├── ses_handler.py       # 邮件服务
├── zabbix_conf.ini      # Zabbix配置
├── zabbix_handler.py    # Zabbix API处理
└── templates/           # 邮件模板目录
```

## 模块组件

### 1. 大语言模型处理 (claude_handler.py)
- 集成AWS Bedrock服务，进行图像识别和数据分析
- 使用Converse接口，可以基于需求灵活切换不同模型

### 2. 配置管理 (config.py)
- 加载并解析配置文件
- 管理系统配置参数
- 支持的配置文件：
  - hosts_conf.ini：主机监控配置
  - zabbix_conf.ini：Zabbix服务器配置

### 3. Zabbix接口 (zabbix_handler.py)
- Zabbix API封装
- 监控数据获取
- 图表下载和处理
- 数据格式化

### 4. 邮件服务 (ses_handler.py)
- AWS SES服务集成
- 邮件模板渲染
- 告警通知发送

### 5. 主程序入口 (lambda_function.py)
- 系统主入口，协调各组件工作
- 处理主机监控数据收集
- 触发智能分析流程
- 处理告警邮件发送

## 使用方法
配置文件设置
- hosts_conf.ini
   - - hosts，如果监控主机数量并不大，可以直接在该配置中的hosts_list；如果监控主机数量比较大，或需要通过额外接口获取主机list，可以在zabbix-function-call中实现，然后使用异步的方式调用该Lambda
   - - 主机类别，基于传入的hosts_list配置主机类别，和对应的zabbix指标视图名称、指标时间段、指标数据提取prompt、汇总后获取指标见解prompt


## 配置要求
- AWS Lambda函数需要配置适当的IAM角色和权限，需要S3、SES、Bedrock相关权限
- 需要设置正确的环境变量和超时时间

