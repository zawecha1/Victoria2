@echo off
chcp 65001 >nul
echo ========================================
echo Victoria II 存档文件解析器
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo 错误: 未找到Python安装
        echo.
        echo 请先安装Python:
        echo 1. 访问 https://www.python.org/downloads/
        echo 2. 下载并安装Python 3.8+
        echo 3. 安装时确保勾选 "Add Python to PATH"
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo Python已安装，版本:
%PYTHON_CMD% --version
echo.

REM 检查存档文件是否存在
if not exist "China2245_04_06.v2" (
    echo 错误: 找不到存档文件 "China2245_04_06.v2"
    echo 请确保存档文件在当前目录下
    echo.
    pause
    exit /b 1
)

echo 存档文件已找到: China2245_04_06.v2
echo.

echo 选择解析模式:
echo 1. 快速分析（推荐）- 提取基本信息和统计数据
echo 2. 完整解析 - 解析所有详细数据（较慢）
echo 3. 退出
echo.
set /p choice="请输入选择 (1-3): "

if "%choice%"=="1" (
    echo.
    echo 正在运行快速分析...
    echo.
    %PYTHON_CMD% simple_parser.py
    if %errorlevel% equ 0 (
        echo.
        echo 分析完成！结果已保存到 victoria2_analysis.json
    ) else (
        echo.
        echo 分析过程中出现错误
    )
) else if "%choice%"=="2" (
    echo.
    echo 正在运行完整解析...
    echo 注意: 这可能需要几分钟时间
    echo.
    %PYTHON_CMD% victoria2_parser.py
    if %errorlevel% equ 0 (
        echo.
        echo 解析完成！详细结果已保存
    ) else (
        echo.
        echo 解析过程中出现错误
    )
) else if "%choice%"=="3" (
    echo 退出程序
    exit /b 0
) else (
    echo 无效选择，退出程序
    exit /b 1
)

echo.
echo 按任意键查看生成的文件...
pause >nul

REM 显示生成的文件
echo.
echo 生成的文件:
dir /b *.json 2>nul
if %errorlevel% neq 0 (
    echo 未找到生成的JSON文件
) else (
    echo.
    echo 可以使用文本编辑器打开这些JSON文件查看详细数据
)

echo.
pause
