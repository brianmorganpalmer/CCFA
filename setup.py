
from setuptools import setup, find_packages

setup(
    name='mibc',
    version='0.0.1',
    description='CCFA data repository and automated analysis service',
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
    zip_safe=False,
    install_requires=[
        'nose>=1.3.0',
        'python-dateutil>=2.2',
        'bottle>=0.10',
        'psutil',
        'websocket',
        'tornado>=4.0',
        # doit, six, networkx, etc should come with anadama
        'anadama',
        'anadama_workflows',
    ],
    dependency_links=[
        'git+https://bitbucket.org/biobakery/anadama.git@master#egg=anadama-0.0.1', 
        'git+https://bitbucket.org/biobakery/anadama_workflows.git@master#egg=anadama_workflows-0.0.1',

    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha"
    ],
    entry_points= {
        'distutils.commands': [
            'web_setup = web_cms.local_setup:LocalSetupCommand'
        ],

        'console_scripts': [
            'email-validate    = mibc.email.cli:main',
            'mibc_build        = mibc.automated.cli:main',
            'mibc_tm           = mibc.tm.cli:main',
            'mibc_tm_daemon    = mibc.tm.cli_daemon.main',
        ],
    }
)
