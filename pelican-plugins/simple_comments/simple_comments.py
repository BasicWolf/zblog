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
        return [
            # A logical container for the comment header and body
            nodes.topic(
                '',
                self._build_header_node(),
                self._build_comment_body_node()
            )
        ]

    def _build_header_node(self) -> nodes.paragraph:
        comment_author = self.options['from']
        published_at = self.options['published_at']

        published_at_node = nodes.inline('', published_at)
        published_at_node['classes'].append('comment-published-at')
        return nodes.paragraph(
            '',
            '',
            nodes.inline('', comment_author),
            nodes.Text(' on '),
            published_at_node
        )

    def _build_comment_body_node(self) -> nodes.paragraph:
        comment_text = '\n'.join(self.content)
        body_node = nodes.paragraph('', comment_text)
        body_node['classes'].append('comment-body')
        return body_node

def register():
    directives.register_directive("comment", CommentDirective)
