# py3dtiles-mod

Python tools for converting LAS point clouds to [3D Tiles](https://www.ogc.org/standards/3dtiles/).

[中文](./README.md)

Original project: [Oslandia/py3dtiles](https://gitlab.com/Oslandia/py3dtiles)

## Requirements

- Python 3.10 or later;
- NumPy 2.0 or later;
- laspy 2.6 or later;
- A Python installation with the standard-library `tkinter` module to use the Windows GUI.

Basic point-cloud conversion does not require PostgreSQL. Install the optional `postgis` dependency group only when the `export` command must access PostgreSQL/PostGIS.

## Installation

Install the project from the current directory:

```powershell
python -m pip install .
```

Install it in editable mode with test dependencies:

```powershell
python -m pip install -e '.[test]'
```

Install the optional PostgreSQL/PostGIS dependency for `export`:

```powershell
python -m pip install '.[postgis]'
```

## Command-Line Conversion

Run `py3dtiles --help` for all commands. The basic LAS-to-3D-Tiles conversion is:

```powershell
py3dtiles convert input.las --out .\3dtiles --srs_in 4547 --srs_out 4978
```

For example, convert `D:\tmp\merge4.las` from EPSG:4547 to the Earth-centered, Earth-fixed EPSG:4978 coordinate reference system commonly used by Cesium, with four parallel workers:

```powershell
py3dtiles convert D:\tmp\merge4.las --out D:\tmp\merge4-3dtiles --srs_in 4547 --srs_out 4978 --jobs 4
```

The entry point is `D:\tmp\merge4-3dtiles\tileset.json`. When `--out` already exists, pass `--overwrite true` to recreate the directory.

Use `--srs_in` to specify the input point cloud CRS; it can be omitted when the LAS file contains a CRS. EPSG numeric codes (such as `4547`), `EPSG:4547`, PROJ strings, and `.prj` file paths are supported. Point-cloud coordinates are always interpreted as X=easting and Y=northing, preventing misplaced output caused by EPSG axis-order rules.

## Graphical Interface

After installation, run:

```powershell
PointCloudConverter
```

Or launch it directly from the source directory:

```powershell
python -m py3dtiles.point_cloud_convert
```

The tkinter interface accepts one or more `.las` files, EPSG/PROJ coordinate systems, and `.prj` files. The coordinate-system field displays a format hint when it is empty. After selecting an output directory, results are written to its `output` subdirectory, with the entry point at `output\tileset.json`.


## Main Changes

1. Migrated LAS reading to the laspy 2.x API and reads embedded LAS coordinate systems;
2. Added NumPy 2.x support;
3. Uses `pyproj` for CRS transformations with a fixed X/Y axis order;
4. Add user interface with standard-library tkinter;
5. Made PostgreSQL/PostGIS support an optional dependency;
6. Uses TCP for Windows process communication.
