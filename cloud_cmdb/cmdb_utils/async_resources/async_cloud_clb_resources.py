import json
from cloud_cmdb.models import ClbInfo
from cloud_cmdb.common.metrics import monitor
from cloud_cmdb.cmdb_utils.async_resources.async_cloud_operator import AliOperator
from aliyunsdkslb.request.v20140515.DescribeLoadBalancersRequest import DescribeLoadBalancersRequest


class AliClbOperator(AliOperator):
    resource_type = 'clb'
    resource_orm = ClbInfo

    def get_clb_resources(self):
        clb_list = self.get_resources(
            DescribeLoadBalancersRequest,
            ['LoadBalancers', 'LoadBalancer']
        )
        return clb_list

    def sync_resources(self):
        print('begin clb resource scheduler')
        monitor.cloud_cmdb_sync_count.labels(resource_type=self.resource_type).inc(1)
        resources = self.get_clb_resources()

        monitor.cloud_cmdb_resources_count.labels(resource_type=self.resource_type).set(len(resources))

        bulk_list = []
        for resource in resources:
            resource_map = {
                'instance_id': resource.get('LoadBalancerId'),
                'status': resource.get('LoadBalancerStatus'),
                'regain': resource.get('RegionId'),
                'zone_id': resource.get('MasterZoneId'),
                'clb_name': resource.get('LoadBalancerName'),
                'ip_version': resource.get('AddressIPVersion'),
                'network_type': resource.get('NetworkType'),
                'band_with': resource.get('Bandwidth'),
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

            bulk_list.append(ClbInfo(**resource_map))
        self.analysis_resources(bulk_list, ClbInfo)


operator = AliClbOperator()
