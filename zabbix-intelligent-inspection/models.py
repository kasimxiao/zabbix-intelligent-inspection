from dataclasses import dataclass

@dataclass
class HostMonitorData:
    """主机监控数据模型"""
    name: str
    service: str
    image_path: str
    analysis: str
