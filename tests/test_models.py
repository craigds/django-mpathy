from mpathy.fields import LTree
from .models import MyTree


def test_ltree_field(db):
    a = MyTree.objects.create(label='a')
    assert isinstance(a.ltree, LTree)

    a = MyTree.objects.get()
    assert isinstance(a.ltree, LTree)


def test_get_descendants_of_root(db):
    a = MyTree.objects.create(label='a')
    desc = {
        MyTree.objects.create(label='a', parent_id='a'),
        MyTree.objects.create(label='a', parent_id='a.a'),
        MyTree.objects.create(label='a', parent_id='a.a.a'),
    }
    MyTree.objects.create(label='b')
    MyTree.objects.create(label='b', parent_id='b')

    assert set(a.get_descendants()) == desc


def test_get_descendants_of_leaf(db):
    a = MyTree.objects.create(label='a')
    MyTree.objects.create(label='b')
    MyTree.objects.create(label='b', parent_id='b')

    assert set(a.get_descendants()) == set()


def test_get_ancestors_of_root(db):
    a = MyTree.objects.create(label='a')
    MyTree.objects.create(label='b')
    MyTree.objects.create(label='b', parent_id='b')

    assert set(a.get_ancestors()) == set()


def test_get_ancestors_of_leaf(db):
    ancestors = {
        MyTree.objects.create(label='a'),
        MyTree.objects.create(label='a', parent_id='a'),
        MyTree.objects.create(label='a', parent_id='a.a'),
    }
    aaaa = MyTree.objects.create(label='a', parent_id='a.a.a')

    MyTree.objects.create(label='b')
    MyTree.objects.create(label='b', parent_id='b')

    assert set(aaaa.get_ancestors()) == ancestors


def test_is_ancestor_of(db):
    a = MyTree.objects.create(label='a')
    aa = MyTree.objects.create(label='a', parent_id='a')
    b = MyTree.objects.create(label='b')

    assert a.is_ancestor_of(aa)
    assert not aa.is_ancestor_of(a)
    assert not b.is_ancestor_of(a)
    assert not a.is_ancestor_of(b)
    assert not b.is_ancestor_of(aa)
    assert not aa.is_ancestor_of(b)

    assert not a.is_ancestor_of(a)
    assert a.is_ancestor_of(a, include_self=True)
    assert not a.is_ancestor_of(b, include_self=True)

    # we allow None as it's like an actual single root node.
    assert not a.is_ancestor_of(None)
    assert not a.is_ancestor_of(None, include_self=True)


def test_is_descendant_of(db):
    a = MyTree.objects.create(label='a')
    aa = MyTree.objects.create(label='a', parent_id='a')
    b = MyTree.objects.create(label='b')

    assert not a.is_descendant_of(aa)
    assert aa.is_descendant_of(a)
    assert not b.is_descendant_of(a)
    assert not a.is_descendant_of(b)
    assert not b.is_descendant_of(aa)
    assert not aa.is_descendant_of(b)

    assert not a.is_descendant_of(a)
    assert a.is_descendant_of(a, include_self=True)
    assert not a.is_descendant_of(b, include_self=True)

    # we allow None as it's like an actual single root node.
    assert a.is_descendant_of(None)
    assert a.is_descendant_of(None, include_self=True)
