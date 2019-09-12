from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tasks_collector',
    version='0.0.9',
    packages=find_packages(),
    install_requires=requirements,
    url='https://github.com/engdan77/tasks_collector',
    license='MIT',
    author='Daniel Engvall',
    author_email='daniel@engvalls.eu',
    description='A small project for collecting tasks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        'console_scripts': ['tasks_collector = tasks_collector.__main__:main'],
        'gui_scripts': ['tasks_collector_gui = tasks_collector.__main__:main']
        }
)
