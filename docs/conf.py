# -*- coding: utf-8 -*-
'''
    Streetsign Documentation config file.
    -------------------------------------
'''
# pylint: disable=redefined-builtin, invalid-name, unused-import
import sys
import os

sys.path.append("../.virtualenv/lib/python2.7/site-packages/")
sys.path.append("../")
sys.path.append(os.path.dirname(__file__))

extensions = [
    'sphinx.ext.autodoc',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = u'StreetSign'
copyright = u'2013, Daniel Fairhead'

version = '0.5'
# The full version, including alpha/beta/rc tags.
release = '0.5'

exclude_patterns = ['_build']
pygments_style = 'sphinx'

# If true, keep warnings as "system message" paragraphs in the built documents.
#keep_warnings = False

rst_epilog = """
.. _Python: http://python.org/
.. _Flask: http://flask.pocoo.org/
.. _peewee: http://peewee.readthedocs.org/en/latest/
.. _flask-peewee: https://github.com/coleifer/flask-peewee
.. _jQuery: http://jquery.com/
.. _jQuery.transit: https://github.com/rstacruz/jquery.transit
.. _chosen: http://harvesthq.github.io/chosen/
.. _knockout.js: http://knockoutjs.com/
.. _pylint: http://www.pylint.org/ 
.. _pylint git commit hook: https://github.com/sebdah/git-pylint-commit-hook
.. _bleach: http://bleach.readthedocs.org/en/latest/index.html
.. _Bootstrap: http://twbs.github.io/bootstrap/
.. _sqlite: http://www.sqlite.org/
.. _FeedParser: http://pythonhosted.org/feedparser/
.. _Waitress: http://docs.pylonsproject.org/projects/waitress/en/latest/


"""

# ---------------------------------------------

html_theme = 'default'

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#html_extra_path = []

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
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'StreetSigndoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
  ('index', 'StreetSign.tex', u'StreetSign Documentation',
   u'Daniel Fairhead', 'manual'),
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


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'streetsign', u'StreetSign Documentation',
     [u'Daniel Fairhead'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'StreetSign', u'StreetSign Documentation',
   u'Daniel Fairhead', 'StreetSign', 'One line description of project.',
   'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#texinfo_no_detailmenu = False
