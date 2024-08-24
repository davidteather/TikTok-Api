# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/main/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/main/usage/configuration.html#project-information

import sys
import os

sys.path.insert(0, os.path.abspath("../."))
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../.."))

project = "TikTokAPI"
copyright = "2023, David Teather"
author = "David Teather"
release = "v6.5.2"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/main/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["docs", "Thumbs.db", ".DS_Store"]

napoleon_google_docstring = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/main/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_baseurl = "https://davidteather.github.io/TikTok-Api/"

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
