# Georise

`Georise` is a Python library built for interactive visualization of geospatial maps. It leverages the power of GDAL and PyQtGraph to provide a user-friendly, high-performance mapping solution. With its simple, Matplotlib-like API, it aims to make geospatial visualization accessible, easy, and beautiful.

**Please note:** Georise is currently in early development and may not be suitable for major use. However, it is being actively developed and improved every day.

### Features

- Interactive visualization of geospatial maps
- Handles map distortion, latitude and longitude, and correct multi-dimensional scaling
- Supports raster type files such as GeoTIFF and DTED (with plans to support point cloud and LIDAR data types)
- Simple, familiar API for ease of use

### Installation
Before installing Georise, you will need to install the following dependencies:

- OSGeo (which includes GDAL)
- PyQt5

Please consult the respective documentation for detailed installation instructions for your operating system. With the prerequisites installed, you can install georise using pip:
```bash
pip install georise
```

The following example demonstrates how to use Georise to display a raster terrain from a GeoTIFF file.


```python
import georise.scene

if __name__ == '__main__':
    # Instantiate the scene
    gplt = georise.scene.GRRasterScene()

    # Add terrains from filepath (use skip to save on memory)
    gplt.raster("test_raster.tif", skip=4)

    # Show rasters using a matplotlib-like API
    gplt.show()
```

### Documentation
More detailed documentation will be provided as the project matures. Keep an eye on this space for updates!

### Contributing
Georise is an open-source project, and contributions are welcome! If you'd like to report a bug, request a feature, or contribute code, please use the GitHub repository to submit issues or pull requests.

### License
Georise is released under the MIT License.
