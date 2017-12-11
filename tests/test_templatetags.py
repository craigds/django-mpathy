# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals


from django.template import Template, Context

from .models import MyTree


def test_render_recursetree(db):
    a = MyTree.objects.create(label='a')
    MyTree.objects.create(label='ab', parent=a)

    t = Template(
        "{% load mpathy %}{% recursetree nodes %}"
        "{% for node in nodes %}\n"
        "    <li>{{ node.label }}<ul>{% recurse node.get_children %}</ul></li>"
        "{% endfor %}"
        "{% endrecursetree %}"
    )

    context = Context({
        'nodes': MyTree.objects.all(),
    })
    rendered = t.render(context)

    assert rendered == (
        '\n'
        '    <li>a<ul>\n'
        '    <li>ab<ul></ul></li></ul></li>'
    )
