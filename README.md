# py3dtiles-mod
las点云数据转换3DTiles

原始代码库地址：[https://gitlab.com/Oslandia/py3dtiles](https://gitlab.com/Oslandia/py3dtiles)





修改记录：

1. 修改setup.py，要求laspy版本小于2，否则无法读取las文件；
2. 修改zmq部分代码，修改为TCP协议，否则在Windows下无法执行；
3. 添加对自定义坐标系的支持，可以支持EPSG代码、proj4字符串、prj投影文件；
4. 当输出坐标系不是4978时，给出警告。（貌似在Cesium中加载，不是4978时找不到在那里，我不懂Cesium，可能有其他解决办法吧）；
5. 添加一个点云转换的GUI界面，按照后执行PointCloudConverter命令即可。



