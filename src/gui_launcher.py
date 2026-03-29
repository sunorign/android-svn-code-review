#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GUI 启动器 - 图形化界面选择项目并启动代码审查。"""

import os
import sys
import tkinter
from tkinter import filedialog, messagebox, ttk
import webbrowser
import subprocess
import logging
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class CodeReviewGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperPower Code Review")
        self.root.geometry("500x280")
        self.root.resizable(False, False)

        # 选中的项目目录
        self.project_dir = tkinter.StringVar()

        # 是否进行全文AI审查
        self.enable_ai = tkinter.BooleanVar(value=True)

        self.create_widgets()

    def create_widgets(self):
        # 标题
        title_label = ttk.Label(
            self.root,
            text="SuperPower Code Review",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(15, 5))

        subtitle = ttk.Label(
            self.root,
            text="Android SVN 自动化代码审查工具"
        )
        subtitle.pack(pady=(0, 20))

        # 项目目录选择
        frame1 = ttk.Frame(self.root)
        frame1.pack(fill='x', padx=20, pady=5)

        ttk.Label(frame1, text="项目目录:").pack(anchor='w')

        dir_frame = ttk.Frame(frame1)
        dir_frame.pack(fill='x', pady=5)

        entry = ttk.Entry(dir_frame, textvariable=self.project_dir)
        entry.pack(side='left', fill='x', expand=True, padx=(0, 5))

        browse_btn = ttk.Button(dir_frame, text="浏览...", command=self.browse_dir)
        browse_btn.pack(side='right')

        # AI审查选项
        ai_frame = ttk.Frame(frame1)
        ai_frame.pack(fill='x', pady=10)

        ai_check = ttk.Checkbutton(
            ai_frame,
            text="启用全文AI审查（需要配置API密钥）",
            variable=self.enable_ai
        )
        ai_check.pack(anchor='w')

        # 开始按钮
        start_btn = ttk.Button(
            self.root,
            text="开始代码审查",
            command=self.start_review,
            style='Accent.TButton'
        )
        start_btn.pack(pady=20, fill='x', padx=20)

        # 状态栏
        self.status = ttk.Label(self.root, text="就绪，请选择项目目录", foreground='gray')
        self.status.pack(pady=(0, 10))

    def browse_dir(self):
        directory = filedialog.askdirectory(
            title="选择 Android 项目根目录",
            mustexist=True
        )
        if directory:
            self.project_dir.set(directory)
            self.status.config(text=f"已选择: {os.path.basename(directory)}")

    def check_svn(self, directory: str) -> bool:
        """检查是否是 SVN 工作副本。"""
        return os.path.exists(os.path.join(directory, '.svn'))

    def start_review(self):
        directory = self.project_dir.get().strip()
        if not directory or not os.path.isdir(directory):
            messagebox.showerror("错误", "请选择有效的项目目录")
            return

        if not self.check_svn(directory):
            result = messagebox.askyesno(
                "警告",
                "该目录不是 SVN 工作副本，无法获取变更列表。\n是否继续尝试审查目录中所有 Java 文件？\n（此功能尚未实现）"
            )
            if not result:
                return

        self.status.config(text="正在运行代码审查...")
        self.root.update()

        # 运行主程序
        try:
            # 切换工作目录
            os.chdir(directory)

            # 导入并运行main
            from src.main import main
            main()

            # 查找最新生成的HTML报告
            report_dir = os.path.join(directory, 'code-review-output')
            if os.path.exists(report_dir):
                html_files = [
                    f for f in os.listdir(report_dir)
                    if f.endswith('.html') and f.startswith('review-result')
                ]
                if html_files:
                    # 按修改时间排序，最新的在最后
                    html_files.sort(
                        key=lambda f: os.path.getmtime(os.path.join(report_dir, f))
                    )
                    latest_html = os.path.join(report_dir, html_files[-1])
                    # 用浏览器打开
                    webbrowser.open(f'file://{latest_html}')
                    messagebox.showinfo(
                        "完成",
                        f"代码审查完成!\n报告已在浏览器打开:\n{latest_html}"
                    )
                else:
                    messagebox.showinfo(
                        "完成",
                        "代码审查完成，未发现问题，未生成报告。"
                    )
            else:
                messagebox.showinfo("完成", "代码审查完成！")

            self.status.config(text="完成")

        except Exception as e:
            error_msg = f"代码审查过程中出错:\n{str(e)}"
            logging.error(error_msg, exc_info=True)
            messagebox.showerror("错误", error_msg)
            self.status.config(text="出错了", foreground='red')


def main():
    # 检查tkinter是否可用
    try:
        import tkinter
    except ImportError:
        print("错误: 当前 Python 安装不包含 tkinter，请重新安装 Python 并确保勾选 tcl/tk 选项")
        sys.exit(1)

    root = tkinter.Tk()
    app = CodeReviewGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()