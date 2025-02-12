from setuptools import setup, find_packages

setup(
    name="common-utils",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # List any dependencies here, e.g., requests or Flask
        "Flask>=2.0",
        "requests>=2.25.1"
    ],
)
