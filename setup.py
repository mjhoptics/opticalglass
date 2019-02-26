import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="opticalglass",
    version="0.3.3",
    author="Michael J Hayford",
    author_email="mjhoptics@gmail.com",
    description="Tools for reading commercial optical glass catalogs",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="BSD-3-Clause",
    url="https://github.com/mjhoptics/opticalglass",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords=['glass', 'optical glass', 'refractive index', 'optics',
              'glass catalog'],
    install_requires=[
        "xlrd>=1.1.0",
        "numpy>=1.15.0",
        "matplotlib>=2.2.3",
        "pyqt5>=9.5.2"
        ],
    package_data={
        '': ['data/*.xlsx', 'data/*.xls']
        },
    entry_points={
        'gui_scripts': [
            'glassmap = opticalglass.qtgui.glassmapviewer:main',
        ],
    },
)
