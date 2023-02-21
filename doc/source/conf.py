"""Sphinx documentation configuration file."""
import os
import shutil
from datetime import datetime
from pathlib import Path

import jupytext
from ansys_sphinx_theme import pyansys_logo_black, ansys_favicon

from ansys.grantami.recordlists import __version__


# Project information
project = "ansys-grantami-recordlists"
project_copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__

# Select desired logo, theme, and declare the html title
html_logo = pyansys_logo_black
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "Granta MI RecordLists"
html_favicon = ansys_favicon

# specify the location of your github repo
html_theme_options = {
    "github_url": "https://github.com/pyansys/grantami-recordlists",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
}

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "nbsphinx",
]

# sphinx
add_module_names = False

# sphinx.ext.autodoc
autodoc_typehints = "both"
autodoc_typehints_description_target = "documented"
autodoc_member_order = "bysource"

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/dev", None),
    "openapi-common": ("https://openapi.docs.pyansys.com", None),
    # kept here as an example
    # "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    # "numpy": ("https://numpy.org/devdocs", None),
    # "matplotlib": ("https://matplotlib.org/stable", None),
    # "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    # "pyvista": ("https://docs.pyvista.org/", None),
    # "grpc": ("https://grpc.github.io/grpc/python/", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}


# static path
html_static_path = ["_static"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# Generate section labels up to four levels deep
autosectionlabel_maxdepth = 4


# -- Example Script functions -------------------------------------------------

# Define some important paths and check were are where we expect to be
cwd = Path(os.getcwd())
assert cwd.name == "source"
EXAMPLES_DIR_NAME = "examples"
DUMMY_EXAMPLES_DIR_NAME = "examples-dummy"

examples_output_dir = Path(EXAMPLES_DIR_NAME).absolute()
examples_source_dir = Path("../../" + EXAMPLES_DIR_NAME).absolute()
dummy_examples_source_dir = Path("../../" + DUMMY_EXAMPLES_DIR_NAME).absolute() / Path(
    EXAMPLES_DIR_NAME
)
EXAMPLE_FLAG = os.getenv("BUILD_EXAMPLES")

# If we are building examples, use the included ipython-profile
if EXAMPLE_FLAG:
    ipython_dir = Path("../../.ipython").absolute()
    os.environ["IPYTHONDIR"] = str(ipython_dir)


def _copy_examples_and_convert_to_notebooks(source_dir, output_dir):
    for root, dirs, files in os.walk(source_dir):
        root_path = Path(root)
        index = root_path.parts.index(EXAMPLES_DIR_NAME) + 1  # Path elements below examples
        root_output_path = output_dir.joinpath(*root_path.parts[index:])
        root_output_path.mkdir(
            parents=False, exist_ok=False
        )  # Create new folders in corresponding output location
        for file in files:
            file_source_path = root_path / Path(file)
            file_output_path = root_output_path / Path(file)
            shutil.copy(file_source_path, file_output_path)  # Copy everything
            if file_source_path.suffix == ".py":  # Also convert python scripts to jupyter notebooks
                ntbk = jupytext.read(file_source_path)
                jupytext.write(ntbk, file_output_path.with_suffix(".ipynb"))


# If we already have a source/examples directory then don't do anything.
# If we don't have an examples folder, we must first create it
# We don't delete the examples after every build because this triggers nbsphinx to re-run them,
# which is very expensive
if not examples_output_dir.is_dir():
    # Only include examples if the environment variable is set to something truthy
    if EXAMPLE_FLAG:
        print("'BUILD_EXAMPLES' environment variable is set, including examples in docs build.")
        _copy_examples_and_convert_to_notebooks(examples_source_dir, examples_output_dir)

    # If we are skipping examples in the docs, create a placeholder index.rst file to avoid sphinx
    # errors.
    else:
        print("'BUILD_EXAMPLES' environment variable is not set, using standalone examples.")
        _copy_examples_and_convert_to_notebooks(dummy_examples_source_dir, examples_output_dir)


nbsphinx_prolog = """
Download this example as a :download:`Jupyter notebook </{{ env.docname }}.ipynb>` or a
:download:`Python script </{{ env.docname }}.py>`.

----
"""
