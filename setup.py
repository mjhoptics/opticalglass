import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="opticalglass",
    version="0.5.0",
    author="Michael J Hayford",
    author_email="mjhoptics@gmail.com",
    description="Tools for reading commercial optical glass catalogs",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="BSD-3-Clause",
    url="https://github.com/mjhoptics/opticalglass",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords=['glass', 'optical glass', 'refractive index', 'optics',
              'glass catalog'],
    install_requires=[
        "xlrd>=1.1.0",
        "numpy>=1.17.1",
        "scipy>=1.3.1",
        "matplotlib>=3.1.1",
        "pyqt5==5.9.2"
        ],
    package_data={
        '': ['data/*.xlsx', 'data/*.xls', 'data/*.txt']
        },
    entry_points={
        'gui_scripts': [
            'glassmap = opticalglass.glassmapviewer:main',
        ],
    },
)
