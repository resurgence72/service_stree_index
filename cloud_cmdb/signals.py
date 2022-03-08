from django.dispatch import Signal
from django.dispatch import receiver
from cloud_cmdb.common.common import get_resource_disallow_labels
from cloud_cmdb.cmdb_utils.async_refresh_inverted_index import (
    add_inverted_index,
    del_inverted_index,
    update_inverted_index
)
from cloud_cmdb.common.metrics import monitor

# 自定义信号
try_refresh = Signal(providing_args=['operate_type', 'operate'])


@receiver(try_refresh)
def my_action(sender, **kwargs):
    # 不同的resource_type 比如ecs/rds
    resource_type = sender
    # action 类型 比如增删改
    operate_type = kwargs.get('operate_type')
    # 具体要操作的对象列表 [dict, dict, dict]
    operate = kwargs.get('operate')

    # 打点
    monitor.cloud_cmdb_resources_action_change.labels(
        action=operate_type,
        resource_type=resource_type,
    ).inc(len(operate))

    if operate_type == 'create':
        # 需要添加倒排索引
        print('信号： create ', len(operate))
        exclude_fields = get_resource_disallow_labels(sender)
        add_inverted_index(resource_type, operate, exclude_fields=exclude_fields)

    elif operate_type == 'delete':
        # 需要删除pk即可
        print('信号： delete ', len(operate))
        del_inverted_index(resource_type, operate)
    elif operate_type == 'update':
        # 先删除再添加
        print('信号： update ', len(operate))
        update_inverted_index(resource_type, operate)


