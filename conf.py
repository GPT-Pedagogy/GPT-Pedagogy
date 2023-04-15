# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys
import os

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'GPT Pedagogy'
copyright = '2023, Matthew Pisano'
author = 'Matthew Pisano'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'venv']

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "model")))

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'classic'
html_static_path = ['docs/sphinx/_static']

html_css_files = ['css/custom.css']

def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False

    return would_skip


def setup(app):
    app.connect("autodoc-skip-member", skip)
