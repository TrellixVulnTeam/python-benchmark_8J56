from setuptools import setup, find_packages

# do not work well in 'python setup.py bdist_rpm'
# with open('./README.md') as f:
#     long_description = f.read()

setup(
    name='benchmark',
    version='0.1.0',
    description='benchmark testing tools',
    long_description="",
    # install_requires=['flask', 'flask_cors', 'flask_restful', 'pymongo'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'benchmark_api = benchmark.app:run'
        ]
    }
)
