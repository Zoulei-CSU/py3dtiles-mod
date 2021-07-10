# -*- coding: utf-8 -*-
"""
Created on  15:56:54 2021-07-09

@author: Zoulei
"""
import sys

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

def getPixmapFromStr(base64_str:str, format:str = 'png') -> QtGui.QPixmap:
    if base64_str is None:
        return None
    if format is None:
        format = 'png'
    ba = QByteArray(base64_str.encode())
    ba = QByteArray.fromBase64(ba)
    pix = QPixmap()
    isOk = pix.loadFromData(ba, format)
    if isOk:
        return pix
    return None

class Ui_PointCloudConverter(object):
    def setupUi(self, MainForm):
        if not MainForm.objectName():
            MainForm.setObjectName(u"MainForm")
        MainForm.resize(653, 399)
        self.gridLayout = QGridLayout(MainForm)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_las_files = QLabel(MainForm)
        self.label_las_files.setObjectName(u"label_las_files")
        self.label_las_files.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout.addWidget(self.label_las_files, 0, 0, 1, 1)

        self.listWidget_las_files = QListWidget(MainForm)
        self.listWidget_las_files.setObjectName(u"listWidget_las_files")

        self.gridLayout.addWidget(self.listWidget_las_files, 0, 1, 1, 1)

        self.label_srs = QLabel(MainForm)
        self.label_srs.setObjectName(u"label_srs")
        self.label_srs.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout.addWidget(self.label_srs, 1, 0, 1, 1)

        self.lineEdit_out = QLineEdit(MainForm)
        self.lineEdit_out.setObjectName(u"lineEdit_out")

        self.gridLayout.addWidget(self.lineEdit_out, 3, 1, 1, 1)

        self.pushButton_run = QPushButton(MainForm)
        self.pushButton_run.setObjectName(u"pushButton_run")

        self.gridLayout.addWidget(self.pushButton_run, 4, 2, 1, 1)

        self.plainTextEdit_srs = QPlainTextEdit(MainForm)
        self.plainTextEdit_srs.setObjectName(u"plainTextEdit_srs")

        self.gridLayout.addWidget(self.plainTextEdit_srs, 1, 1, 1, 1)

        self.label_out = QLabel(MainForm)
        self.label_out.setObjectName(u"label_out")

        self.gridLayout.addWidget(self.label_out, 3, 0, 1, 1)

        self.pushButton_out = QPushButton(MainForm)
        self.pushButton_out.setObjectName(u"pushButton_out")

        self.gridLayout.addWidget(self.pushButton_out, 3, 2, 1, 1)

        self.pushButton_las_files = QPushButton(MainForm)
        self.pushButton_las_files.setObjectName(u"pushButton_las_files")

        self.gridLayout.addWidget(self.pushButton_las_files, 0, 2, 1, 1)

        self.pushButton_srs = QPushButton(MainForm)
        self.pushButton_srs.setObjectName(u"pushButton_srs")

        self.gridLayout.addWidget(self.pushButton_srs, 1, 2, 1, 1)

        self.horizontalSlider_chouxi = QSlider(MainForm)
        self.horizontalSlider_chouxi.setObjectName(u"horizontalSlider_chouxi")
        self.horizontalSlider_chouxi.setEnabled(False)
        self.horizontalSlider_chouxi.setMinimum(1)
        self.horizontalSlider_chouxi.setMaximum(100)
        self.horizontalSlider_chouxi.setValue(100)
        self.horizontalSlider_chouxi.setOrientation(Qt.Horizontal)
        self.horizontalSlider_chouxi.setTickPosition(QSlider.TicksBelow)
        self.horizontalSlider_chouxi.setTickInterval(10)

        self.gridLayout.addWidget(self.horizontalSlider_chouxi, 2, 1, 1, 1)

        self.label_chouxi = QLabel(MainForm)
        self.label_chouxi.setObjectName(u"label_chouxi")

        self.gridLayout.addWidget(self.label_chouxi, 2, 0, 1, 1)

        self.label_chouxi_2 = QLabel(MainForm)
        self.label_chouxi_2.setObjectName(u"label_chouxi_2")

        self.gridLayout.addWidget(self.label_chouxi_2, 2, 2, 1, 1)

        self.gridLayout.setRowStretch(0, 2)
        self.gridLayout.setRowStretch(1, 1)

        MainForm.setWindowTitle(u"点云数据转3DTiles -- Zoulei")
        self.label_las_files.setText(u"点云数据：")
        self.label_srs.setText(u"点云坐标系：")
        self.lineEdit_out.setPlaceholderText(u"选择输出文件夹")
        self.pushButton_run.setText(u"转 换 >>")
        self.plainTextEdit_srs.setPlainText(u"+proj=tmerc +lat_0=0 +lon_0=114.3333333333333 +k=1 +x_0=800000 +y_0=-3000000 +ellps=GRS80 +units=m +no_defs ")
        self.plainTextEdit_srs.setPlaceholderText(u"这里写EPSG代码，或者proj4坐标系描述字符串，或者打开prj投影文件。")
        self.label_out.setText(u"输出路径：")
        self.pushButton_out.setText(u"浏览...")
        self.pushButton_las_files.setText(u"添加点云...")
        self.pushButton_srs.setText(u"打开prj...")
        self.label_chouxi.setText(u"抽稀比例：")
        self.label_chouxi_2.setText(u"100%")

        QMetaObject.connectSlotsByName(MainForm)
    # setupUi

