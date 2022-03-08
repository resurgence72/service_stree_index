from django.db import models


class AssetRecord(models.Model):
    resource_id = models.CharField(max_length=128, verbose_name='实例id', default='')
    resource_type_choices = (
        (0, 'ecs'),
        (1, 'rds'),
    )
    resource_type = models.IntegerField(choices=resource_type_choices, default=0)
    content = models.TextField(verbose_name='变更信息')
    resource_action_choices = (
        (0, 'create'),
        (1, 'delete'),
        (2, 'update'),
    )
    record_type = models.IntegerField(choices=resource_action_choices, default=0)
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        db_table = 'asset_record'


class Common(models.Model):
    resource_type = None
    inverted_fields = [
        'g',
        'p',
        'a',
        # pk 用作唯一定位
        'id',
        'regain'
    ]

    regain = models.CharField(max_length=16, verbose_name="regain")
    instance_id = models.CharField(max_length=128, verbose_name="资源id", db_index=True)
    status = models.CharField(max_length=32, verbose_name="资源状态")
    zone_id = models.CharField(max_length=64, verbose_name="可用区id")
    g = models.CharField(max_length=32, verbose_name="group")
    p = models.CharField(max_length=32, verbose_name="project")
    a = models.CharField(max_length=32, verbose_name="app")
    field_md5 = models.CharField(max_length=64, verbose_name="资源字段md5")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    delete_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True


class EcsInfo(Common):
    resource_type = 'ecs'
    # 需要倒排索引的字段
    inverted_fields = Common.inverted_fields + [
        'hostname', 'vpc_addr', 'status',
        'regain', 'cpu_core', 'mem_size',
        'disk_size', 'os_type',
    ]
    hostname = models.CharField(max_length=128, verbose_name="主机名")
    vpc_addr = models.GenericIPAddressField(max_length=32, verbose_name="内网ip")
    cpu_core = models.IntegerField(verbose_name="cpu核数")
    mem_size = models.IntegerField(verbose_name="内存G")
    disk_size = models.IntegerField(verbose_name="磁盘G")
    desc = models.TextField(verbose_name="主机描述")
    os_type = models.CharField(max_length=16, verbose_name="操作系统类型")
    tags = models.CharField(max_length=512, verbose_name="tag json字符传")

    class Meta:
        db_table = "ecs_info"

    def __repr__(self):
        return f'{self.hostname}-{self.vpc_addr}'


class RdsInfo(Common):
    resource_type = 'rds'
    # 需要倒排索引的字段
    inverted_fields = Common.inverted_fields + [
        'instance_type', 'instance_net_type', 'instance_work_type',
        'engine', 'engine_version', 'connection_mode',
        'lock_mode'
    ]

    instance_type = models.CharField(max_length=32, verbose_name="db实例类型 主/从")
    instance_net_type = models.CharField(max_length=32, verbose_name="内外网连接方式")
    instance_work_type = models.CharField(max_length=32, verbose_name="实例网络类型")
    engine = models.CharField(max_length=64, verbose_name="数据库类型")
    engine_version = models.CharField(max_length=16, verbose_name='数据库版本')
    connection_mode = models.CharField(max_length=32, verbose_name='连接类型 单点/集群')
    connection_str = models.CharField(max_length=256, verbose_name='连接uri')
    lock_mode = models.CharField(max_length=32, verbose_name='实例锁定状态')

    class Meta:
        db_table = "rds_info"

    def __repr__(self):
        return f'{self.engine}-{self.engine_version}'


class ClbInfo(Common):
    resource_type = 'clb'
    # 需要倒排索引的字段
    inverted_fields = Common.inverted_fields + [
        'ip_version', 'tags',
    ]

    ip_version = models.CharField(max_length=32, verbose_name='ip类型 ipv4/ipv6')
    network_type = models.CharField(max_length=32, verbose_name='私网负载均衡实例的网络类型 vpc/classic')
    band_with = models.IntegerField(verbose_name='监听的带宽峰值，单位Mbps')
    tags = models.CharField(max_length=512, verbose_name="tag json字符传")
    clb_name = models.CharField(max_length=64, verbose_name='clb实例名称')

    class Meta:
        db_table = "clb_info"

    def __repr__(self):
        return f'{self.clb_name}-{self.ip_version}'


class VpcInfo(Common):
    resource_type = 'vpc'
    inverted_fields = Common.inverted_fields + [
        'tags', 'vpc_name', 'cidr_block'
    ]

    cidr_block = models.CharField(max_length=32, verbose_name='VPC的IPv4网段')
    desc = models.CharField(max_length=256, verbose_name='Description')
    owner_id = models.CharField(max_length=64, verbose_name='VPC所属的阿里云账号ID')
    tags = models.CharField(max_length=512, verbose_name="tag json字符传")
    vpc_name = models.CharField(max_length=64, verbose_name='实例名称')

    class Meta:
        db_table = "vpc_info"

    def __repr__(self):
        return f'{self.vpc_name}-{self.desc}'


class CdnInfo(Common):
    resource_type = 'cdn'
    inverted_fields = Common.inverted_fields + [
        'ssl_protocol', 'cdn_type', 'source_type'
    ]

    ssl_protocol = models.CharField(max_length=16, verbose_name='是否开启ssl')
    desc = models.CharField(max_length=256, verbose_name='Description')
    cname = models.CharField(max_length=128, verbose_name='cname')
    domain_name = models.CharField(max_length=128, verbose_name="加速域名")
    cdn_type = models.CharField(max_length=64, verbose_name='加速业务类型 web/download/video')
    source_type = models.CharField(max_length=64, verbose_name='源站类型')
    source_content = models.CharField(max_length=64, verbose_name='源站地址')
    source_port = models.CharField(max_length=64, verbose_name='源站地端口')
    coverage = models.CharField(max_length=16, verbose_name='加速区域 domestic：仅中国内地/global：全球/overseas：全球（不包含中国内地)')

    class Meta:
        db_table = "cdn_info"

    def __repr__(self):
        return f'{self.cname}-{self.cdn_type}'


class StreePath(models.Model):
    level = models.IntegerField(verbose_name="服务树级别")
    path = models.CharField(max_length=16, verbose_name="物化路径")
    node_name = models.CharField(max_length=32, verbose_name="节点名称")

    class Meta:
        db_table = "stree_path"
        # 联合约束   其中goods和user不能重复
        unique_together = ["level", "path", "node_name"]
