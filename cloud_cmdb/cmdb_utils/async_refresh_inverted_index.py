import time
from json import loads
from cloud_cmdb.common.common import get_resource_disallow_labels
from cloud_cmdb.common.metrics import monitor
from cloud_cmdb.common import rii


def refresh_inverted_index(resource_type, orm_type):
    """
    刷新指定倒排索引
    :param resource_type:
    :param orm_type:
    :return:
    """
    monitor.inverted_index_refresh_count.labels(resource_type=resource_type).inc(1)

    refresh_begin_time = time.time()

    ii = rii.resource_map.get(resource_type)
    ii.reset()

    # 获取不同 resource_type 希望获取的字段
    info_list = orm_type.objects.values(*orm_type.inverted_fields)
    add_inverted_index(resource_type, info_list)

    monitor.inverted_index_refresh_duration.labels(resource_type=resource_type).set(time.time() - refresh_begin_time)
    monitor.inverted_index_refresh_last_time.labels(resource_type=resource_type).set(refresh_begin_time)


def add_inverted_index(resource_type, info_list, exclude_fields=None):
    """
    向指定倒排索引中添加 obj
    :param resource_type:
    :param info_list:
    :param exclude_fields:
    :return:
    """
    ii = rii.resource_map.get(resource_type)
    exclude_fields = exclude_fields or []

    for info in info_list:
        # exclude_fields 不为none说明 dict中需要pop非法labels
        for fields in exclude_fields:
            if fields in info:
                info.pop(fields)

        pk = info.pop('id')

        if 'tags' in info:
            # 此处用来兼容 ecs 的tags 字段
            tags = info.pop('tags')
            if tags:
                info.update(loads(tags))

        monitor.inverted_index_change_count.labels(resource_type=resource_type).inc(1)
        ii.create_invert_index(pk, info)


def del_inverted_index(resource_type, pks):
    """
    在倒排索引中删除obj
    :param resource_type:
    :param pks:
    :return:
    """
    monitor.inverted_index_change_count.labels(resource_type=resource_type).inc(1)
    rii.resource_map.get(resource_type).delete_invert_index(pks)


def update_inverted_index(resource_type, info_list):
    """
     在倒排索引中更新obj
    :param resource_type:
    :param info_list:
    :return:
    """
    del_inverted_index(resource_type, [
        info.get('id')
        for info in info_list
    ])

    exclude_fields = get_resource_disallow_labels(resource_type)
    add_inverted_index(
        resource_type,
        info_list,
        exclude_fields=exclude_fields
    )