class PointCloudConverter(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.ui = Ui_PointCloudConverter()
        self.ui.setupUi(self)

    @QtCore.Slot()
    def on_pushButton_out_clicked(self):
        file = QFileDialog.getExistingDirectory(self, u"选择输出文件夹")
        if len(file) > 1:
            self.ui.lineEdit_out.setText(file)

    @QtCore.Slot()
    def on_pushButton_las_files_clicked(self):
        files = QFileDialog.getOpenFileNames(self, u"打开点云文件", None, u"点云数据(*.las)")
        files = files[0]
        for file in files:
            self.ui.listWidget_las_files.addItem(file)

    @QtCore.Slot()
    def on_pushButton_srs_clicked(self):
        file = QFileDialog.getOpenFileName(self, u"打开投影文件", None, u"投影文件(*.prj)")
        file = file[0]
        if len(file) > 1:
            with open(file, 'r') as f:
                prj_str = f.read()
                self.ui.plainTextEdit_srs.setPlainText(str(prj_str).strip(' '))
                self.ui.plainTextEdit_srs.setToolTip(file)

    @QtCore.Slot()
    def on_pushButton_run_clicked(self):
        files = []
        for i in range(self.ui.listWidget_las_files.count()):
            files.append(self.ui.listWidget_las_files.item(i).text())
        if len(files) == 0:
            QMessageBox.critical(self, '错误', '请先添加需要转换的点云数据！')
            return
        
        out_dir = self.ui.lineEdit_out.text()
        if len(out_dir) == 0:
            QMessageBox.critical(self, '错误', '需指定3DTiles的输出路径！')
            return

        srs = self.ui.plainTextEdit_srs.toPlainText()
        if len(srs) < 1:
            QMessageBox.critical(self, '错误', '必须指定点云数据的原始坐标系！')
            return

        if srs.startswith('+proj'):
            pass
        elif srs.startswith('epsg:'):
            pass
        elif srs.startswith('PROJCS'):
            srs = self.ui.plainTextEdit_srs.toolTip()
        elif srs.isnumeric():
            pass
        else:
             QMessageBox.critical(self, '错误', '未识别的坐标系！')
             return

        self.ui.pushButton_run.setEnabled(False)
        self.convert(files, out_dir, srs)

    def convert(self, fileList, output, srs):
        import psutil
        from py3dtiles.convert import convert
        total_memory_MB = int(psutil.virtual_memory().total / (1024 * 1024))
        if not output.endswith('/'):
            output = output + '/'
        output = output + '/output'
        convert(files=fileList, outfolder=output, cache_size=total_memory_MB, srs_out='4978', srs_in=srs)


def main():
    app = QApplication(sys.argv)
    window = PointCloudConverter(None)

    #设置图标
    logo_png_str = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANKSURBVEiJtZU9bxxFHMZ/M/ty3tuNcznAUhIcn2RLWNg4ISCEIiW0NDQoFZ+AhiYV34GXnsoFLQUUhI4GS0gRFRISKDoCUQS2dXD2eXdm93ZnhuJ8lzuvzwYBT7Or0ezz+7/M/Bf+Z4nxc3d395M4jt/6t4bWWtXr9d5bXV29D+Afr0dRFN0VQlw63oSUkpPvf0ee52GtfRuYBRhjnBCCsixpNps450apCYFSiiAIzjSeDiJNU8eoOm4MEABKKRqNBkVRTD6oqopHj3/j+58eI4TgNHlScu3yM7xyfR0hBM45cRIAwNHREdZaoiiarJVlidKaTz/7Cim9uRncfm2T6xtrtUxnAEophBAYY0iSBGMMaZpSDXPefedNGo2FuYCV5cunlnEGsLCwQL/fJ4oiDg8PgVGTL8QRN7Y2CcOwZjDdq9M0A2i1WmRZxmAwwPM8nHNYa2m327XoyrIkiiKklDjn0FrjeV4NNAOIoohL7TY/dPfJiyFCSMIwpMoC/vzlYLLPViXrnTbD4XACkFKSZRlJkswHADz6w+ejB2uUZQlCIr0GnIjq5ef2ef9KgX98GEZHWaO1Jo7jswGhD1XWoyhr5Zyozx55/jxhGE4yyIscrTVVVZ0NeKlzgS/uNee7A93uIVmWURQFURQxHA6pqoosy87uwThd3x8tj2srpcQYg3MOIQTtdpu9vT3CMERrjbV2MgHG34516pCx1qKUwvM8PG90uYIgGJUiz0mShMXFRcqyJE1TiqIgSRKWlpZqXvUm/57y7a8BV5OCWy8E+L6PEIKqqrDW8uXXD9jvZ1hryLXGGkMQ+Ly6tcby8vL5gCd9wwf3LffupNy4FnBx8en511rT7f7MN9/9WDNypuL1m5u1EtUAW52Yj+8OKA4HFHkD5Y/uglIKrTUvrl3ljVs3a4ClZ9s18xmAtXY0FhYkdzYu8vDhPoPBAK31ZHOe52ysr7GyslIzGnvMBWRZVk6Pg2azSa/XA5icIt/3abVaKKVOBYyllJpchjHA7OzsfNjpdG5PRSMODg6CPM+lMUZ4nufiODZSyjOuIADl9vb254CDp//kBnAFqI/LURAeUAHmHPOxMuDJNACgOQfwT+UADQz/A6/z9RcwxHY0GcyfyAAAAABJRU5ErkJggg=="
    pix = getPixmapFromStr(base64_str=logo_png_str, format='png')
    if pix:
        window.setWindowIcon(QIcon(pix))

    window.show()
    app.exec_()
    sys.exit()

if __name__ == '__main__':
    main()