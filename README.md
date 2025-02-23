# Zabbix 智能巡检系统

基于AWS Lambda和大语言模型的Zabbix监控数据智能分析系统

## 系统架构

![架构图](image/architecture.png)

## 项目简介

本项目是一个基于AWS Lambda和大语言模型的智能运维解决方案，通过自动化的方式对Zabbix监控系统中的数据进行智能分析和预警。系统能够自动获取Zabbix监控视图，利用大语言模型进行数据理解和分析，从而实现智能化的预警机制。

## 文件结构

```
zabbix-intelligent-inspection/
├── README.md                 # 项目说明文档
├── image/                    # 系统架构图目录
├── zabbix-function-call/     # Lambda函数调用模块
└── zabbix-intelligent-inspection/  # 核心实现目录
    ├── claude_handler.py     # 大语言模型处理
    ├── config.py            # 配置管理
    ├── hosts_conf.ini       # 主机配置
    ├── lambda_function.py   # 主程序入口
    ├── models.py           # 数据模型
    ├── ses_handler.py      # 邮件服务
    ├── zabbix_conf.ini     # Zabbix配置
    ├── zabbix_handler.py   # Zabbix API处理
    └── templates/          # 邮件模板目录
```

## 核心组件功能

### 1. 主程序入口 (lambda_function.py)
- 系统主入口，协调各组件工作
- 处理主机监控数据收集
- 触发智能分析流程
- 处理告警邮件发送

### 2. Zabbix处理模块 (zabbix_handler.py)
- 实现与Zabbix API的交互
- 获取监控数据和图表
- 下载监控图表
- 处理监控数据的格式化

### 3. 大语言模型处理 (claude_handler.py)
- 集成AWS Bedrock的Claude模型
- 提供图像识别功能
- 提供监控数据智能分析
- 使用两个不同的模型：
  - nova-lite-v1用于图像识别
  - nova-pro-v1用于数据分析

### 4. 配置管理
- hosts_conf.ini：主机配置信息
- zabbix_conf.ini：Zabbix服务器配置
- config.py：配置文件加载和处理

### 5. 邮件通知 (ses_handler.py)
- 使用AWS SES服务
- 发送告警邮件
- 使用HTML模板格式化邮件内容

## 工作流程

1. Lambda函数触发后，从配置文件获取需要监控的主机列表
2. 对每个主机：
   - 通过Zabbix API获取监控数据和图表
   - 使用Claude模型分析监控图表
   - 生成智能分析报告
3. 如果发现异常：
   - 收集异常信息
   - 通过SES发送告警邮件
4. 清理临时文件并完成执行

## 系统特点

- 基于AWS Lambda的无服务器架构
- 集成Claude大语言模型进行智能分析
- 自动化的监控和告警流程
- 支持多主机监控管理
- 灵活的配置管理系统
- 图表识别和数据分析能力
- 基于AWS SES的邮件通知机制
