# aiida-sqs/setup.py
from setuptools import setup, find_packages

setup(
    name='aiida-sqs',
    version='0.1.0a0',
    description='SQS for AiiDA',
    author='The AiiDA Team',
    author_email='jzlshangan@163.com',
    url='https://github.com/jiazuolong/aiida-sqs',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'aiida-core>=2.5',
        'pymatgen>=2023.0.0',
        'icet>=2.0.0',
        'ase>=3.22.0',
        'click>=8.0.0',
    ],
    entry_points={
        'aiida.workflows': [
            'sqs.sqs = aiida_sqs.workflows.sqs:SQSWorkChain',
        ],
        'console_scripts': [
            'aiida-sqs = aiida_sqs.cli:cli',
        ],
    },
)
