import configparser
from pathlib import Path

class Config:
    def __init__(self):
        self.config_dir = Path(__file__).parent
        self.zabbix_config = self._load_config('zabbix_conf.ini')
        self.hosts_config = self._load_config('hosts_conf.ini')
        
    def _load_config(self, filename):
        config = configparser.ConfigParser()
        config.read(self.config_dir / filename, encoding='utf-8')
        return config
    
    def get_hosts_list(self):
        hosts_string = self.hosts_config.get('hosts', 'hosts_list')
        return [host.strip() for host in hosts_string.split('\n') if host.strip()]
    
    def get_insight_prompt(self, service):
        return self.hosts_config.get(service, 'insight_prompt')
    
    def get_email_config(self):
        return {
            'sender': self.zabbix_config.get('ses', 'sender'),
            'recipients': self.zabbix_config.get('ses', 'recipients'),
            'region': self.zabbix_config.get('ses', 'region')
        }

config = Config()
