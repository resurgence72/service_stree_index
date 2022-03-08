from ..models import StreePath


def gpa_add(gpa_list):
    """
    插入幂等 因为使用了 get_or_create 方法，如果存在会get
    :param gpa_list:
    :return:
    """
    from collections import defaultdict
    resp = defaultdict(list)

    # 要求新增的是gpa三段式
    for gpa in gpa_list:
        if len(gpa.split('.')) != 3:
            # 检测是否合规三段式
            print('gpa 不是三段式： ', gpa)
            resp['gpa_failed'].append(gpa)
            continue

        g, p, a = gpa.split('.')

        # 查g
        obj_g = gpa_check_g(g)
        # 查p
        obj_p = gpa_check_p(obj_g, p)
        # 查a
        _ = gpa_check_a(obj_p, a)
        resp['gpa_succ'].append(gpa)
    return resp


def gpa_check_g(g):
    # 如果没有g 插入g 返回g
    # 如果有g 返回g
    obj_g, _ = StreePath.objects.get_or_create(
        level=0,
        node_name=g,
        path='0'
    )
    return obj_g


def gpa_check_p(g, p):
    # 如果有p 获取p
    # 如果没有p 插入p /g.id 获取p
    obj_p, _ = StreePath.objects.get_or_create(
        level=1,
        node_name=p,
        path=f'/{g.pk}'
    )
    return obj_p


def gpa_check_a(p, a):
    # 如果有a 获取a
    # 如果没有a 插入a /g.pk/p.pk 获取p
    obj_a, _ = StreePath.objects.get_or_create(
        level=2,
        node_name=a,
        path=f'{p.path}/{p.pk}'
    )
    return obj_a
