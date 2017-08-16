======
MoSyCo
======

This is the prototype for a Model-/System-Controller architecture.

Installation:
-------------

This application requires Python 3.6 or higher!

The easiste way to install this may be to download the latest version
of Anaconda_. It comes with most of the necessary dependencies.

It is recommended to use a virtualenv or conda environment if there are muliple
Python installations on your system.

After installing Python:

1. Clone this repository and change into the directory::

    git clone "https://github.com/vab9/mosyco"
    cd mosyco

2. Setup a virtual environment

3. Install the required dependencies (takes a while)::

    pip install -r requirements.txt


Running:
--------

Run this command from the root mosyco directory::

    python -m mosyco

You can specify command line arguments to the program as well::

    python -m mosyco [arguments]

For example, to print the help message::

    python -m mosyco --help


`Link to the data preparation notebook <https://vab9.github.io/observer/>`_

.. _Anaconda: https://www.continuum.io/downloads
