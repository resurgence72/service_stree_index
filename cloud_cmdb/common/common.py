import hashlib


def get_resource_disallow_labels(resource_type):
    """
    # 刷新倒排索引需要排除的labels
    :param resource_type:
    :return:
    """
    common = [
        'field_md5', 'create_at',
        'update_at', 'delete_at',
        'instance_id', 'zone_id'
    ]
    # 指定需要排除的resource type 字段
    disallow_labels_map = {
        'ecs': ['desc'],
        'rds': ['connection_str'],
        'clb': ['network_type', 'band_with'],
        'vpc': ['owner_id', 'desc'],
        'cdn': ['cname', 'desc', 'domain_name', 'source_content', 'source_port'],
    }

    disallow_list = disallow_labels_map.get(resource_type) + common
    return list(set(disallow_list))


# 特殊资源Label （sum）
special_labels = (
    'cpu_core', 'mem_size',
    'disk_size'
)


def get_gpa_tup(gpa):
    g, p, a = gpa.split('.')
    return (
        ('g', g),
        ('p', p),
        ('a', a),
    )


def get_md5(text):
    return hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()
