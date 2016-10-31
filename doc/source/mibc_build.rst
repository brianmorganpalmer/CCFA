.. _mibc-build:

###################################################################
mibc_build - A command line interface to standard AnADAMA pipelines
###################################################################

.. contents::

________________________________________________________________________________

Introduction to mibc_build
==========================

``mibc_build`` is a command line tool that extends the AnADAMA tool
functionality with the concept of a project to perform automated
analysis of metagenomic and metatranscriptomic data. Whereas AnADAMA
referenced a DoIt script (or implicitly if were the script named
dodo.py) for a set of tasks to perform any workflow, ``mibc_build``
references a project for its set of tasks to perform a set of
metagenomic workflows (a pipeline). The ``mibc_build`` tool can
customize how a particular project's data will be fed through a
standard metagenomic pipeline by use of some well-placed command line
parameters and/or by editing a configuration file.

A project is the atomic unit of a collection of data for all things
``mibc``. A project is defined as a directory containing a set of
primary data files and two pieces of metadata that describe the
project and raw inputs. The project defines the nature of the
deposited data with metadata, a set of key-value pairs describing the
project's sample type, the files intended as raw input for analysis,
whether data products should be visualized, etc. For details on
project metadata, refer to :ref:`metadata-txt`. A typical project is
comrprised of many samples, where each sample corresponds to a study
participant, model animal, or time series step. These sample-specific
metadata are described in a free-form, tab-delimited fashion in
:ref:`map-txt`.


Generating Project Metadata
===========================

Generating the required metadata by hand is tiresome. We added a
function to ``mibc_build`` for that: ``initialize-project``. Running
``mibc_build initialize-project`` generates the required project and
sample-specific metadata in the current directory. Metadata key-values
are specified on the command lines as ``key: value``. ``mibc_build
initialize-project`` will query the user for any missing but required
metadata keys. Without arguments, ``initialize-project`` queries the
user for all required metadata fields.

Some metadata keys have a special meaning to ``mibc_build
initialize-project``. 

* ``filename`` is interpreted as a list, with each file separated by a
  comma. ``filename`` can also be specified using shell-style globbing
  patterns: an argument of ``filename: glob:*.fastq`` will be
  interpreted as all FASTQ files in current directory and be written
  to the metadata.txt file accordingly. In a similar fashion,
  ``filename`` can be given as a regular expression: ``filename:
  re:SRS[0-9]+.sff`` would write all numerical sff files beginning
  with "SRS" to the project and sample metadata. Finally, simply
  leaving the value blank will write all files to the projects
  metadata: just do ``filename:``.

* ``platform`` describes the make of the sequencing platform used to
  sequence these data. Valid choices for this key are "Illumina"
  or 454. ``mibc_build initialize-project`` will handle the necessary
  capitalization for you.

* ``visualize`` and ``16s_data`` are true/false keys. The only
  excepted values are ones that can be coerced into true or
  false. Some example strings considered true: ``Y``, ``true``,
  ``yes``. Some example strings considered false: ``no``, ``n``,
  ``kittenpants``.


Running the standard pipelines
==============================

The hard part is over. With a project sufficiently described with
metadata, just point ``mibc_build`` at your project and let it run the
pipeline with the ``--project`` flag: 
``mibc_build runproject --project puppies_project``


Examples
========

Test WGS pipeline data
----------------------

.. code-block:: bash

  wget -O- 'http://huttenhower.sph.harvard.edu/biobakery-shop/anadama/16s_functional_test.tgz' | tar -xvzf -
  cd 16s_functional_test
  mibc_build initialize-project \
	  'study_description: test' \
	  'sample_type: mouse' \
	  'filename:' \
	  '16s_data: true' \
	  'study_title: test' \
	  'platform: 454' \
	  'visualize: yes'
  cd - 
  mibc_build runproject \
           --project 16s_functional_test/ \
           --reporter=verbose \
           > 16s_functional_test.run.log \
           2>&1


Test 16S pipeline data
----------------------

.. code-block:: bash

  wget -O- 'http://huttenhower.sph.harvard.edu/biobakery-shop/anadama/wgs_functional_test.tgz' | tar -xvzf -
  cd wgs_functional_test
  mibc_build initialize-project \
	  'study_description: test' \
	  'sample_type: human, skin' \
	  'filename:' \
	  '16s_data: no' \
	  'study_title: test' \
	  'platform: 454' \
	  'visualize: yes'
  cd - 
  mibc_build runproject \
           --project wgs_functional_test/ \
           --reporter=verbose \
           > wgs_functional_test.run.log \
           2>&1

