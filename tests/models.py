from mpathy.models import MPathNode


class MyTree(MPathNode):
    def __str__(self):
        return self.ltree
