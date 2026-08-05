# py3dtiles-mod
Convert LAS point cloud data to 3DTiles

Original code repository: [https://gitlab.com/Oslandia/py3dtiles](https://gitlab.com/Oslandia/py3dtiles)



Modification notes:

1. Modified `setup.py` to require `laspy` version < 2, otherwise LAS files cannot be read;
2. Modified `zmq` related code to use TCP protocol, otherwise it cannot run on Windows;
3. Added support for custom coordinate systems, supporting EPSG codes, proj4 strings, and prj projection files;
4. A warning is given when the output coordinate system is not 4978. (It seems that when loading in Cesium, if it's not 4978, it can't find where it is. I don't know Cesium, maybe there are other solutions);
5. Added a GUI interface for point cloud conversion, just execute the `PointCloudConverter` command afterwards.
