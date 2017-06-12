import pytest

from django.db import IntegrityError

from mpathy.models import BadMove

from .models import MyTree
from .test_db_consistency import flush_constraints


def test_move_to_self(db):
    a = MyTree.objects.create(label='a')
    with pytest.raises(BadMove):
        MyTree.objects.move_subtree(a, a)


def test_move_to_child(db):
    a = MyTree.objects.create(label='a')
    b = MyTree.objects.create(label='b', parent=a)
    with pytest.raises(BadMove):
        MyTree.objects.move_subtree(a, b)


def test_root_to_root(db):
    a = MyTree.objects.create(label='a')
    MyTree.objects.move_subtree(a, None)
    assert a.parent is None
    assert a.ltree == 'a'


def test_move_nonroot_to_nonroot(db):
    a = MyTree.objects.create(label='a')
    b = MyTree.objects.create(label='b', parent=a)
    c = MyTree.objects.create(label='c')
    MyTree.objects.move_subtree(b, c)
    assert b.parent == c
    assert b.ltree == 'c.b'
    assert set(a.get_children()) == set()
    assert set(c.get_children()) == {b}


def test_move_nonroot_to_root(db):
    a = MyTree.objects.create(label='a')
    b = MyTree.objects.create(label='b', parent=a)
    MyTree.objects.move_subtree(b, None)
    assert b.parent is None
    assert b.ltree == 'b'
    assert set(a.get_children()) == set()


def test_move_root_to_nonroot(db):
    a = MyTree.objects.create(label='a')
    b = MyTree.objects.create(label='b')
    MyTree.objects.move_subtree(b, a)
    assert b.parent.label == 'a'
    assert b.ltree == 'a.b'
    assert set(a.get_children()) == {b}


def test_move_nonroot_with_children_to_root(db):
    a = MyTree.objects.create(label='a')
    b = MyTree.objects.create(label='b', parent=a)
    c = MyTree.objects.create(label='c', parent=b)
    MyTree.objects.move_subtree(b, None)
    assert b.parent is None
    assert b.ltree == 'b'
    assert set(a.get_children()) == set()
    assert set(b.get_children()) == {c}

    flush_constraints()
    with pytest.raises(IntegrityError):
        # This node no longer has a valid ltree path, it was re-written in
        # the database when we moved b.
        # So we check that saving it with the old path correctly raises an error.
        c.save()
        flush_constraints()


def test_move_root_with_children_to_nonroot(db):
    a = MyTree.objects.create(label='a')
    b = MyTree.objects.create(label='b')
    c = MyTree.objects.create(label='c', parent=b)
    MyTree.objects.move_subtree(b, a)
    assert b.parent.label == 'a'
    assert b.ltree == 'a.b'
    assert set(a.get_children()) == {b}
    assert set(b.get_children()) == {c}

    flush_constraints()
    with pytest.raises(IntegrityError):
        # This node no longer has a valid ltree path, it was re-written in
        # the database when we moved b.
        # So we check that saving it with the old path correctly raises an error.
        c.save()
        flush_constraints()
