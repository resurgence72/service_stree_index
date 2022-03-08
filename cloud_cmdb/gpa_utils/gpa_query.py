from .gpa_operator import *

query_type_map = {
    'g_get_p': 1,
    'g_get_gpa': 2,
    'gp_get_gpa': 3,
    'get_gpa': 4,
}


def get_gpa():
    all_gpa = StreePath.objects.all()
    g_map = {}
    p_map = {}
    a_map = {}

    for gpa in all_gpa:
        tmp_map = {}
        if gpa.level == 0:
            tmp_map = g_map
        elif gpa.level == 1:
            tmp_map = p_map
        elif gpa.level == 2:
            tmp_map = a_map
        tmp_map[gpa.pk] = gpa

    gpa_list = []
    for _, a in a_map.items():
        # a /a/b 所属的p p_pk=b ; p /b  所属的g g_pk=b
        _, g_pk, p_pk = a.path.split('/')
        g_pk, p_pk = int(g_pk), int(p_pk)

        gpa_list.append('{}.{}.{}'.format(
            g_map.get(g_pk).node_name,
            p_map.get(p_pk).node_name,
            a.node_name
        ))

    return gpa_list


def g_get_p(g):
    tmp = []
    # 根据g查询 所有p的列表 node=g  query_type=1
    obj_g = get_g(g)

    if not obj_g:
        return tmp

    p_list = StreePath.objects.filter(
        level=1,
        path=f'/{obj_g.pk}'
    )
    for p in p_list:
        tmp.append(p.node_name)
    return tmp


def g_get_gpa(g):
    # 根据g查询 所有g.p.a的列表 node=g   query_type=2
    tmp = []
    obj_g = get_g(g)

    if not obj_g:
        return tmp

    p_list = StreePath.objects.filter(
        level=1,
        path=f'/{obj_g.pk}'
    )

    if not p_list:
        return tmp

    for obj_p in p_list:
        a_list = StreePath.objects.filter(
            level=2,
            path=f'{obj_p.path}/{obj_p.pk}'
        )

        if not a_list:
            return tmp
        for obj_a in a_list:
            tmp.append(f'{g}.{obj_p.node_name}.{obj_a.node_name}')

    return tmp


def gp_get_gpa(gp):
    # 根据g.p查询 所有g.p.a的列表  node=g.p  query_type=3
    tmp = []

    g, p = gp.split('.')
    obj_g = get_g(g)

    if not obj_g:
        return tmp

    obj_p = StreePath.objects.filter(
        level=1,
        node_name=p,
    ).first()
    if not obj_p:
        return tmp

    # 找所有a
    a_list = StreePath.objects.filter(
        level=2,
        path=f'{obj_p.path}/{obj_p.pk}'
    )

    if not a_list:
        return tmp

    for obj_a in a_list:
        tmp.append(f'{g}.{p}.{obj_a.node_name}')

    return tmp
