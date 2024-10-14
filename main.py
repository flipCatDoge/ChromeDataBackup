import os
import sys
import re
import shutil
import psutil
from tkinter import Tk, Label, Button, filedialog, messagebox, ttk
from threading import Thread
import queue


def resource_path(relative_path):
    """获取资源的路径"""
    try:
        # PyInstaller 创建临时文件夹，然后将文件解压到此文件夹
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ChromeProfileCopier:
    def __init__(self, master):
        self.master = master
        master.title("谷歌数据备份V1.0 Powered by Ben")

        # 设置窗口图标（将 'chrome.ico' 替换为实际图标文件名）
        icon_path = resource_path("chrome.ico")
        master.iconbitmap(icon_path)  # 设置窗口图标
        # 设置窗口大小
        master.geometry("400x150")  # 宽度 x 高度
        # 创建进度条

        self.label = Label(master, text="点击下方按钮进行备份")
        self.label.pack(pady=10)
        self.progress = ttk.Progressbar(
            master, orient="horizontal", length=300, mode="determinate"
        )
        self.progress.pack(pady=10)

        self.copy_button = Button(master, text="开始备份", command=self.start_backup)
        self.copy_button.pack(pady=5)

        self.progress_queue = queue.Queue()  # 创建一个队列用于进度传递

    def is_chrome_running(self):
        # 遍历所有正在运行的进程
        for process in psutil.process_iter(["pid", "name"]):
            try:
                # 检查进程名称是否包含 'chrome'
                if "chrome" in process.info["name"].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def get_chrome_user_data_dir(self):
        if sys.platform == "win32":
            # Windows
            path = os.path.join(
                os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data"
            )
        elif sys.platform == "darwin":
            # macOS
            path = os.path.expanduser("~/Library/Application Support/Google/Chrome")
        elif sys.platform == "linux":
            # Linux
            path = os.path.expanduser("~/.config/google-chrome/")
        else:
            path = None
        return path

    def find_chrome_profiles(self, directory):
        # 匹配 'Profile <数字>' 的正则表达式
        profile_pattern = re.compile(r"Profile \d+")
        # 用于存储匹配的文件夹
        found_profiles = []
        # 遍历目录，查找符合条件的文件夹
        for folder_name in os.listdir(directory):
            folder_path = os.path.join(directory, folder_name)
            if os.path.isdir(folder_path):
                if folder_name == "Default":
                    print(f"Found Default profile: {folder_path}")
                    # found_profiles.append(folder_name)
                elif profile_pattern.match(folder_name):
                    print(f"Found {folder_name} profile: {folder_path}")
                    found_profiles.append(folder_name)
        return found_profiles

    def copy_profiles(
        self, profiles, progressStep, chrome_user_data_dir, destination_dir
    ):
        progressValue = 0

        # 遍历找到的 profiles 文件夹，进行复制
        for profile in profiles:
            source_path = os.path.join(chrome_user_data_dir, profile)
            destination_path = os.path.join(destination_dir, profile)
            try:
                # 遍历源目录，逐个文件复制
                for root, dirs, files in os.walk(source_path):
                    # 创建目标目录
                    relative_path = os.path.relpath(root, source_path)
                    new_destination_path = os.path.join(destination_path, relative_path)
                    if not os.path.exists(new_destination_path):
                        os.makedirs(new_destination_path)

                    # 逐个复制文件并更新进度条
                    for file_name in files:
                        source_file = os.path.join(root, file_name)
                        destination_file = os.path.join(new_destination_path, file_name)
                        shutil.copy2(
                            source_file, destination_file
                        )  # 使用 copy2 保留元数据
                        progressValue = progressValue + 1  # 更新进度条的值
                        if progressValue % progressStep == 0:
                            print(f"Copied {progressValue} files...")
                            self.progress_queue.put(progressValue)  # 将进度放入队列
                print(f"Copied {profile} to {destination_path}")
            except shutil.Error as e:
                print(f"Error copying {profile}: {e}")
            except OSError as e:
                print(f"OS error copying {profile}: {e}")
        # 备份完成后在主线程中提示
        self.progress_queue.put("done")  # 向队列中添加完成标记

    def start_backup(self):
        # 启动线程来执行备份操作
        # 启动进度更新线程
        self.update_progress_thread()
        self.progress["value"] = 0  # 重置进度条的值
        self.progress["maximum"] = 0  # 重置进度条的最大值
        # 选择目标目录
        destination_dir = filedialog.askdirectory(title="选择备份目录")
        if not destination_dir:
            return
        # 禁用按钮
        self.copy_button.config(state="disabled")
        if self.is_chrome_running():
            messagebox.showwarning(
                "Warning",
                "谷歌浏览器正在运行，请关闭浏览器后再进行操作",
            )
            self.copy_button.config(state="normal")  # 备份完成后重新启用按钮
            return
        chrome_user_data_dir = self.get_chrome_user_data_dir()
        if chrome_user_data_dir is None:
            messagebox.showerror(
                "Error",
                "不支持的平台或无法确定Chrome用户数据目录",
            )
            self.copy_button.config(state="normal")  # 备份完成后重新启用按钮
            return
        profiles = self.find_chrome_profiles(chrome_user_data_dir)
        if not profiles:
            messagebox.showwarning("Warning", "没有需要备份的用户数据")
            self.copy_button.config(state="normal")  # 备份完成后重新启用按钮
            return
        # 统计要复制的所有文件的总数
        progressMax = sum(
            len(files)
            for profile in profiles
            for _, _, files in os.walk(os.path.join(chrome_user_data_dir, profile))
        )
        progressStep = int(progressMax / 50)  # 每次更新进度条的步长
        print(f"progressStep: {progressStep}")
        print(f"progressMax: {progressMax}")
        self.progress["maximum"] = progressMax  # 设置进度条的最大值

        # 在新线程中执行文件复制
        Thread(
            target=self.copy_profiles,
            args=(profiles, progressStep, chrome_user_data_dir, destination_dir),
        ).start()

    def update_progress(self):
        try:
            while True:
                progress_value = self.progress_queue.get_nowait()  # 获取队列中的进度值
                if progress_value == "done":  # 检查是否为完成标记
                    self.copy_button.config(state="normal")  # 备份完成后重新启用按钮
                    messagebox.showinfo("Completed", "数据备份完成!")
                    return
                else:
                    self.progress["value"] = progress_value  # 更新进度条的值
        except queue.Empty:
            pass
        self.master.after(100, self.update_progress)  # 每 100 毫秒更新一次进度

    def update_progress_thread(self):
        self.master.after(100, self.update_progress)  # 启动定时器来更新进度


if __name__ == "__main__":
    root = Tk()
    app = ChromeProfileCopier(root)
    root.mainloop()
