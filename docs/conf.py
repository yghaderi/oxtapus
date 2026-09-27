"""Sphinx configuration for the Oxtapus documentation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from oxtapus._version import __version__

project = "Oxtapus"
author = "Yaghoub Ghadri"
copyright = "2026, Yaghoub Ghadri"
version = ".".join(__version__.split(".")[:2])
release = __version__

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
root_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_format = "short"
napoleon_google_docstring = True
napoleon_numpy_docstring = False

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "html_admonition",
    "html_image",
    "tasklist",
]
myst_heading_anchors = 3

copybutton_prompt_text = r">>> |\.\.\. "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "polars": ("https://docs.pola.rs/api/python/stable", None),
}

html_theme = "pydata_sphinx_theme"
html_title = f"مستندات Oxtapus {version}"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "github_url": "https://github.com/yghaderi/oxtapus",
    "show_nav_level": 2,
    "show_toc_level": 2,
    "navigation_with_keys": True,
    "navbar_align": "left",
    "navbar_end": ["theme-switcher", "navbar-icon-links", "search-field"],
    "footer_start": ["copyright"],
    "footer_end": ["sphinx-version", "theme-version"],
    "icon_links": [
        {
            "name": "حمایت از Oxtapus",
            "url": "https://daramet.com/yghaderi",
            "icon": "fa-regular fa-heart",
            "type": "fontawesome",
        }
    ],
}
