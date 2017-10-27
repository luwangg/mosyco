.. _intro:

************
Introduction
************

The Problem
===========

Model-based business planning requires domain knowledge. This knowledge often comes from domain experts and will always reflect the currently available information about the system at the time it is devised.

Most real-life business systems are dynamic in nature. Without constant readjustments to the corresponding model, it may lose its predictive quality over time. The domain experts must therefore regularly adjust the model to fit the changing environment. [1]_

As business modelling can be difficult and expensive, the cost of maintaining accurate models for dynamic systems can grow rapidly. The proposed Model-/System-Controller architecture seeks to mitigate this issue by integrating a self-correction mechanism (or self-adaptive property) [2]_ into the model.

The Model-/System-Controller Architecture
=========================================

.. figure:: _static/mosyco-architecture.png
    :alt: mosyco-architecture

    Model-/System-Controller Architecture. Source: Breuer, 2016 [2]_


The architecture introduces several interconnected components. The components that are important to be aware of for this project are:
- The *system under observation* provides a stream of actual system data to the observer.
- The *observer* monitors the running system for deviations from the model and alerts the Model-Controller if such deviations exceed some (possibly dynamic) threshold.
- The *model-controller* makes structural or parametric changes to the model in order to reflect changes in the running systems environment.
- The *model* allows planning for some business purpose. It is based on expert- and/or domain-knowledge.


Detailed Information about the prototype can be found here: :ref:`prototype`. Information on how to install and test the prototype can be found here in its Readme: :ref:`readme`. For an in-depth description of the prototype's components and how they work together, see the accompanying paper.


Academic Sources
================

For a detailed list of academic sources that this project references in the footnotes, please consult the accompanying paper's bibliography:

    `"Real-Time Gap Analysis - Konzeption und prototypische Implementierung einer automatisierten Abweichungsanalyse zur betriebswirtschaftlichen Planung" <http://127.0.0.1>`_


.. [1] Sauter, 2011
.. [2] Breuer, 2016
