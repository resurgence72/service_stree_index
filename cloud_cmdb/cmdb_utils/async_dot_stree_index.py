from cloud_cmdb.common.metrics import monitor
from cloud_cmdb.gpa_utils.gpa_query import get_gpa
from cloud_cmdb.common.common import special_labels, get_gpa_tup
from cloud_cmdb.common import rii


def dot_resources_by_regain(resource_type, ii):
    """
    统计 resource region分布
    :param resource_type:
    :param ii:
    :return:
    """
    regain_map = ii.get_labels_values('regain') or {}
    for regain, pks in regain_map.items():
        monitor.cloud_cmdb_resources_regain_count.labels(
            regain=regain,
            resource_type=resource_type
        ).set(len(pks))


def dot_resources_by_status(resource_type, ii):
    """
    统计 resource status 分布
    :param resource_type:
    :param ii:
    :return:
    """
    status_map = ii.get_labels_values('status') or {}
    for status, pks in status_map.items():
        monitor.cloud_cmdb_resources_status_count.labels(
            status=status,
            resource_type=resource_type
        ).set(len(pks))


def dot_resources_by_ecs_os_type(resource_type, ii):
    """
    根据ecs 统计 os_type 分布
    :param resource_type:
    :param ii:
    :return:
    """
    os_type_map = ii.get_labels_values('os_type') or {}
    for os_type, pks in os_type_map.items():
        monitor.cloud_cmdb_resources_os_type_count.labels(
            os_type=os_type,
            resource_type=resource_type
        ).set(len(pks))


def dot_resources_by_gpa_special(resource_type, ii):
    """
    统计 ecs 按照 cpu/meme/disk
    :param resource_type:
    :param ii:
    :return:
    """
    if resource_type not in ('ecs',):
        # 只有 ecs 资源才可以统计特殊 cpu/mem/disk
        return
    for sl in special_labels:
        for gpa in get_gpa():
            gpa_tup = get_gpa_tup(gpa)
            search, gpa_name = [], []
            for i in range(3):
                gpa_name.append(gpa_tup[i][1])
                search.append({'type': 0, 'key': gpa_tup[i][0], 'value': gpa_tup[i][1]})

                total_count_map = ii.find_match_sums_by_labels(search, target_label=sl)
                sl_count = total_count_map.get('total_count')
                monitor.cloud_cmdb_resources_gpa_special.labels(
                    gpa='.'.join(gpa_name),
                    hardware=sl
                ).set(sl_count)


def dot_resources_by_gpa(resource_type, ii):
    """
    根据 resource_type 统计各 region 的gpa 数量分布分布
    :param resource_type:
    :param ii:
    :return:
    """
    for gpa in get_gpa():
        gpa_tup = get_gpa_tup(gpa)

        search, gpa_name = [], []
        for i in range(3):
            gpa_name.append(gpa_tup[i][1])
            search.append({'type': 0, 'key': gpa_tup[i][0], 'value': gpa_tup[i][1]})

            lb_list = ii.find_match_pks_by_labels(search, target_label='regain')
            for lb in lb_list:
                regain = lb.get('label')
                count = lb.get('count')
                monitor.cloud_cmdb_resources_gpa.labels(
                    regain=regain,
                    gpa='.'.join(gpa_name),
                    resource_type=resource_type
                ).set(count)


__all__ = [
    dot_resources_by_regain,
    dot_resources_by_status,
    dot_resources_by_ecs_os_type, dot_resources_by_gpa,
    dot_resources_by_gpa_special
]


def dot_cloud_cmdb_resources():
    for dot_func in __all__:
        for resource_type, ii in rii.resource_map.items():
            dot_func(resource_type, ii)
