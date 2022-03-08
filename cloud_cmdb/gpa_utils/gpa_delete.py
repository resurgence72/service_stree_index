from .gpa_operator import *


def delete_gpa(gpa, force=False):
    """
    force 表示是否强制删除
    传入g，如果g下有p就不让删g
    传入g.p，如果p下有a就不让删p
    传入g.p.a，直接删
    :param gpa:
    :param force:
    :return:
    """
    gpa_list = gpa.split('.')
    lens = len(gpa_list)

    msg = ''

    if lens == 1:
        # 传入g，如果g下有p就不让删g
        g = gpa
        msg = delete_by_g(g, force)
    elif lens == 2:
        # 传入g.p，如果p下有a就不让删p
        msg = delete_by_gp(gpa_list, force)
    elif lens == 3:
        msg = delete_by_gpa(gpa_list)
    return msg


def delete_by_g(g, force):
    obj_g = get_g(g)
    if not obj_g:
        return f'g: {g} 不存在'

    has_p = StreePath.objects.filter(
        level=1,
        path=f'/{obj_g.pk}'
    )
    if not has_p:
        # g下没有p 可以删除g
        obj_g.delete()
        return f'g: {obj_g.node_name} 已经删除'

    # g下有p 返回
    if not force:
        return f'g: {obj_g.node_name} 下存在p, 无法删除'

    """
    如果支持强制删除
    - 第一步 删除path 前缀的p和a  del_where="path like '/1/%' and level in(2,3) "
    - 第二步 删除这个g
    """
    StreePath.objects.filter(
        level__in=[1, 2],
        path__startswith=f'/{obj_g.pk}'
    ).delete()
    obj_g.delete()
    return f'g: {obj_g.node_name} 强制删除删除'


def delete_by_gp(gp, force):
    g, p = gp

    obj_g = get_g(g)
    if not obj_g:
        return f'g: {g} 不存在'

    obj_p = get_p(obj_g, p)
    if not obj_p:
        return f'p: {p} 不存在'

    a_list = StreePath.objects.filter(
        level=2,
        path=f'{obj_p.path}/{obj_p.pk}'
    )
    if not a_list:
        # 说明p下无数据，可以删除p
        obj_p.delete()
        return f'p: {p} 删除成功'

    # p 下有数据
    if not force:
        return f'g.p: {g}.{p} 下存在a, 无法删除'

    """
    1. 先删除p下的所有a
    2. 在删除p
    """
    for obj_a in a_list:
        obj_a.delete()
    obj_p.delete()
    return f'g.p: {g}.{p} 强制删除'


def delete_by_gpa(gpa):
    g, p, a = gpa

    obj_g = get_g(g)
    if not obj_g:
        return f'g: {g} 不存在'

    obj_p = get_p(obj_g, p)
    if not obj_p:
        return f'p: {p} 不存在'

    # 直接删除a
    StreePath.objects.filter(
        level=2,
        path=f'{obj_p.path}/{obj_p.pk}',
    ).first().delete()

    return f'a: {a} 删除成功'
