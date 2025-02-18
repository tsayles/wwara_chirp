from setuptools import setup

setup(
    name='wwara-chirp',
    version='2.0',
    packages=['wwara-csv-to-chirp-csv'],
    url='https://github.com/tsayles/wwara-chirp.git',
    license='MIT',
    aauthor='Tom Sayles (KE4HET), GitHub Copilot',
    author_email='tsayles@Soot-n-Smoke.com',
    description='WWARA CHIRP Export Script Update',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Amateur Radio Operators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    entry_points={
        'console_scripts': [
            'wwara-chirp=wwara_csv_to_chirp_csv:main',
        ],
    },
    python_requires='>=3.6',
    keywords='WWARA CHIRP',
    project_urls={
        'Bug Reports': 'https://github.com/tsayles/wwara-chirp/issues',
        'Source': 'https://github.com/tsayles/wwara-chirp',
    }
)