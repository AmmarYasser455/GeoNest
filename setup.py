from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geonest",
    version="0.1.0",
    author="Ammar Yasser",
    description="Interactive Python Map library for GIS using ipyleaflet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[
        "ipyleaflet",
        "ipywidgets",
        "geopandas",
        "localtileserver",
    ],
    license="MIT",
)
