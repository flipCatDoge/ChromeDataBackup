param(
    [string]$envName = ".venv",
    [string]$requirementsFile = "pipAutoShell\requirements.txt"
)

# 检查虚拟环境文件夹是否存在
if (Test-Path $envName) {
    Write-Host "Virtual environment '$envName' already exists. No need to create a new one."
    # 在虚拟环境中使用以下命令刷新 VSCode
    # deactivate  # 先退出虚拟环境
    code .      # 重新打开 VSCode 并自动识别虚拟环境
} else {
    # 创建虚拟环境
    Write-Host "Creating virtual environment: $envName"
    python -m venv $envName
    Write-Host "Virtual environment '$envName' created."
    # 激活虚拟环境
    Write-Host "Activating virtual environment"
    $venvActivate = ".\$envName\Scripts\Activate.ps1"
    & $venvActivate
}

# 获取当前 pip 版本
$currentPipVersion = pip --version | Select-String -Pattern '\d+\.\d+\.\d+' | ForEach-Object { $_.Matches.Value }

# 获取最新的 pip 版本
$latestPipVersion = (Invoke-RestMethod -Uri 'https://pypi.org/pypi/pip/json').info.version

# 比较当前版本和最新版本
if ($currentPipVersion -eq $latestPipVersion) {
    Write-Host "pip is up-to-date (version: $currentPipVersion). No upgrade needed."
} else {
    Write-Host "Current pip version: $currentPipVersion. Upgrading to the latest version: $latestPipVersion."
    python.exe -m pip install --upgrade pip
}

# 检查是否存在 requirements.txt 文件，并安装依赖
if (Test-Path $requirementsFile) {
    Write-Host "Installing dependencies from $requirementsFile"
    pip install -r $requirementsFile
} else {
    Write-Host "No $requirementsFile found, skipping dependency installation."
}

Write-Host "Virtual environment '$envName' created and dependencies installed."
Write-Host "Please restart VsCode or PyCharm IDE" -ForegroundColor Green
# 保持虚拟环境激活状态
$SHELL

# 在虚拟环境中使用以下命令刷新 VSCode
# deactivate  # 先退出虚拟环境
code .      # 重新打开 VSCode 并自动识别虚拟环境