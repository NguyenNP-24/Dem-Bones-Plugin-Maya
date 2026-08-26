@echo off
setlocal enabledelayedexpansion

echo ============================================
echo DemBones Maya Plugin Multi-Version Builder
echo ============================================

REM Cấu hình đường dẫn
set PROJECT_ROOT=%~dp0
set OUTPUT_DIR=%PROJECT_ROOT%output_mll

REM Tạo thư mục output
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Danh sách các phiên bản Maya cần build
set MAYA_VERSIONS=2020 2022 2023 2024 2025

REM Build từng phiên bản
for %%V in (%MAYA_VERSIONS%) do (
    call :build_version %%V
)

echo.
echo ============================================
echo Build Summary
echo ============================================
dir /b "%OUTPUT_DIR%\*.mll"
echo ============================================
pause
goto :eof

:build_version
set VERSION=%1
echo.
echo ========================================
echo Building for Maya %VERSION%
echo ========================================

REM Tạo thư mục build riêng cho từng phiên bản
set BUILD_DIR=%PROJECT_ROOT%build_%VERSION%
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"
cd /d "%BUILD_DIR%"

REM Cấu hình CMake
cmake -G "Visual Studio 17 2022" -A x64 ^
    -DMAYA_VERSION=%VERSION% ^
    -DMAYA_DEVKIT_ROOT="C:/Program Files/Autodesk/Maya%VERSION%/devkit" ^
    ..

if errorlevel 1 (
    echo [ERROR] CMake failed for Maya %VERSION%
    goto :eof
)

REM Build
cmake --build . --config Release

if errorlevel 1 (
    echo [ERROR] Build failed for Maya %VERSION%
    goto :eof
)

REM Copy file .mll với tên phiên bản
if exist "src\Release\DemBones.mll" (
    copy "src\Release\DemBones.mll" "%OUTPUT_DIR%\DemBones_%VERSION%.mll"
    echo [SUCCESS] Created DemBones_%VERSION%.mll
) else (
    echo [WARNING] DemBones.mll not found for Maya %VERSION%
)

cd /d "%PROJECT_ROOT%"
goto :eof
