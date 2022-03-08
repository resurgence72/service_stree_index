from cloud_cmdb.models import RdsInfo
from cloud_cmdb.common.metrics import monitor
from cloud_cmdb.cmdb_utils.async_resources.async_cloud_operator import AliOperator
from aliyunsdkrds.request.v20140815.DescribeDBInstancesRequest import DescribeDBInstancesRequest


class AliRdsOperator(AliOperator):
    resource_type = 'rds'
    resource_orm = RdsInfo

    def get_rds_resources(self):
        rds_list = self.get_resources(
            DescribeDBInstancesRequest,
            ['Items', 'DBInstance']
        )
        return rds_list

    def sync_resources(self):
        print('begin rds resource scheduler')
        monitor.cloud_cmdb_sync_count.labels(resource_type=self.resource_type).inc(1)
        resources = self.get_rds_resources()

        monitor.cloud_cmdb_resources_count.labels(resource_type=self.resource_type).set(len(resources))

        bulk_list = []
        for resource in resources:
            resource_map = {
                'instance_id': resource.get('DBInstanceId'),
                'status': resource.get('DBInstanceStatus'),
                'instance_type': resource.get('DBInstanceType'),
                'instance_net_type': resource.get('DBInstanceNetType'),
                'instance_work_type': resource.get('InstanceNetworkType'),
                'regain': resource.get('RegionId'),
                'engine': resource.get('Engine'),
                'engine_version': resource.get('EngineVersion'),
                'zone_id': resource.get('ZoneId'),
                'connection_mode': resource.get('ConnectionMode'),
                'connection_str': resource.get('ConnectionString'),
                'lock_mode': resource.get('LockMode'),
            }
            resource_map['field_md5'] = self.get_resource_md5(resource_map)

            bulk_list.append(RdsInfo(**resource_map))
        self.analysis_resources(bulk_list, RdsInfo)


operator = AliRdsOperator()
