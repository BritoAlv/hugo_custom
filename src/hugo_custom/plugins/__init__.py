from __future__ import annotations

from hugo_custom.plugins.assets import AssetsPlugin
from hugo_custom.plugins.base import Plugin
from hugo_custom.plugins.codeview import CodeViewPlugin
from hugo_custom.plugins.content import NotebookPlugin, PagePlugin
from hugo_custom.plugins.graph import GraphPlugin
from hugo_custom.plugins.homepage import HomepagePlugin
from hugo_custom.plugins.preview import PreviewPlugin
from hugo_custom.plugins.raw import RawPlugin
from hugo_custom.plugins.sidebar import SidebarPlugin


def default_plugins() -> list[Plugin]:
    return [
        NotebookPlugin(),
        PagePlugin(),
        CodeViewPlugin(),
        PreviewPlugin(),
        RawPlugin(),
        HomepagePlugin(),
        AssetsPlugin(),
        SidebarPlugin(),
        GraphPlugin(),
    ]
