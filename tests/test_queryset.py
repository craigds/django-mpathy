# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals


from .models import MyTree


def test_get_cached_trees_empty(db):
    assert MyTree.objects.get_cached_trees() == []


def test_get_cached_trees(db, django_assert_num_queries):
    a = MyTree.objects.create(label='a')
    aa = MyTree.objects.create(label='aa', parent=a)
    aaa = MyTree.objects.create(label='aaa', parent=aa)
    aaz = MyTree.objects.create(label='aaz', parent=aa)
    b = MyTree.objects.create(label='b')
    bb = MyTree.objects.create(label='bb', parent=b)

    # just ordering this to make the asserts a bit simpler. not required.
    qs = MyTree.objects.order_by('label')

    with django_assert_num_queries(1):
        cached = qs.get_cached_trees()

    with django_assert_num_queries(0):
        assert cached == [a, b]
        assert cached[0].get_children() == [aa]
        assert cached[0].get_children()[0].get_children() == [aaa, aaz]
        assert cached[1].get_children() == [bb]
        assert cached[1].get_children()[0].get_children() == []
