import json
import hashlib
from io import StringIO
from aliyunsdkcore.client import AcsClient
from django.forms import model_to_dict
from cloud_cmdb.signals import try_refresh
from cloud_cmdb.models import AssetRecord
# from cloud_cmdb.common.metrics import monitor
from aliyunsdkcore.auth.credentials import AccessKeyCredential


class AliOperator(object):
    resource_type = None

    @staticmethod
    def get_unhash_field():
        return [
            # 自带的属性不做hash
            'create_at', 'update_at', 'delete_at', 'id',
            # 用户自定义的 gpa 不做hash
            'g', 'p', 'a'
        ]

    def __init__(self):
        self.credentials = AccessKeyCredential('', '')
        self.client = AcsClient(region_id='cn-beijing', credential=self.credentials)

    def get_resources(self, sdk, items_path=None):
        items_path = items_path or []

        resource_list = []
        request = sdk()
        request.set_accept_format('json')
        # 需要修改为 50 因为 vpc 最大限制为50, 会报错
        request.set_PageSize(50)
        request.set_PageNumber(1)

        response = self.client.do_action_with_exception(request)
        resp = json.loads(response)

        def get_inner_resp(resp):
            _resp = resp
            for item in items_path:
                _resp = _resp.get(item)
            return _resp

        resource_list.extend(get_inner_resp(resp))
        next_token = resp.get('NextToken')
        while next_token:
            request.set_NextToken(next_token)
            response = self.client.do_action_with_exception(request)
            resp = json.loads(response)
            resource_list.extend(get_inner_resp(resp))
            next_token = resp.get('NextToken')

        return resource_list

    @staticmethod
    def get_resource_md5(resource_map):
        m = hashlib.md5()
        for v in resource_map.values():
            v_bytes = bytes(str(v), encoding='utf8')
            m.update(v_bytes)
        return m.hexdigest()

    def get_resource_dict(self, resource):
        resource_map = resource.__dict__
        drop_field = self.get_unhash_field()

        for k in resource_map:
            if k.startswith('_'):
                drop_field.append(k)

        for field in drop_field:
            if field in resource_map:
                resource_map.pop(field)
        return resource_map

    def analysis_resources(self, bulk_list, orm_type):
        curr_resource_hash_map = {
            resource.instance_id: resource
            for resource in bulk_list
        }

        old_resource_hash_map = {
            resource.instance_id: resource
            for resource in orm_type.objects.all()
        }

        old_instances_id = set(old_resource_hash_map.keys())
        curr_instances_id = {resource.instance_id for resource in bulk_list}

        maybe_modify_instances = old_instances_id & curr_instances_id
        del_instances = old_instances_id - curr_instances_id
        add_instances = curr_instances_id - old_instances_id

        # 新增 使用的是 curr_resource_hash_map，里面存的新resource
        if add_instances:
            for instance_id in add_instances:
                resource = curr_resource_hash_map.get(instance_id)
                resource.save()

                # 保存记录
                AssetRecord.objects.create(
                    resource_type=1,
                    resource_id=resource.instance_id,
                    record_type=0,
                    content=f'阿里云 {self.resource_type} - {resource.instance_id} 机器增加'
                )

            # 触发新增信号
            try_refresh.send(
                sender=self.resource_type,
                operate_type='create',
                operate=[
                    model_to_dict(curr_resource_hash_map.get(instance_id))
                    for instance_id in add_instances
                ])
            # 打点
            # monitor.cloud_cmdb_resources_action_change.labels(
            #     action='create',
            #     resource_type=self.resource_type,
            # ).inc(len(add_instances))

        # 删除
        if del_instances:
            for instance_id in del_instances:
                resource = old_resource_hash_map.get(instance_id)
                # 保存删除记录
                AssetRecord.objects.create(
                    resource_type=1,
                    resource_id=resource.instance_id,
                    record_type=1,
                    content=f'阿里云 {self.resource_type} - {resource.instance_id} 机器删除'
                )

                resource.delete()

            # 触发删除信号
            try_refresh.send(
                sender=self.resource_type,
                operate_type='create',
                operate=list(del_instances)
            )
            # 打点
            # monitor.cloud_cmdb_resources_action_change.labels(
            #     action='delete',
            #     resource_type=self.resource_type,
            # ).inc(len(del_instances))

        # 修改
        actual_modify_list = []
        for instance_id in maybe_modify_instances:
            curr_resource = curr_resource_hash_map.get(instance_id)
            resource_map = self.get_resource_dict(curr_resource)

            curr_field_md5 = self.get_resource_md5(resource_map)
            # 当前md5和数据库中同instance的hash比较
            old_resource = orm_type.objects.filter(instance_id=instance_id).first()

            if old_resource.field_md5 == curr_field_md5:
                # 数据一致 不做操作
                continue

            # 数据不一致 需要比对每个数据是否变化

            # 准备更新记录表
            is_change = False
            stream = StringIO()
            stream.write(f'阿里云 {self.resource_type} - {instance_id} 机器准备更新:\n')

            for field_K, field_V in self.get_resource_dict(curr_resource).items():
                old_field = getattr(old_resource, field_K)
                curr_field = getattr(curr_resource, field_K)

                if old_field == curr_field:
                    # md5比对相同，不处理
                    continue

                is_change = True
                # 不相等的字段需要赋值
                actual_modify_list.append(instance_id)
                setattr(old_resource, field_K, field_V)
                old_resource.save()

                # 重要 需要重新赋值，否则下面报错 get(instance_id) 对象缺少attname属性
                old_resource_hash_map[instance_id] = old_resource

                stream.write(f'字段 {field_K} 由 {old_field} 更新为 {curr_field}; ')

            if is_change:
                # 保存删除记录
                AssetRecord.objects.create(
                    resource_type=1,
                    resource_id=old_resource.instance_id,
                    record_type=2,
                    content=stream.getvalue()
                )

        # 触发修改信号
        if actual_modify_list:
            # 发送倒排索引信号
            try_refresh.send(
                sender=self.resource_type,
                operate_type='update',
                operate=[
                    model_to_dict(old_resource_hash_map.get(instance_id))
                    for instance_id in actual_modify_list
                ])
            # 打点
            # monitor.cloud_cmdb_resources_action_change.labels(
            #     action='update',
            #     resource_type=self.resource_type,
            # ).inc(len(actual_modify_list))

        print(
            f'{self.resource_type} 新增: {len(add_instances)}, 删除: {len(del_instances)}, 可能修改: {len(maybe_modify_instances)}, 实际修改: {len(actual_modify_list)}')
