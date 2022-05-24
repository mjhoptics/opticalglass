import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="opticalglass",
    version="1.0.0",
    author="Michael J Hayford",
    author_email="mjhoptics@gmail.com",
    description="Tools for reading commercial optical glass catalogs",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="BSD-3-Clause",
    url="https://github.com/mjhoptics/opticalglass",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords=['glass', 'optical glass', 'refractive index', 'optics',
              'glass catalog'],
    install_requires=[
        "numpy>=1.21.5",
        "scipy>=1.7.3",
        "matplotlib>=3.5.1",
        "pandas>=1.3.5",
        "pyqt5<5.13"
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
