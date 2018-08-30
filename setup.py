import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="opticalglass",
    version="0.1.5",
    author="Michael J Hayford",
    author_email="mjhoptics@gmail.com",
    description="Tools for reading commercial optical glass catalogs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD-3-Clause",
    url="https://github.com/mjhoptics/opticalglass",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "xlrd>=1.1.0",
        "numpy>=1.15.0",
        ],
    data_files=[
        ('', ['*.xlsx', '*.xls']),
        ],
)
