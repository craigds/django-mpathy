from .models import MyTree


def test_nest_nodes_empty(db):
    assert MyTree.objects.nest_nodes() == {}


def test_nest_nodes(db):
    a = MyTree.objects.create(label='a')
    aa = MyTree.objects.create(label='aa', parent=a)
    aaa = MyTree.objects.create(label='aaa', parent=aa)
    b = MyTree.objects.create(label='b')

    assert MyTree.objects.nest_nodes() == {
        'a': {
            'node': a,
            'children': {
                'aa': {
                    'node': aa,
                    'children': {
                        'aaa': {
                            'node': aaa,
                            'children': {}
                        }
                    }
                }
            },
        },
        'b': {
            'node': b,
            'children': {}
        }
    }
