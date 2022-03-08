from json import loads
from django.http import HttpResponse
from cloud_cmdb.gpa_utils.gpa_insert import *
from cloud_cmdb.gpa_utils.gpa_query import *
from cloud_cmdb.gpa_utils.gpa_delete import *
from cloud_cmdb.gpa_utils.gpa_mount import *
from cloud_cmdb.common import rii
from django.http.response import JsonResponse
from django.forms import model_to_dict
from prometheus_client import generate_latest
from cloud_cmdb import async_apscheduler
from cloud_cmdb.common.metrics import monitor


def stree_path_add(request):
    """
    服务树添加gpa需求 必须是三段式
    :param request:
    :return:
    """
    if request.method == "POST":
        gpa_list = loads(request.body).get('gpa')
        # 具体添加gpa逻辑
        resp = gpa_add(gpa_list)
        return JsonResponse({'code': 0, 'result': resp})


def stree_path_query(request):
    if request.method == "POST":
        """
        都是基于g/gp查下级
        
        1. 根据g查询 所有p的列表 node=g  query_type=1 
        2. 根据g查询 所有g.p.a的列表 node=g   query_type=2 
        3. 根据g.p查询 所有g.p.a的列表  node=g.p  query_type=3
        4. 查询所有gpa列表 query_type=4
        """
        gpa_node, gpa_query_type = loads(request.body).get('node'), loads(request.body).get('query_type')

        gpa_node_check = 0
        if gpa_node:
            gpa_node_check = len(gpa_node.split('.'))

        if gpa_query_type == query_type_map['g_get_p']:
            # 根据g查询 所有p的列表 node=g  query_type=1
            if gpa_node_check != 1 or gpa_node_check > 3:
                return JsonResponse({'code': 1, 'msg': 'query_type 对应的 node 格式校验失败'})
            resp_data = g_get_p(gpa_node)

        elif gpa_query_type == query_type_map['g_get_gpa']:
            # 根据g查询 所有g.p.a的列表 node=g   query_type=2
            if gpa_node_check != 1 or gpa_node_check > 3:
                return JsonResponse({'code': 1, 'msg': 'query_type 对应的 node 格式校验失败'})
            resp_data = g_get_gpa(gpa_node)

        elif gpa_query_type == query_type_map['gp_get_gpa']:
            #  根据g.p查询 所有g.p.a的列表  node=g.p  query_type=3
            if gpa_node_check != 2 or gpa_node_check > 3:
                return JsonResponse({'code': 1, 'msg': 'query_type 对应的 node 格式校验失败'})
            resp_data = gp_get_gpa(gpa_node)
        elif gpa_query_type == query_type_map['get_gpa']:
            # 只需要传入 query_type即可
            resp_data = get_gpa()

        else:
            return JsonResponse({'code': 1, 'msg': 'query_type 不存在'})

        return JsonResponse({'code': 0, 'result': resp_data})


def stree_path_delete(request):
    """
    传入g，如果g下有p就不让删g
    传入g.p，如果p下有a就不让删p
    传入g.p.a，直接删
    :param request:
    :return:
    """
    if request.method == 'POST':
        gpa_node = loads(request.body).get('node')
        gpa_node_check = len(gpa_node.split('.'))
        allow_force_delete = loads(request.body).get('force_delete')

        if not gpa_node_check or gpa_node_check > 3:
            return JsonResponse({'code': 1, 'msg': 'gpa 参数校验失败'})

        result = delete_gpa(gpa_node, allow_force_delete)
        return JsonResponse({'code': 0, 'result': result})


def stree_path_mount(request):
    if request.method == 'POST':
        req_data = loads(request.body)
        resource_type = req_data.get('resource_type')
        mount_ids, gpa_path = req_data.get('resource_ids'), req_data.get('target_path')
        gpa_node_check = len(gpa_path.split('.'))

        # 挂载操作只能限定于 gpa
        if not gpa_node_check or gpa_node_check > 3:
            return JsonResponse({'code': 1, 'msg': 'gpa 参数校验失败'})

        result = mount_gpa(resource_type, mount_ids, gpa_path)
        return JsonResponse({'code': 0, 'result': result})


def resources_query(request):
    if request.method == 'POST':
        req_data = loads(request.body)

        # 必须传入当前要查找的资源名
        resource_type = req_data.get('resource_type') or 'ecs'
        labels = req_data.get('labels')
        target_label = req_data.get('target_label')

        if not labels:
            return JsonResponse({'code': -1, 'msg': 'labels 不能为空'})

        special_target_labels = (
            'disk_size', 'mem_size', 'cpu_core'
        )

        ii = rii.resource_map.get(resource_type)
        analysis_func = ii.find_match_pks_by_labels
        if target_label in special_target_labels:
            analysis_func = ii.find_match_sums_by_labels

        # 结果需要强转为list
        analysis_result = analysis_func(labels, target_label)
        if isinstance(analysis_result, set):
            analysis_result = list(analysis_result)
            # 查找真正的数据
            tmp = []
            for ecs in EcsInfo.objects.filter(pk__in=analysis_result):
                ecs_dict = model_to_dict(
                    ecs,
                    exclude=['create_at', 'update_at', 'delete_at']
                )
                tmp.append(ecs_dict)
            analysis_result = {
                'resources_list': tmp,
                'resources_count': len(analysis_result)
            }

        # print(analysis_result)
        return JsonResponse({'code': 0, 'result': analysis_result})


def prometheus_metrics(request):
    if request.method == 'GET':
        # ;charset=utf-8 防止中文乱码
        return HttpResponse(generate_latest(monitor.register), status=200, content_type='text/plain;charset=utf-8')
