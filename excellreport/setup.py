from setuptools import setup, find_packages

setup(
    name='excellreport',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'openpyxl'
    ],
    entry_points={
        'console_scripts': [
            'task_duration_analyzer=excellreport.TaskDurationAnalyzer:main'
        ]
    }
)
