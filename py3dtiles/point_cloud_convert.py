"""A small tkinter front end for converting LAS files to 3D Tiles."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class TextPlaceholder:
    """Display non-input guidance in an otherwise empty tkinter Text widget."""

    placeholder_color = "#777777"
    input_color = "#000000"

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.visible = False

    def show(self, event=None):
        if self.value() or self.visible:
            return
        self.widget.insert("1.0", self.text)
        self.widget.configure(foreground=self.placeholder_color)
        self.visible = True

    def clear(self, event=None):
        if self.visible:
            self.widget.delete("1.0", tk.END)
            self.visible = False
        self.widget.configure(foreground=self.input_color)

    def restore_if_empty(self, event=None):
        if not self.widget.get("1.0", tk.END).strip():
            self.show()

    def value(self):
        if self.visible:
            return ""
        return self.widget.get("1.0", tk.END).strip()


class PointCloudConverter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("点云转换为 3D Tiles")
        self.minsize(760, 430)

        self.output_var = tk.StringVar()
        self.srs_var = tk.StringVar(
            value="+proj=tmerc +lat_0=0 +lon_0=114.3333333333333 "
            "+k=1 +x_0=800000 +y_0=-3000000 +ellps=GRS80 +units=m +no_defs"
        )
        self._build_form()

    def _build_form(self):
        frame = ttk.Frame(self, padding=12)
        frame.grid(sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)

        ttk.Label(frame, text="点云文件\n（仅支持 .las）").grid(row=0, column=0, sticky="nw")
        self.files_list = tk.Listbox(frame, height=8)
        self.files_list.grid(row=0, column=1, sticky="nsew", padx=(12, 8))
        ttk.Button(frame, text="添加...", command=self._select_files).grid(
            row=0, column=2, sticky="n"
        )

        ttk.Label(frame, text="输入坐标系").grid(row=1, column=0, sticky="nw", pady=(12, 0))
        self.srs_entry = tk.Text(frame, height=5, wrap="word")
        self.srs_entry.insert("1.0", self.srs_var.get())
        self.srs_entry.grid(row=1, column=1, sticky="ew", padx=(12, 8), pady=(12, 0))
        self.srs_placeholder = TextPlaceholder(
            self.srs_entry,
            "例如：EPSG:4547、4547、PROJ 字符串或 .prj 文件内容",
        )
        self.srs_entry.bind("<FocusIn>", self.srs_placeholder.clear)
        self.srs_entry.bind("<FocusOut>", self.srs_placeholder.restore_if_empty)
        ttk.Label(
            frame,
            text="支持 EPSG 编号、PROJ 字符串或 .prj 文件内容",
            foreground="#555555",
        ).grid(row=2, column=1, sticky="w", padx=(12, 8), pady=(4, 0))
        ttk.Button(frame, text="导入 .prj...", command=self._load_prj).grid(
            row=1, column=2, sticky="n", pady=(12, 0)
        )

        ttk.Label(frame, text="输出目录").grid(row=3, column=0, sticky="w", pady=(12, 0))
        ttk.Entry(frame, textvariable=self.output_var).grid(
            row=3, column=1, sticky="ew", padx=(12, 8), pady=(12, 0)
        )
        ttk.Button(frame, text="浏览...", command=self._select_output).grid(
            row=3, column=2, sticky="ew", pady=(12, 0)
        )
        ttk.Label(frame, text="转换结果将写入所选目录下的 output 子目录", foreground="#555555").grid(
            row=4, column=1, sticky="w", padx=(12, 8), pady=(4, 0)
        )

        self.convert_button = ttk.Button(frame, text="开始转换", command=self._run_conversion)
        self.convert_button.grid(row=5, column=2, sticky="e", pady=(16, 0))

    def _select_files(self):
        files = filedialog.askopenfilenames(
            parent=self,
            title="选择点云文件",
            filetypes=[("LAS 点云文件", "*.las"), ("所有文件", "*.*")],
        )
        for filename in files:
            self.files_list.insert(tk.END, filename)

    def _load_prj(self):
        filename = filedialog.askopenfilename(
            parent=self,
            title="打开投影文件",
            filetypes=[("投影文件", "*.prj"), ("所有文件", "*.*")],
        )
        if not filename:
            return
        try:
            projection = Path(filename).read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            projection = Path(filename).read_text(encoding="gbk").strip()
        except OSError as error:
            messagebox.showerror("无法打开投影文件", str(error), parent=self)
            return
        self.srs_placeholder.clear()
        self.srs_entry.delete("1.0", tk.END)
        self.srs_entry.insert("1.0", projection)

    def _select_output(self):
        directory = filedialog.askdirectory(parent=self, title="选择输出目录")
        if directory:
            self.output_var.set(directory)

    def _run_conversion(self):
        files = list(self.files_list.get(0, tk.END))
        output = self.output_var.get().strip()
        srs = self.srs_placeholder.value()

        if not files:
            messagebox.showerror("缺少点云文件", "请至少选择一个 LAS 文件。", parent=self)
            return
        if not output:
            messagebox.showerror("缺少输出目录", "请选择输出目录。", parent=self)
            return
        if not self._is_srs_value(srs):
            messagebox.showerror(
                "无效的坐标系",
                "请输入 EPSG 编号、PROJ 字符串或 .prj 文件内容。",
                parent=self,
            )
            return

        self.convert_button.state(["disabled"])
        self.update_idletasks()
        try:
            self.convert(files, output, srs)
        except Exception as error:
            messagebox.showerror("转换失败", str(error), parent=self)
        else:
            messagebox.showinfo("转换完成", "3D Tiles 已写入输出目录。", parent=self)
        finally:
            self.convert_button.state(["!disabled"])

    @staticmethod
    def _is_srs_value(value):
        lower_value = value.lower()
        return (
            value.isdecimal()
            or lower_value.startswith("epsg:")
            or lower_value.startswith("+proj")
            or value.startswith(("PROJCS", "GEOGCS", "COMPOUNDCRS", "PROJCRS", "GEODCRS"))
        )

    @staticmethod
    def convert(files, output, srs):
        import psutil
        from py3dtiles.convert import convert

        total_memory_mb = int(psutil.virtual_memory().total / (1024 * 1024))
        convert(
            files=files,
            outfolder=str(Path(output) / "output"),
            cache_size=total_memory_mb,
            srs_out="4978",
            srs_in=srs,
        )


def main():
    app = PointCloudConverter()
    app.mainloop()


if __name__ == "__main__":
    main()
