"""
Stub replacement for the legacy django-chunks package.
All chunk tags render empty strings so templates load without errors.
"""
from django.template import Library, Node

register = Library()


class ChunkNode(Node):
    def render(self, context):
        return ""


@register.tag
def chunk(parser, token):
    return ChunkNode()
