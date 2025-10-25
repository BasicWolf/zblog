from docutils import nodes
from docutils.parsers.rst import Directive, directives



class CommentDirective(Directive):
    has_content = True

    option_spec = {
        'from': directives.unchanged_required,
        'published_at': directives.unchanged_required,
    }

    def run(self) -> list[nodes.Node]:
        self.assert_has_content()
        comment_from = self.options['from']
        comment_text = '\n'.join(self.content)

        header_node = nodes.paragraph('', '', nodes.Text(comment_from))
        body_node = nodes.paragraph('', comment_text)
        body_node['classes'].append('comment-body')

        return [
            # A logical container for the comment header and body
            nodes.topic('', header_node, body_node)
        ]


def register():
    directives.register_directive("comment", CommentDirective)
