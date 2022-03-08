from cloud_cmdb.common.interted_index import InvertIndex


class ResourceInvertedIndex(object):

    def __init__(self):
        self.resource_map = {
            'ecs': InvertIndex(),
            'rds': InvertIndex(),
            'clb': InvertIndex(),
            'vpc': InvertIndex(),
            'cdn': InvertIndex(),
        }


rii = ResourceInvertedIndex()
