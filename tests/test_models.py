import pytest

from django.db import IntegrityError

from .models import MyTree


@pytest.fixture
def tree(db):
    MyTree.objects.create(label='a')
    MyTree.objects.create(label='b')


def test_node_creation_simple(db):
    MyTree.objects.create(label='root1')
    MyTree.objects.create(label='root2')


def test_node_creation_with_no_label(db):
    # You need a label
    with pytest.raises(ValueError):
        MyTree.objects.create(label='')
    with pytest.raises(ValueError):
        MyTree.objects.create(label=None)
    with pytest.raises(ValueError):
        MyTree.objects.create()


def test_root_node_already_exists(db):
    MyTree.objects.create(label='root1')

    with pytest.raises(IntegrityError):
        MyTree.objects.create(label='root1')


def test_same_label_but_different_parent(db):
    root1 = MyTree.objects.create(label='root1')
    MyTree.objects.create(label='root1', parent=root1)


def test_same_label_as_sibling(db):
    root1 = MyTree.objects.create(label='root1')
    MyTree.objects.create(label='child', parent=root1)
    with pytest.raises(IntegrityError):
        MyTree.objects.create(label='child', parent=root1)


def test_parent_is_self(db):
    root1 = MyTree.objects.create(label='root1')
    root1._parent = root1
    with pytest.raises(IntegrityError):
        root1.save()
