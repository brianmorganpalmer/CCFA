.. _metadata-txt:

###############################
metadata.txt - Project metadata
###############################

The metadata.txt file is a project's description. The file contains tab
separated values listing key-value pairs. The first column is the key,
while columns left of the key specify a list of values.

Required metadata keys
======================
``study_title``
    This can be any string that names your project.

``study_description``
    This can be any string that describes your project.

``sample_type``
    This string specifies the organism from which the samples were
    derived. Please specify species and body site separated by a
    comma. E.g. ``human, saliva`` or ``mouse, stool``.

``filename`` 
    Any list of strings, where each filename is delimited by
    a tab. Only files within this attribute/key are used as raw
    pipeline inputs.

``16s_data``
    ``true`` or ``false``. A ``true`` value initiates the
    :py:class:`anadama_workflows.pipelines.sixteen.SixteenSPipeline`. A
    ``false`` value initiates the 
    :py:class:`anadama_workflows.pipelines.wgs.WGSPipeline`.

``visualize``
    ``true`` or ``false``. A ``true`` value appends the optional
    visualization pipeline 
    :py:class:`anadama_workflows.pipelines.vis.VisualizationPipeline`.

``platform``
    ``illumina`` or ``454``. An ``illumina`` value modifies the 16S
    pipeline to demultiplexes using the Illumina-optimized QIIME
    demultiplexing script, while the ``454`` value uses the
    454-optimized QIIME demultiplexing script. When the ``16s_data``
    key is ``false``, this metadata key has no effect.


Optional metadata keys
======================
``skiptasks``
    list of strings, separated by tabs. Each string should be a
    key-value pair separated by a colon ``:``. The ``skiptasks``
    metadata field defines criterion by which AnADAMA will filter out
    or skip when executing tasks. The key in each key-value pair is
    the task field on which the filter operates, while the value (the
    string that comes after the colon) is a regular expression. If the
    regular expression matches contents of the field named in the key,
    the task is skipped. **All children of the skipped task will be
    also be skipped.** Here's an example: ``skiptasks	name:humann``
    will skip any tasks that contain ``humann`` in the task's ``name``
    attribute.

``pi_first_name``
    list of strings, separated by tabs

``pi_last_name``
    list of strings, separated by tabs

``pi_contact_email``
    list of strings, separated by tabs

``lab_name``
    list of strings, separated by tabs

``researcher_first_name``
    list of strings, separated by tabs

``researcher_last_name``
    list of strings, separated by tabs

``researcher_contact_email``
    list of strings, separated by tabs

``collection_start_date``
    date-like str

``collection_end_date``
    date-like str

``submit_to_insdc``
    true or false

``reverse_primer``
    str
