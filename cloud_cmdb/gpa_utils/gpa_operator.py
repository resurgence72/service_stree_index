from ..models import StreePath


def get_g(g):
    return StreePath.objects.filter(
        level=0,
        node_name=g,
        path='0'
    ).first()


def get_p(g, p):
    return StreePath.objects.filter(
        level=1,
        node_name=p,
        path=f'/{g.pk}'
    ).first()
