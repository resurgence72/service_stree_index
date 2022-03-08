import json
from cloud_cmdb.models import VpcInfo
from cloud_cmdb.common.metrics import monitor
from cloud_cmdb.cmdb_utils.async_resources.async_cloud_operator import AliOperator
from aliyunsdkvpc.request.v20160428.DescribeVpcsRequest import DescribeVpcsRequest


class AliVpcOperator(AliOperator):
    resource_type = 'vpc'
    resource_orm = VpcInfo

    def get_vpc_resources(self):
        vpc_list = self.get_resources(
            DescribeVpcsRequest,
            ['Vpcs', 'Vpc']
        )
        return vpc_list

    def sync_resources(self):
        print('begin vpc resource scheduler')
        monitor.cloud_cmdb_sync_count.labels(resource_type=self.resource_type).inc(1)
        resources = self.get_vpc_resources()

        monitor.cloud_cmdb_resources_count.labels(resource_type=self.resource_type).set(len(resources))

        bulk_list = []
        for resource in resources:
            resource_map = {
                'instance_id': resource.get('VpcId'),
                'status': resource.get('Status'),
                'regain': resource.get('RegionId'),
                'zone_id': resource.get('ZoneId', 'cn-beijing'),
                'vpc_name': resource.get('VpcName'),
                'desc': resource.get('Description'),
                'owner_id': str(resource.get('OwnerId')),
                'cidr_block': resource.get('CidrBlock')
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

            bulk_list.append(VpcInfo(**resource_map))
        self.analysis_resources(bulk_list, VpcInfo)


operator = AliVpcOperator()
