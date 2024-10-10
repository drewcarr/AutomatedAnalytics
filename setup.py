from setuptools import setup, find_packages

setup(
    name='AutomatedAnalysis',
    version='0.1',
    package_dir={'': 'src'},  # Pointing to the src directory
    packages=find_packages(where='src'),  # Automatically find packages under src/
    install_requires=[],  # Add your dependencies here
)
