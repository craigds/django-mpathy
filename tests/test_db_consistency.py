import pytest

from django.db import connection, IntegrityError

from .models import MyTree


def flush_constraints():
    # the default db setup is to have constraints DEFERRED.
    # So IntegrityErrors only happen when the transaction commits.
    # Django's testcase thing does eventually flush the constraints but to
    # actually test it *within* a testcase we have to flush it manually.
    connection.cursor().execute("SET CONSTRAINTS ALL IMMEDIATE")


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


def test_parent_is_self_errors(db):
    root1 = MyTree.objects.create(label='root1')
    root1.parent = root1
    with pytest.raises(IntegrityError):
        root1.save()
        flush_constraints()


def test_parent_is_remote_ancestor_errors(db):
    root1 = MyTree.objects.create(label='root1')
    child2 = MyTree.objects.create(label='child2', parent=root1)
    desc3 = MyTree.objects.create(label='desc3', parent=child2)
    with pytest.raises(IntegrityError):
        # To test this integrity error, have to update table without calling save()
        # (because save() changes `ltree` to match `parent_id`)
        MyTree.objects.filter(pk=desc3.pk).update(parent=root1)
        flush_constraints()


def test_parent_is_descendant_errors(db):
    root1 = MyTree.objects.create(label='root1')
    child2 = MyTree.objects.create(label='child2', parent=root1)
    desc3 = MyTree.objects.create(label='desc3', parent=child2)
    child2.parent = desc3
    with pytest.raises(IntegrityError):
        child2.save()
        flush_constraints()
