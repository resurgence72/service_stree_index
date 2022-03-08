from .gpa_operator import *
from cloud_cmdb.models import (
    EcsInfo,
    ClbInfo,
    RdsInfo,
    CdnInfo,
    StreePath
)


def mount_gpa(resource_type, mount_ids, gpa_path):
    """
    挂载到具体表中
    :param resource_type:
    :param mount_ids:
    :param gpa_path:
    :return:
    """
    operator = None
    if resource_type == 'ecs':
        operator = EcsInfo
    elif resource_type == 'clb':
        operator = ClbInfo
    elif resource_type == 'rds':
        operator = RdsInfo
    elif resource_type == 'cdn':
        operator = CdnInfo
    else:
        return f'挂载失败, 当前不存在 {resource_type} resource_type'

    # 1. 校验 gpa是否存在
    g, p, a = gpa_path.split('.')
    obj_g = get_g(g)
    if not obj_g:
        return f'g: {g} 不存在'

    obj_p = get_p(obj_g, p)
    if not obj_p:
        return f'p: {p} 不存在'

    obj_a = StreePath.objects.filter(
        level=2,
        node_name=a,
        path=f'{obj_p.path}/{obj_p.pk}'
    )
    if not obj_a:
        return f'a: {a} 不存在'

    # 2. gpa存在，校验ecs是否存在
    from django.forms import model_to_dict
    from cloud_cmdb.signals import try_refresh

    succ_list = []
    refresh_inverted_index_obj = []
    for pk in mount_ids:
        ecs = operator.objects.filter(pk=pk).first()
        if ecs:
            ecs.g, ecs.p, ecs.a = g, p, a
            ecs.save()
            succ_list.append(str(pk))
            refresh_inverted_index_obj.append(ecs)

    if refresh_inverted_index_obj:
        # 如果有数据被挂载，通知信号刷新倒排索引
        # 发送倒排索引信号
        try_refresh.send(
            sender=resource_type,
            operate_type='update',
            operate=[model_to_dict(obj) for obj in refresh_inverted_index_obj]
        )

    return f'{",".join(succ_list)} gpa 已经设置完毕'
