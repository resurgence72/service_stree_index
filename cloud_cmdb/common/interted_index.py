from re import match
from cloud_cmdb.common.heap import Heap
from collections import defaultdict


class LabelGroup(object):

    def __init__(self, label, count):
        self.label = label
        self.count = count

    def __lt__(self, other):
        """
        重写 __lt__ 对比大小
        :param other:
        :return:
        """
        return self.count < other.count


class InvertIndex(object):
    """
    倒排索引： 将需要查询的 tags 缓存，做提速查找用，同时支持多种 labels 查找策略：
    invert_index 根本用途仅提速用，同时支持多 labels_group, 多 expr 的灵活查找
    拼接 sql 或 ORM 也完全可实现
    """
    def __init__(self):
        # 此处如果写类变量 则不论实例化多少个 InvertIndex() 都会全局会共享
        self.mmap = defaultdict(dict)

    def reset(self):
        self.mmap.clear()

    def create_invert_index(self, pk, tags):
        """
        根据对象构建倒排索引
        将需要构建的 kv 组合成 dict 类型， 同时需要指定对应的唯一 pk
        :return:
        """
        for k, v in tags.items():
            if not v:
                continue
            if v not in self.mmap[k]:
                self.mmap[k][v] = {pk}
                continue

            # add 倒排索引 pk_set
            self.mmap[k][v].add(pk)

    def delete_invert_index(self, del_pks):
        """
        将指定 pk 从当前倒排索引中删除
        :param del_pks:
        :return:
        """
        if not self.mmap:
            return

        pk_set = set()
        pk_set.update(del_pks)

        for v in self.mmap.values():
            for kk, vv in v.items():
                v[kk] = vv - pk_set

    def find_match_pks_by_labels(self, labels, target_label=None):
        """
        根据 labels 加速找符合条件的pks
        """
        matcher_set = set()

        for idx, label in enumerate(labels):
            tmp_set = set()
            express = label['type']
            tag = label['key']
            value = label['value']
            if tag not in self.mmap:
                return {}

            for v, pks in self.mmap.get(tag).items():
                if express == 0 and value == v:
                    # 匹配
                    tmp_set.update(pks)
                elif express == 1 and value != v:
                    # 不匹配
                    tmp_set.update(pks)
                elif express == 2:
                    # 正则匹配
                    if value == '*':
                        return '* rex not allow'
                    if match(r'{}'.format(value), v):
                        tmp_set.update(pks)
                elif express == 3:
                    # 正则不匹配
                    if value == '*':
                        return '* rex not allow'
                    if not match(value, str(v)):
                        tmp_set.update(pks)

            # 如果刚开始执行，pk_set 需要初始化
            # 取相交的数据赋值给 pk_set
            if not idx and not matcher_set:
                matcher_set = tmp_set
            matcher_set &= tmp_set

            # 如果当前 pk_set 已经为空了，那么直接返回
            # 任何集合与空相交都为空，只有无意义了
            if not len(matcher_set):
                return matcher_set

        # 根据pks构建最终 result
        return self._build_match_data(matcher_set, target_label)

    def find_match_sums_by_labels(self, labels, target_label):
        """
        对 cpu disk mem 特殊统计需求，求总数
        """
        base_matchers = self.find_match_pks_by_labels(labels, target_label)
        # print("source.matchers: ", base_matchers)
        total_count = 0

        for matcher in base_matchers:
            # 表示当前资源配置(可能需要自定义取指定配置数字，此处模拟全部为数字)
            try:
                label = int(matcher.get('label', 1))
            except:
                return {'result': 'match.sums func label mast be integer!'}
            # 表示每个资源的数量
            count = int(matcher.get('count', 1))
            # 累加综合
            total_count += label * count

        return {"total_count": total_count}

    def _build_match_data(self, pks, target_label):
        """
        构建最终返回结果
        :param target_label:
        :param pks:
        :return:
        """

        if not target_label:
            return pks

        return self.get_group_by_label(pks, target_label)

    def get_group_by_label(self, pks, target_label):
        # 查询根据 target_label 的分布情况
        if target_label not in self.mmap:
            # return {'result': 'inverted-index can not find label_value'}
            print('inverted-index can not find label_value ', target_label, self.mmap)
            return set()

        distribute_map = defaultdict(int)
        label_values = self.mmap.get(target_label)

        # 构建 group_by
        for name, values in label_values.items():
            for vv in values:
                if vv in pks:
                    distribute_map[name] += 1

        # 根据 group_by 结果构建大根堆, 默认返回 top 10
        # print(distribute_map)
        return self._build_match_top_k([
            LabelGroup(*kv)
            for kv in distribute_map.items()
        ])

    @staticmethod
    def _build_match_top_k(match_count_group):
        # 构建大根堆 返回top k 的数据
        heap = Heap(match_count_group)
        return [top.__dict__ for top in heap.top_k(10)]

    def show_invert_index(self):
        """
        展示当前倒排索引内容 调试用
        :return:
        """
        for m in self.mmap.items():
            print(m)

    def get_labels(self):
        """
        展示当前所有的labels
        :return:
        """
        return list(self.mmap.keys())

    def get_labels_values_list(self, label):
        """
        根据 label 查询当前所有的 values_list
        :param label:
        :return:
        """
        return list(self.mmap.get(label).keys())

    def get_labels_values(self, label):
        """
        根据 label 查询当前所有的 values
        :param label:
        :return:
        """
        return self.mmap.get(label)


ii = InvertIndex()
