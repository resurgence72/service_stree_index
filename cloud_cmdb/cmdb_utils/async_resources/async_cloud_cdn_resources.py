from cloud_cmdb.models import CdnInfo
from cloud_cmdb.common.metrics import monitor
from cloud_cmdb.common.common import get_md5
from cloud_cmdb.cmdb_utils.async_resources.async_cloud_operator import AliOperator
from aliyunsdkcdn.request.v20180510.DescribeUserDomainsRequest import DescribeUserDomainsRequest


class AliCdnOperator(AliOperator):
    resource_type = 'cdn'
    resource_orm = CdnInfo

    def get_cdn_resources(self):
        cdn_list = self.get_resources(
            DescribeUserDomainsRequest,
            ['Domains', 'PageData']
        )
        return cdn_list

    def sync_resources(self):
        print('begin cdn resource scheduler')
        monitor.cloud_cmdb_sync_count.labels(resource_type=self.resource_type).inc(1)
        resources = self.get_cdn_resources()

        monitor.cloud_cmdb_resources_count.labels(resource_type=self.resource_type).set(len(resources))

        bulk_list = []
        for resource in resources:
            source = resource.get('Sources', {}).get('Source', [])
            domain_name = resource.get('DomainName')
            group_id = resource.get('ResourceGroupId')
            instance_id = get_md5(f'{domain_name}|{group_id}')

            resource_map = {
                'instance_id': instance_id,
                'status': resource.get('DomainStatus'),
                'regain': resource.get('RegionId', 'cn-beijing'),
                'ssl_protocol': resource.get('SslProtocol'),
                'coverage': resource.get('Coverage'),
                'desc': resource.get('Description'),
                'cname': resource.get('Cname'),
                'domain_name': domain_name,
                'cdn_type': resource.get('CdnType'),
                'zone_id': resource.get('ZoneId', 'cn-beijing')
            }

            if source:
                source = source[0]
                resource_map['source_type'] = source.get('Type')
                resource_map['source_content'] = source.get('Content')
                resource_map['source_port'] = str(source.get('Port'))

            resource_map['field_md5'] = self.get_resource_md5(resource_map)

            bulk_list.append(CdnInfo(**resource_map))
        self.analysis_resources(bulk_list, CdnInfo)


operator = AliCdnOperator()
