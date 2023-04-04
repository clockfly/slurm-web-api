from setuptools import setup, find_packages
import os

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('slurm-ui/static')

setup(
    name='slurm-ui',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'slurm-ui': extra_files
    },
    install_requires=[
        'flask',
        'flask_restful',
        'pymysql',
        'sqlalchemy'
    ],
)
