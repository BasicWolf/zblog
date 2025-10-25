import pytest

from textwrap import dedent

from docutils.core import publish_doctree
from docutils.parsers.rst import directives
from docutils.utils import SystemMessage

from .simple_comments import CommentDirective, CommentNode, register
from docutils import nodes


@pytest.fixture(scope='session', autouse=True)
def register_comment_directive():
    register()


def test_comment_renders_to_single_node():
    doctree = build_doctree("""
       .. comment::
          :from: does not matter

          Does not matter
    """)

    assert len(doctree.children) == 1, "The rendered document should contain only one Comment node"
    comment_node = doctree.children[0]
    assert isinstance(comment_node, CommentNode), "Expected to find Comment node in the document"


def test_has_from_attribute():
    doctree = build_doctree("""
       .. comment::
          :from: Alex Black

          Does not matter
    """)

    comment_node = doctree.children[0]
    from_node_text = comment_node[0].astext()
    assert from_node_text  == 'Alex Black', "Expected to find comment author's name"


def test_errors_when_from_attribute_missing():
    with pytest.raises(KeyError) as e:
        build_doctree("""
        .. comment::

           Does not matter
        """)
    assert e.value.args[0] == 'from'


def test_has_publication_timestamp():
    doctree = build_doctree("""
       .. comment::
          :published_at: 2025-10-25T11:22:47+00:00
          :from: Does Not Matter

          Does Not Matter
    """)

def test_has_body():
    doctree = build_doctree("""
       .. comment::
          :from: Does Not Matter

          An awesome article
    """)

    comment_node = doctree.children[0]
    comment_body_text = comment_node[1].astext()
    assert comment_body_text == 'An awesome article', "Expected to find comment body"


def test_has_body_with_multiline_text():
    doctree = build_doctree("""
       .. comment::
          :from: Does Not Matter

          An
          awesome
          article
    """)

    comment_node = doctree.children[0]
    comment_body_text = comment_node[1].astext()
    assert comment_body_text == 'An\nawesome\narticle', "Expected to find comment body"


def test_errors_when_comment_body_missing():
    with pytest.raises(SystemMessage):
        build_doctree("""
        .. comment::
           :from: Does Not Matter

        not-comment
        """)


def build_doctree(content: str):
    # Configuration to halt on errors
    settings = {
        'halt_level': 3,  # Halt on ERROR or higher (adjust as needed)
        # Optionally: 'traceback': 1 to propagate the full traceback
    }

    return publish_doctree(dedent(content), settings_overrides=settings)
