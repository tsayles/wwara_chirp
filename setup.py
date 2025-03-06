from importlib.metadata import entry_points

from setuptools import setup, find_packages

setup(
    name='wwara_chirp',
    version='2.0.2',
    # packages=['wwara_chirp'],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    url='https://github.com/tsayles/wwara-chirp.git',
    license='MIT',
    author='Tom Sayles (KE4HET)',
    author_email='tsayles@Soot-n-Smoke.com',
    description='WWARA CHIRP Export Script Update',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research'
        'Intended Audience :: Other Audience', # Amateur Radio Operators
        'Topic :: Communications :: Ham Radio',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],

    python_requires='>=3.6',
    keywords='WWARA CHIRP',
    project_urls={
        'Bug Reports': 'https://github.com/tsayles/wwara-chirp/issues',
        'Source': 'https://github.com/tsayles/wwara-chirp',
    },
    entry_points={
        'console_scripts': [
            'wwara_chirp=wwara_chirp:main',
        ],
    },
)