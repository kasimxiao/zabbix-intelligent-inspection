# Zabbix Function Call 模块

这是Zabbix智能巡检系统的Lambda函数调用模块。

## 模块功能

该模块主要负责调用Zabbix智能巡检系统的主Lambda函数，实现以下功能：

1. 定时触发监控任务
2. 支持单主机和多主机巡检
3. 处理Lambda函数的调用参数

## 文件说明

- `lambda_function.py`: Lambda函数入口文件，负责处理事件触发和函数调用

## 使用方法

### 单主机巡检
```python
event = {
    "host": "service-ip"  # 例如: "mysql-10.0.0.1"
}
```

### 多主机巡检
```python
event = {}  # 空事件将触发配置文件中定义的所有主机巡检
```
或者自行实现调用外部的接口，动态的获取主机列表

## 配置要求
- AWS Lambda函数需要配置适当的IAM角色和权限，赋予STS调用zabbix-intelligent-inspection Lambda

## 注意事项
定时触使用EventBridge配置
