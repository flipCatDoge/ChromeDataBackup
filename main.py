import os
import sys
import re
import shutil
import psutil
from tkinter import Tk, Label, Button, filedialog, messagebox, ttk
from threading import Thread
import queue
from loguru import logger

# 配置 loguru 日志记录器
logger.add("backup_log.log", level="DEBUG", format="{time} {level} {message}")


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
        # 启动进度更新线程
        self.update_progress_thread()

    def is_chrome_running(self):
        # 遍历所有正在运行的进程
        for process in psutil.process_iter(["pid", "name"]):
            try:
                # 检查进程名称是否包含 'chrome'
                if "chrome.exe" in process.info["name"].lower():
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
                    logger.debug(f"Found Default profile: {folder_path}")
                    found_profiles.append(folder_name)
                elif profile_pattern.match(folder_name):
                    logger.debug(f"Found {folder_name} profile: {folder_path}")
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
            if not os.path.exists(source_path):
                logger.debug(
                    f"Source path {source_path} does not exist. Skipping {profile}."
                )
                os.copytree(source_path, destination_path)
                continue
            try:
                # 使用 os.makedirs 创建目标目录，并且允许已存在的目录
                os.makedirs(destination_path, exist_ok=True)
                items = os.listdir(source_path)
                for item in items:
                    source_item = os.path.join(source_path, item)
                    destination_item = os.path.join(destination_path, item)
                    if os.path.isfile(source_item):
                        logger.debug(f"Copying file {item}...")
                        try:
                            shutil.copy2(
                                source_item, destination_item
                            )  # 使用 copy2 保留元数据
                            progressValue += 1  # 更新进度条的值
                            if progressValue % progressStep == 0:
                                logger.debug(f"Copied {progressValue} items...")
                                self.progress_queue.put(progressValue)  # 将进度放入队列
                        except (shutil.Error, OSError) as e:
                            logger.debug(
                                f"Error copying file {source_item} to {destination_item}: {e}"
                            )
                        except Exception as e:
                            logger.debug(f"Error processing profile {profile}: {e}")
                    # 如果是目录，则创建目标目录并复制其直接内容
                    elif os.path.isdir(source_item):
                        logger.debug(f"Copying folder {item}...")
                        try:
                            shutil.copytree(
                                source_item, destination_item
                            )  # 复制整个文件夹
                            logger.debug(f"Copying folder {item}...")
                            progressValue += 1  # 更新进度条的值
                            if progressValue % progressStep == 0:
                                logger.debug(f"Copied {progressValue} items...")
                                self.progress_queue.put(progressValue)  # 更新进度
                        except (shutil.Error, OSError) as e:
                            logger.debug(
                                f"Error copying directory {source_item} to {destination_item}: {e}"
                            )
                        except Exception as e:
                            logger.debug(f"Error processing profile {profile}: {e}")
                logger.debug(f"Copied {profile} to {destination_path}")
            except Exception as e:
                logger.debug(f"Error processing profile {profile}: {e}")
        # 备份完成后在主线程中提示
        self.progress_queue.put("done")  # 向队列中添加完成标记

    def start_backup(self):
        # 启动线程来执行备份操作
        self.progress["value"] = 0  # 重置进度条的值
        self.progress["maximum"] = 0  # 重置进度条的最大值
        # 选择目标目录
        destination_dir = filedialog.askdirectory(title="选择备份目录")
        logger.debug(f"Selected destination directory: {destination_dir}")
        if not destination_dir:
            return
        # 禁用按钮
        self.copy_button.config(state="disabled")
        if self.is_chrome_running():
            messagebox.showwarning(
                "Warning",
                "谷歌浏览器正在运行，请关闭浏览器后再进行操作",
            )
            self.copy_button.config(state="normal")  # 异常后重新启用按钮
            return
        chrome_user_data_dir = self.get_chrome_user_data_dir()
        if chrome_user_data_dir is None:
            messagebox.showerror(
                "Error",
                "不支持的平台或无法确定Chrome用户数据目录",
            )
            self.copy_button.config(state="normal")  # 异常后重新启用按钮
            return
        profiles = self.find_chrome_profiles(chrome_user_data_dir)
        if not profiles:
            messagebox.showwarning("Warning", "没有需要备份的用户数据")
            self.copy_button.config(state="normal")  # 异常后重新启用按钮
            return
        # 统计每个 profile 目录下直接子目录和文件的总数
        progressMax = sum(
            len(os.listdir(os.path.join(chrome_user_data_dir, profile)))
            for profile in profiles
        )
        # 打印结果
        logger.debug(f"Total number of files and folders: {progressMax}")
        progressStep = int(progressMax / 25)  # 每次更新进度条的步长
        logger.debug(f"progressStep: {progressStep}")
        logger.debug(f"progressMax: {progressMax}")
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
                    self.progress["value"] = self.progress["maximum"]
                    self.copy_button.config(state="normal")  # 备份完成后重新启用按钮
                    messagebox.showinfo("Completed", "数据备份完成!")
                    return
                else:
                    self.progress["value"] = progress_value  # 更新进度条的值
        except queue.Empty:
            # logger.debug("当前队列为空，等待下次更新...")
            pass
        except Exception as e:
            logger.debug(f"更新进度时发生异常: {e}")  # 记录异常
        finally:
            # 确保无论如何都要定时更新
            self.master.after(100, self.update_progress)  # 每 100 毫秒更新一次进度

    def update_progress_thread(self):
        self.master.after(100, self.update_progress)  # 启动定时器来更新进度


if __name__ == "__main__":
    try:
        # 启动程序的主逻辑
        root = Tk()
        app = ChromeProfileCopier(root)
        root.mainloop()
    except Exception as e:
        logger.debug(f"程序异常: {e}")
        # raise  # 可以注释掉这行来避免显示异常
