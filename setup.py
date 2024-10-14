from cx_Freeze import setup, Executable

# 指定需要包括的包、模块、额外文件等
options = {
    "build_exe": {
        "packages": [],
        "excludes": [],
        "include_files": ["chrome.ico"],  # 包括额外的文件
    }
}

executables = [
    Executable(
        "main.py",
        base="Win32GUI",
        icon="chrome.ico",
        target_name="ChromeDataBackup_V1.0"  # 生成的可执行文件名称
    )  # 如果你要打包 GUI 程序
]

# 设置其他打包选项
setup(
    name="ChromeDataBackup",
    version="1.0",
    options=options,
    description="谷歌浏览器数据备份工具",
    executables=executables,
)
