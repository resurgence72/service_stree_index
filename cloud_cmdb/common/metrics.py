from prometheus_client import Gauge, Counter
from prometheus_client.core import CollectorRegistry


class Metrics(object):

    def __init__(self):
        register = CollectorRegistry()

        # 倒排索引相关
        self.inverted_index_refresh_count = Counter(
            'inverted_index_refresh_count',
            'inverted index 刷新次数',
            ['resource_type'],
            registry=register
        )
        self.inverted_index_refresh_duration = Gauge(
            'inverted_index_refresh_duration',
            'inverted index 刷新用时',
            ['resource_type'],
            registry=register
        )
        self.inverted_index_refresh_last_time = Gauge(
            'inverted_index_refresh_last_time',
            'inverted index 上次刷新时间戳',
            ['resource_type'],
            registry=register
        )
        self.inverted_index_change_count = Counter(
            'inverted_index_change_count',
            'inverted index 调整次数',
            ['resource_type'],
            registry=register
        )

        # cloud_cmdb 相关
        self.cloud_cmdb_sync_count = Counter(
            'cloud_cmdb_sync_count',
            'cloud_cmdb 同步次数',
            ['resource_type'],
            registry=register
        )
        self.cloud_cmdb_resources_count = Gauge(
            'cloud_cmdb_resources_count',
            'cloud_cmdb 资源数量',
            ['resource_type'],
            registry=register
        )
        self.cloud_cmdb_resources_action_change = Counter(
            'cloud_cmdb_resources_action_change',
            'cloud_cmdb 增加 删除 修改动作次数',
            ['action', 'resource_type'],
            registry=register
        )

        # 服务树资源统计
        self.cloud_cmdb_resources_regain_count = Gauge(
            'cloud_cmdb_resources_regain_count',
            'cloud_cmdb 根据regain统计资源',
            ['regain', 'resource_type'],
            registry=register
        )

        self.cloud_cmdb_resources_status_count = Gauge(
            'cloud_cmdb_resources_status_count',
            'cloud_cmdb 根据status统计资源',
            ['status', 'resource_type'],
            registry=register
        )

        self.cloud_cmdb_resources_os_type_count = Gauge(
            'cloud_cmdb_resources_os_type_count',
            'cloud_cmdb 根据os_type统计资源',
            ['os_type', 'resource_type'],
            registry=register
        )

        self.cloud_cmdb_resources_gpa = Gauge(
            'cloud_cmdb_resources_gpa',
            'cloud_cmdb 根据regain 统计 gpa 资源',
            ['gpa', 'regain', 'resource_type'],
            registry=register
        )

        self.cloud_cmdb_resources_gpa_special = Gauge(
            'cloud_cmdb_resources_gpa_special',
            'cloud_cmdb 统计 ecs gpa 特殊资源 cpu/mem/disk',
            ['gpa', 'hardware'],
            registry=register
        )

        self.register = register


monitor = Metrics()
