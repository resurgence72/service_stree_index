from apscheduler.schedulers.background import BackgroundScheduler
from cloud_cmdb.cmdb_utils.async_resources import __all__ as operator_list
from cloud_cmdb.cmdb_utils.async_refresh_inverted_index import refresh_inverted_index
from cloud_cmdb.cmdb_utils.async_dot_stree_index import dot_cloud_cmdb_resources

scheduler = BackgroundScheduler()

# 定时设置执行 ecs rds 的同步方法
for operator in operator_list:
    # 每 30min 同步一次云数据
    scheduler.add_job(operator.sync_resources, 'interval', seconds=30)
    # 每天凌晨清空倒排索引
    scheduler.add_job(
        refresh_inverted_index,
        'cron',
        hour=23,
        minute=59,
        args=(
            operator.resource_type,
            operator.resource_orm
        ),
    )

# 每10s打点一次倒排索引
scheduler.add_job(dot_cloud_cmdb_resources, 'interval', seconds=10)


def init():
    # 首次执行 ecs rds 方法
    for op in operator_list:
        op.sync_resources()
        refresh_inverted_index(op.resource_type, op.resource_orm)

    # 开始打点
    dot_cloud_cmdb_resources()
    scheduler.start()


init()
