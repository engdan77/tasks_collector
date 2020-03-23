from setuptools import setup, find_packages
import os

opt = {
    'install_requires': {'in': (True, ['requirements.txt', '../requirements.txt']), 'out': None},
    'long_description': {'in': (False, ['README.md', '../README.md']), 'out': None}
}

for k, v in opt.items():
    _split, files = v['in']
    for p in files:
        try:
            with open(p) as f:
                d = f.read()
                opt[k]['out'] = d.splitlines() if _split else d
                print(f'Found data for {k}')
            break
        except FileNotFoundError:
            print(f'Unable to find {p} being in {os.getcwd()}')
    if not opt[k]['out']:
        raise RuntimeError(f'Abort due to missing data for {k} in setup')

setup(
    name='tasks_collector',
    version='0.9.5',
    packages=find_packages(),
    install_requires=opt['install_requires']['out'],
    url='https://github.com/engdan77/tasks_collector',
    license='MIT',
    author='Daniel Engvall',
    author_email='daniel@engvalls.eu',
    description='A small project for collecting tasks',
    long_description=opt['long_description']['out'],
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Environment :: MacOS X",
        "Topic :: Office/Business"
    ],
    entry_points={
        'console_scripts': ['tasks_collector = tasks_collector.__main__:main'],
        'gui_scripts': ['tasks_collector_gui = tasks_collector.__main__:main']
        }
)
