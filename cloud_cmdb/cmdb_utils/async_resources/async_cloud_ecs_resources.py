import json
from .async_cloud_operator import AliOperator
from cloud_cmdb.models import EcsInfo
from cloud_cmdb.common.metrics import monitor
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest


class AliEcsOperator(AliOperator):
    resource_type = 'ecs'
    resource_orm = EcsInfo

    def get_ecs_resources(self):
        ecs_list = self.get_resources(
            DescribeInstancesRequest,
            ['Instances', 'Instance']
        )
        return ecs_list

    def sync_resources(self):
        print('begin ecs resource scheduler')
        monitor.cloud_cmdb_sync_count.labels(resource_type=self.resource_type).inc(1)
        resources = self.get_ecs_resources()

        monitor.cloud_cmdb_resources_count.labels(resource_type=self.resource_type).set(len(resources))

        bulk_list = []
        for resource in resources:
            resource_map = {
                'instance_id': resource.get('InstanceId'),
                'hostname': resource.get('HostName'),
                'vpc_addr': resource.get('VpcAttributes').get('PrivateIpAddress').get('IpAddress')[0],
                'status': resource.get('Status'),
                'regain': resource.get('RegionId'),
                'zone_id': resource.get('ZoneId'),
                'cpu_core': resource.get('Cpu'),
                'mem_size': int(resource.get('Memory') / 1024),
                'disk_size': 500,
                'os_type': resource.get('OSType'),
                'desc': resource.get('Description'),
            }

            source_tag = resource.get('Tags')
            if source_tag:
                tag_map = {
                    tag_KV.get('TagKey'): tag_KV.get('TagValue')
                    for tag_KV in source_tag.get('Tag')
                }
                serialize_data = json.dumps(tag_map)
                resource_map['tags'] = serialize_data
            resource_map['field_md5'] = self.get_resource_md5(resource_map)

            # bulk_list.append(resource_map)
            bulk_list.append(EcsInfo(**resource_map))

        self.analysis_resources(bulk_list, EcsInfo)


operator = AliEcsOperator()
