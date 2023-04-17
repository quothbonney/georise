from setuptools import setup, find_packages

setup(
    name="georise",
    version="0.0.3",
    author='Jack David Carson',
    author_email='jackdavidcarson@gmail.com',
    long_description_content_type='text/markdown',
    description='A Python Library Built on GDAL for Visualization of Geospatial Maps',
    long_description=open('README.md').read(),
    url='https://github.com/quothbonney/georise',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=[
        'geopy>=2.3.0',
        'matplotlib>=3.4.3',
        'numpy>=1.20.2',
        'pyqtgraph>=0.13.1',
        'rasterio>=1.3.6',
        'setuptools>=44.0.0',
    ],
    python_requires='>=3.6',
)

