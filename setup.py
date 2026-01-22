from setuptools import setup, find_packages

setup(
    name="geonest",
    version="0.1.0",
    description="Interactive Python Map library for GIS using ipyleaflet",
    author="Ammar Yasser",
    author_email="ammaryasr522@gmail.com",
    packages=find_packages(),
    install_requires=[
        "ipyleaflet>=0.17.0",
        "ipywidgets>=8.0.0",
        "geopandas>=0.13.0",
        "shapely>=2.1.0",
        "localtileserver>=0.2.0"
    ],
    python_requires='>=3.10',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

license="MIT",
