from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='tasks_collector',
    version='0.9.0',
    packages=find_packages(),
    install_requires=requirements,
    url='https://github.com/engdan77/tasks_collector',
    license='MIT',
    author='Daniel Engvall',
    author_email='daniel@engvalls.eu',
    description='A small project for collecting tasks',
    entry_points={
        'console_scripts': ['tasks_collector = tasks_collector.tasks_collector:main'],
        'gui_scripts': ['tasks_collector_gui = tasks_collector.tasks_collector:main']
        }
)
