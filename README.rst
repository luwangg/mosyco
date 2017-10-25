The Mosyco Readme
====================

The mosyco prototype implements the observing part of the Model-/System-Controller architecture. It monitors the running system and evaluates the model performance in real-time. It outputs deviation logs and offers an optional dashboard view of live model performance.


Installation
-------------

This application requires Python 3.6 or higher!

The easiest way to install this may be to download the latest version
of Anaconda_. It comes with most of the necessary dependencies.

It is recommended to use a virtualenv or conda environment if there are muliple
Python installations on your system.

After installing Python:

1. Clone this repository and change into the directory::

    git clone "https://github.com/vab9/mosyco"
    cd mosyco

2. Setup a `virtual environment`_

3. Install the required dependencies with pip (or conda)::

    pip install -r requirements.txt


Dependencies
------------

Mosyco depends on numpy, pandas, dateutil and seaborn. Running in GUI-Mode (in order to view the live dashboard) also requires PyQt5 and matplotlib. Consult the the :download:`requirements file <../../requirements.txt>` to find the exact version numbers for each of the dependencies.


Usage
-----

Summary
^^^^^^^

::

    mosyco [-h] [-v | -q] [-s SYSTEMS [SYSTEMS ...]] \
        [-m MODELS [MODELS ...]] [-t THRESHOLD] [--gui] [--logfile]


Options
^^^^^^^

====================================   ================================================
Option                                 Explanation
====================================   ================================================
-h, --help                             Show this help message and exit
-v, --verbose                          Debug mode: generate more verbose log output
-q, --quiet                            Silence output: suppress any console or log output
-s, --systems SYSTEMS [SYSTEMS ...]    List of the actual system data columns. e.g. --systems 'PAseasonal' 'PAtrend'
-m, --models MODELS [MODELS ...]       List of the model data columns. e.g. -models 'PAmodel1' 'PAmodel2'
--threshold THRESHOLD                  The initial threshold used for the gap analysis
-t threshold                           Short form of --threshold
--gui                                  GUI-mode: show live updating plots. This will only work if for single model and system values.
--logfile                              Log to a file called 'mosyco.log'
====================================   ================================================



Examples
^^^^^^^^

All of these commands should be run from the root mosyco directory.

To print the help message, use::

    python -m mosyco --help

Run this command to start in non-gui mode, logging to a file called `mosyco.log`::

    python -m mosyco -v --logfile

Add the quiet option to suppress all terminal and log output::

    python -m mosyco -q

For GUI-Mode, use the following::

    python -m mosyco --gui

NOTE: GUI-Mode requires PyQt5. While in GUI-Mode, you can press SPACE in order
to pause/unpause the animation and ESC to quit.

References
^^^^^^^^^^

`Link to the data preparation notebook. <dataprep>`_

.. _dataprep: https://vab9.github.io/observer/

.. _Anaconda: https://www.continuum.io/downloads
.. _`virtual environment`: https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments
