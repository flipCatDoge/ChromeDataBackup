param(
    [string]$fileName = "requirements.txt"  # 默认输出文件名
)
# 打印当前运行的 PS1 文件目录
Write-Host "Current script directory: $PSScriptRoot"
$file = "$PSScriptRoot/$fileName"
# 判断是否在虚拟环境中
function Get-VirtualEnv {
    # 检查环境变量是否存在，并且路径有效
    if ($env:VIRTUAL_ENV -and (Test-Path $env:VIRTUAL_ENV)) {
        return $true
    }
    
    # 检查当前目录中是否存在名为 .venv 或 venv 的虚拟环境文件夹
    return (Test-Path ".venv") -or (Test-Path "venv")
}

# 检查是否在虚拟环境中
if (Get-VirtualEnv) {
    # 在虚拟环境中，执行 pip freeze 并输出到指定文件
    pip freeze > $file
    Write-Host "Packages have been exported to $file."
}
else {
    # 不在虚拟环境中，返回提示信息
    Write-Host "Not in a virtual environment. Please activate your virtual environment first." -ForegroundColor Red
}