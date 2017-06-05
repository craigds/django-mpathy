from django.contrib.postgres.operations import CreateExtension


class LTreeExtension(CreateExtension):

    def __init__(self):
        self.name = 'ltree'
