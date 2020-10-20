# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
#
# aiida documentation build configuration file, created by
# sphinx-quickstart on Wed Oct 24 11:33:37 2012.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.
import os
import sys

import aiida
from aiida.manage.configuration import load_documentation_profile

# Load the dummy profile even if we are running locally, this way the documentation will succeed even if the current
# default profile of the AiiDA installation does not use a Django backend.
load_documentation_profile()

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#sys.path.insert(0, os.path.abspath('.'))

# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = '1.5.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.intersphinx', 'sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.viewcode', 'sphinx.ext.coverage',
    'sphinx.ext.mathjax', 'sphinx.ext.ifconfig', 'sphinx.ext.todo', 'IPython.sphinxext.ipython_console_highlighting',
    'IPython.sphinxext.ipython_directive', 'aiida.sphinxext', 'sphinx_panels', 'sphinx_copybutton', 'sphinxext.rediraffe'
]
ipython_mplbackend = ''
copybutton_selector = 'div:not(.no-copy)>div.highlight pre'
copybutton_prompt_text = r'>>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: '
copybutton_prompt_is_regexp = True

todo_include_todos = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'AiiDA'
copyright = '2014-2020, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '.'.join(aiida.__version__.split('.')[:2])
# The full version, including alpha/beta/rc tags.
release = aiida.__version__

author = 'The AiiDA team.'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    'datatypes/**',
    'developer_guide/**',
    'get_started/**',
    'howto/installation_more/index.rst',
    'import_export/**',
    'internals/engine.rst',
    'internals/global_design.rst',
    'internals/orm.rst',
    'internals/rest_api.rst',
    'restapi/**',
    'scheduler/index.rst',
    'topics/daemon.rst',
    'topics/repository.rst',
    'working_with_aiida/**',
]

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

intersphinx_mapping = {
    'click': ('https://click.palletsprojects.com/', None),
    'flask': ('http://flask.pocoo.org/docs/latest/', None),
    'flask_restful': ('https://flask-restful.readthedocs.io/en/latest/', None),
    'kiwipy': ('https://kiwipy.readthedocs.io/en/latest/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'plumpy': ('https://plumpy.readthedocs.io/en/latest/', None),
    'python': ('https://docs.python.org/3', None),
}

# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'pydata_sphinx_theme'


# Enable labeling for figures
numfig = True

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'external_links': [
        {'url': 'http://www.aiida.net/', 'name': 'AiiDA Home'}
    ],
    'github_url': 'https://github.com/aiidateam/aiida-core',
    'twitter_url': 'https://twitter.com/aiidateam',
    'use_edit_page_button': True,
}
html_context = {
    'github_user': 'aiidateam',
    'github_repo': 'aiida-core',
    'github_version': 'master',
    'doc_path': 'docs/source',
}
panels_add_bootstrap_css = False  # pydata-sphinx-theme already loads this

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = 'images/logo_aiida_docs.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_css_files = ['aiida-custom.css']
rediraffe_redirects = 'redirects.txt'

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = False

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'aiidadoc'


# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'aiida.tex', 'AiiDA documentation',
   author.replace(',',r'\and'), 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True

# this is to avoid the error
# aiida/orm/implementation/django/querybuilder.py:docstring of
# aiida.orm.implementation.django.querybuilder.array_length._compiler_dispatch:1: WARNING: Unknown target name: "visit".
autodoc_default_options = {
    'exclude-members': '_compiler_dispatch'
}


def run_apidoc(_):
    """Runs sphinx-apidoc when building the documentation.

    Needs to be done in conf.py in order to include the APIdoc in the
    build on readthedocs.

    See also https://github.com/rtfd/readthedocs.org/issues/1139
    """
    source_dir = os.path.abspath(os.path.dirname(__file__))
    apidoc_dir = os.path.join(source_dir, 'reference', 'apidoc')
    package_dir = os.path.join(source_dir, os.pardir, os.pardir, 'aiida')

    # In #1139, they suggest the route below, but for me this ended up
    # calling sphinx-build, not sphinx-apidoc
    #from sphinx.apidoc import main
    #main([None, '-e', '-o', apidoc_dir, package_dir, '--force'])

    import subprocess
    cmd_path = 'sphinx-apidoc'
    if hasattr(sys, 'real_prefix'):  # Check to see if we are in a virtualenv
        # If we are, assemble the path manually
        cmd_path = os.path.abspath(os.path.join(sys.prefix, 'bin', 'sphinx-apidoc'))

    options = [
        '-o', apidoc_dir, package_dir,
        '--private',
        '--force',
        '--no-headings',
        '--module-first',
        '--no-toc',
        '--maxdepth', '4',
    ]

    # See https://stackoverflow.com/a/30144019
    env = os.environ.copy()
    env['SPHINX_APIDOC_OPTIONS'] = 'members,special-members,private-members,undoc-members,show-inheritance'
    subprocess.check_call([cmd_path] + options, env=env)

def setup(app):
    if os.environ.get('RUN_APIDOC', None) != 'False':
        app.connect('builder-inited', run_apidoc)


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'aiida', 'AiiDA documentation',
     [author], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'aiida', 'AiiDA documentation',
   author, 'aiida', 'Automated Interactive Infrastructure and Database for Computational Science',
   'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'


# -- Options for Epub output ---------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = 'AiiDA'
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The language of the text. It defaults to the language option
# or en if the language is not set.
#epub_language = ''

# The scheme of the identifier. Typical schemes are ISBN or URL.
#epub_scheme = ''

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#epub_identifier = ''

# A unique identification for the text.
#epub_uid = ''

# A tuple containing the cover image and cover page html template filenames.
#epub_cover = ()

# HTML files that should be inserted before the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#epub_pre_files = []

# HTML files shat should be inserted after the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#epub_post_files = []

# A list of files that should not be packed into the epub file.
#epub_exclude_files = []

# The depth of the table of contents in toc.ncx.
#epub_tocdepth = 3

# Allow duplicate toc entries.
#epub_tocdup = True

# Warnings to ignore when using the -n (nitpicky) option
with open('nitpick-exceptions', 'r') as handle:
    nitpick_ignore = [
        tuple(line.strip().split(None, 1)) for line in handle.readlines() if line.strip() and not line.startswith('#')
    ]
