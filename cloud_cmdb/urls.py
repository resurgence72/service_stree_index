from django.urls import path
from . import views

urlpatterns = [
    # 服务树操作
    path('gpa_add/', views.stree_path_add),
    path('gpa_query/', views.stree_path_query),
    path('gpa_delete/', views.stree_path_delete),
    path('gpa_mount/', views.stree_path_mount),

    # 资源查询
    path('resources_query/', views.resources_query),

    # prometheus 指标
    path('metrics/', views.prometheus_metrics),

]
