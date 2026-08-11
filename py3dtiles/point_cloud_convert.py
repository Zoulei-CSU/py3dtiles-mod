"""A small tkinter front end for converting LAS files to 3D Tiles."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


UI_TEXT = {
    "zh_CN": {
        "window_title": "点云转换为 3D Tiles",
        "switch_language": "English",
        "files_label": "点云文件\n（仅支持 .las）",
        "add_files": "添加...",
        "srs_label": "输入坐标系",
        "srs_placeholder": "例如：EPSG:4547、4547、PROJ 字符串或 .prj 文件内容",
        "srs_hint": "支持 EPSG 编号、PROJ 字符串或 .prj 文件内容",
        "import_prj": "导入 .prj...",
        "output_label": "输出目录",
        "browse": "浏览...",
        "output_hint": "转换结果将写入所选目录下的 output 子目录",
        "convert": "开始转换",
        "select_files_title": "选择点云文件",
        "las_files": "LAS 点云文件",
        "all_files": "所有文件",
        "open_prj_title": "打开投影文件",
        "projection_files": "投影文件",
        "select_output_title": "选择输出目录",
        "open_prj_error_title": "无法打开投影文件",
        "missing_files_title": "缺少点云文件",
        "missing_files_message": "请至少选择一个 LAS 文件。",
        "missing_output_title": "缺少输出目录",
        "missing_output_message": "请选择输出目录。",
        "invalid_srs_title": "无效的坐标系",
        "invalid_srs_message": "请输入 EPSG 编号、PROJ 字符串或 .prj 文件内容。",
        "conversion_failed_title": "转换失败",
        "conversion_complete_title": "转换完成",
        "conversion_complete_message": "3D Tiles 已写入输出目录。",
    },
    "en_US": {
        "window_title": "Point Cloud to 3D Tiles",
        "switch_language": "中文",
        "files_label": "Point cloud files\n(.las only)",
        "add_files": "Add...",
        "srs_label": "Input CRS",
        "srs_placeholder": "For example: EPSG:4547, 4547, a PROJ string, or .prj content",
        "srs_hint": "EPSG codes, PROJ strings, and .prj file contents are supported",
        "import_prj": "Import .prj...",
        "output_label": "Output directory",
        "browse": "Browse...",
        "output_hint": "Results will be written to the output subdirectory",
        "convert": "Convert",
        "select_files_title": "Select point cloud files",
        "las_files": "LAS point cloud files",
        "all_files": "All files",
        "open_prj_title": "Open projection file",
        "projection_files": "Projection files",
        "select_output_title": "Select output directory",
        "open_prj_error_title": "Unable to open projection file",
        "missing_files_title": "Point cloud files required",
        "missing_files_message": "Select at least one LAS file.",
        "missing_output_title": "Output directory required",
        "missing_output_message": "Select an output directory.",
        "invalid_srs_title": "Invalid coordinate reference system",
        "invalid_srs_message": "Enter an EPSG code, a PROJ string, or .prj file content.",
        "conversion_failed_title": "Conversion failed",
        "conversion_complete_title": "Conversion complete",
        "conversion_complete_message": "3D Tiles were written to the output directory.",
    },
}

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

    def set_text(self, text):
        self.text = text
        if self.visible:
            self.widget.delete("1.0", tk.END)
            self.widget.insert("1.0", self.text)


class PointCloudConverter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.language = "zh_CN"
        self.minsize(760, 430)

        self.output_var = tk.StringVar()
        self.srs_var = tk.StringVar(
            value="+proj=tmerc +lat_0=0 +lon_0=114.3333333333333 "
            "+k=1 +x_0=800000 +y_0=-3000000 +ellps=GRS80 +units=m +no_defs"
        )
        self._build_form()
        self._apply_language()

    @property
    def text(self):
        return UI_TEXT[self.language]

    def _build_form(self):
        frame = ttk.Frame(self, padding=12)
        frame.grid(sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)

        self.files_label = ttk.Label(frame)
        self.files_label.grid(row=0, column=0, sticky="nw")
        self.files_list = tk.Listbox(frame, height=8)
        self.files_list.grid(row=0, column=1, sticky="nsew", padx=(12, 8))
        self.add_files_button = ttk.Button(frame, command=self._select_files)
        self.add_files_button.grid(
            row=0, column=2, sticky="n"
        )

        self.srs_label = ttk.Label(frame)
        self.srs_label.grid(row=1, column=0, sticky="nw", pady=(12, 0))
        self.srs_entry = tk.Text(frame, height=5, wrap="word")
        self.srs_entry.insert("1.0", self.srs_var.get())
        self.srs_entry.grid(row=1, column=1, sticky="ew", padx=(12, 8), pady=(12, 0))
        self.srs_placeholder = TextPlaceholder(
            self.srs_entry,
            "",
        )
        self.srs_entry.bind("<FocusIn>", self.srs_placeholder.clear)
        self.srs_entry.bind("<FocusOut>", self.srs_placeholder.restore_if_empty)
        self.srs_hint = ttk.Label(frame, foreground="#555555")
        self.srs_hint.grid(row=2, column=1, sticky="w", padx=(12, 8), pady=(4, 0))
        self.import_prj_button = ttk.Button(frame, command=self._load_prj)
        self.import_prj_button.grid(
            row=1, column=2, sticky="n", pady=(12, 0)
        )

        self.output_label = ttk.Label(frame)
        self.output_label.grid(row=3, column=0, sticky="w", pady=(12, 0))
        ttk.Entry(frame, textvariable=self.output_var).grid(
            row=3, column=1, sticky="ew", padx=(12, 8), pady=(12, 0)
        )
        self.browse_button = ttk.Button(frame, command=self._select_output)
        self.browse_button.grid(
            row=3, column=2, sticky="ew", pady=(12, 0)
        )
        self.output_hint = ttk.Label(frame, foreground="#555555")
        self.output_hint.grid(
            row=4, column=1, sticky="w", padx=(12, 8), pady=(4, 0)
        )

        self.convert_button = ttk.Button(frame, command=self._run_conversion)
        self.convert_button.grid(row=5, column=2, sticky="e", pady=(16, 0))

        self.language_button = ttk.Button(frame, command=self._toggle_language)
        self.language_button.grid(row=5, column=0, sticky="w", pady=(16, 0))

    def _apply_language(self):
        text = self.text
        self.title(text["window_title"])
        self.files_label.configure(text=text["files_label"])
        self.add_files_button.configure(text=text["add_files"])
        self.srs_label.configure(text=text["srs_label"])
        self.srs_placeholder.set_text(text["srs_placeholder"])
        self.srs_hint.configure(text=text["srs_hint"])
        self.import_prj_button.configure(text=text["import_prj"])
        self.output_label.configure(text=text["output_label"])
        self.browse_button.configure(text=text["browse"])
        self.output_hint.configure(text=text["output_hint"])
        self.convert_button.configure(text=text["convert"])
        self.language_button.configure(text=text["switch_language"])

    def _toggle_language(self):
        self.language = "en_US" if self.language == "zh_CN" else "zh_CN"
        self._apply_language()

    def _select_files(self):
        files = filedialog.askopenfilenames(
            parent=self,
            title=self.text["select_files_title"],
            filetypes=[(self.text["las_files"], "*.las"), (self.text["all_files"], "*.*")],
        )
        for filename in files:
            self.files_list.insert(tk.END, filename)

    def _load_prj(self):
        filename = filedialog.askopenfilename(
            parent=self,
            title=self.text["open_prj_title"],
            filetypes=[(self.text["projection_files"], "*.prj"), (self.text["all_files"], "*.*")],
        )
        if not filename:
            return
        try:
            projection = Path(filename).read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            projection = Path(filename).read_text(encoding="gbk").strip()
        except OSError as error:
            messagebox.showerror(self.text["open_prj_error_title"], str(error), parent=self)
            return
        self.srs_placeholder.clear()
        self.srs_entry.delete("1.0", tk.END)
        self.srs_entry.insert("1.0", projection)

    def _select_output(self):
        directory = filedialog.askdirectory(parent=self, title=self.text["select_output_title"])
        if directory:
            self.output_var.set(directory)

    def _run_conversion(self):
        files = list(self.files_list.get(0, tk.END))
        output = self.output_var.get().strip()
        srs = self.srs_placeholder.value()

        if not files:
            messagebox.showerror(
                self.text["missing_files_title"], self.text["missing_files_message"], parent=self
            )
            return
        if not output:
            messagebox.showerror(
                self.text["missing_output_title"], self.text["missing_output_message"], parent=self
            )
            return
        if not self._is_srs_value(srs):
            messagebox.showerror(
                self.text["invalid_srs_title"],
                self.text["invalid_srs_message"],
                parent=self,
            )
            return

        self.convert_button.state(["disabled"])
        self.update_idletasks()
        try:
            self.convert(files, output, srs)
        except Exception as error:
            messagebox.showerror(self.text["conversion_failed_title"], str(error), parent=self)
        else:
            messagebox.showinfo(
                self.text["conversion_complete_title"],
                self.text["conversion_complete_message"],
                parent=self,
            )
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
