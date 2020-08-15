# coding: utf-8



from django import template

from django.utils.encoding import force_text
from django.utils.translation import ugettext as _

register = template.Library()


@register.filter
def tree_path(items, separator=' > '):
    """
    Creates a tree path represented by a list of ``items`` by joining
    the items with a ``separator``.

    Each path item will be coerced to unicode, so a list of model
    instances may be given if required.

    Example::

       {{ some_list|tree_path }}
       {{ some_node.get_ancestors|tree_path:" >> " }}

    """
    return separator.join(force_text(i) for i in items)


NOTSET = object()


class RecurseTreeNode(template.Node):
    def __init__(self, nodelist, parent_queryset_var):
        self.nodelist = nodelist
        self.parent_queryset_var = template.Variable(parent_queryset_var)

    def render(self, context, qs=NOTSET):
        with context.push():
            if qs is NOTSET:
                # At the top level, turn the given queryset into a list
                # of top-level nodes.
                qs = self.parent_queryset_var.resolve(context)
                root_nodes = qs.get_cached_trees()
                context[self.parent_queryset_var.var] = root_nodes
            else:
                # At lower levels, we've been passed in a list of child nodes.
                context[self.parent_queryset_var.var] = qs
            context['_mpathy_recursetree_parent'] = self
            return self.nodelist.render(context)


@register.tag
def recursetree(parser, token):
    """
    Iterates over the nodes in the tree, and renders the contained block for each node.
    This tag will recursively render children into the template variable {{ children }}.
    Only one database query is required (children are cached for the whole tree)

    Usage:
            <ul>
                {% recursetree nodes %}
                    {% for node in nodes %}
                        <li>
                            {{ node.label }}
                            {% if not node.is_leaf_node %}
                                <ul>
                                    {% recurse node.get_children %}
                                </ul>
                            {% endif %}
                        </li>
                    {% endfor %}
                {% endrecursetree %}
            </ul>
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError(_('%s tag takes one argument') % bits[0])

    parent_queryset_var = bits[1]

    nodelist = parser.parse(['endrecursetree'])
    parser.delete_first_token()

    return RecurseTreeNode(nodelist, parent_queryset_var)


class RecurseNode(template.Node):
    def __init__(self, child_queryset_var):
        self.child_queryset_var = template.Variable(child_queryset_var)

    def render(self, context):
        if '_mpathy_recursetree_parent' not in context:
            raise template.TemplateSyntaxError(
                'Invalid syntax: {% recurse %} must be inside {% recursetree %}'
            )

        parent = context['_mpathy_recursetree_parent']
        qs = self.child_queryset_var.resolve(context)
        with context.push():
            return parent.render(context, qs)


@register.tag
def recurse(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError(_('%s tag takes one argument') % bits[0])

    return RecurseNode(bits[1])
