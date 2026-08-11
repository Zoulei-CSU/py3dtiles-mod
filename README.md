# py3dtiles-mod

将 LAS 点云数据转换为 [3D Tiles](https://www.ogc.org/standards/3dtiles/) 的 Python 工具。

[English](./README.en-US.md)

原始代码库：[Oslandia/py3dtiles](https://gitlab.com/Oslandia/py3dtiles)

## 环境要求

- Python 3.10 或更高版本；
- NumPy 2.0 或更高版本；
- laspy 2.6 或更高版本；
- Windows 上使用图形界面时，Python 应包含标准库 `tkinter`。

基础点云转换不依赖 PostgreSQL。`export` 命令需要连接 PostgreSQL/PostGIS 时，再安装可选的 `postgis` 依赖组。

## 安装

安装当前目录中的项目：

```powershell
python -m pip install .
```

以可编辑模式安装，并同时安装测试依赖：

```powershell
python -m pip install -e '.[test]'
```

需要使用 PostgreSQL/PostGIS 的 `export` 命令时：

```powershell
python -m pip install '.[postgis]'
```

## 命令行转换

执行 `py3dtiles --help` 可查看全部命令。将 LAS 文件转换为 3D Tiles 的基本形式如下：

```powershell
py3dtiles convert input.las --out .\3dtiles --srs_in 4547 --srs_out 4978
```

例如，将 `D:\tmp\merge4.las`（EPSG:4547）转换为 Cesium 常用的地心地固坐标系 EPSG:4978，并启动 4 个并行任务：

```powershell
py3dtiles convert D:\tmp\merge4.las --out D:\tmp\merge4-3dtiles --srs_in 4547 --srs_out 4978 --jobs 4
```

生成的入口文件为 `D:\tmp\merge4-3dtiles\tileset.json`。`--out` 已存在时，使用 `--overwrite true` 允许重新创建该目录。

`--srs_in` 用于指定输入点云的坐标系；若 LAS 文件内嵌坐标系，可省略该参数。
支持 EPSG 数字编号（如 `4547`）、`EPSG:4547`、PROJ 字符串和 `.prj` 文件路径。点云坐标始终按 X=东向坐标、Y=北向坐标处理，避免 EPSG 轴顺序造成位置偏移。

## 图形界面

安装完成后运行：

```powershell
PointCloudConverter
```

也可以直接从源码目录启动：

```powershell
python -m py3dtiles.point_cloud_convert
```

界面支持选择一个或多个 `.las` 文件、输入 EPSG/PROJ 坐标系或导入 `.prj` 文件。坐标系输入框在为空时会显示格式示例。选择输出目录后，转换结果写入该目录下的 `output` 子目录，入口文件为 `output\tileset.json`。

## 主要改动

1. 使用 laspy 2.x API 读取 LAS 文件，并支持从 LAS 文件读取内嵌坐标系；
2. 支持 NumPy 2.x；
3. 使用 `pyproj` 进行坐标转换，并固定 X/Y 坐标轴顺序；
4. 增加 Python 标准库 tkinter 图形界面；
5. 将 PostgreSQL/PostGIS 支持改为可选依赖；
6. Windows 下的进程通信使用 TCP 协议。
