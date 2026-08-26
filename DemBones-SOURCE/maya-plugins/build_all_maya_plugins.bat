@echo off
setlocal enabledelayedexpansion

echo ============================================
echo DemBones Maya Plugin Builder
echo Building for Maya 2020, 2022-2025
echo ============================================

REM Configuration
set EIGEN_DIR=D:/DemBones-Maya/eigen-3.4.0
set DEMBONES_DIR=D:/DemBones-Maya/dem-bones/include
set DEVKIT_ROOT=D:/MayaDevKits
set PROJECT_ROOT=D:/DemBones-Maya/plugins
set OUTPUT_DIR=D:/DemBones-Maya/outputMll

REM Create output directory
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Build Maya 2020
call :build_version 2020

REM Build Maya 2022
call :build_version 2022

REM Build Maya 2023
call :build_version 2023

REM Build Maya 2024
call :build_version 2024

REM Build Maya 2025
call :build_version 2025

echo.
echo ============================================
echo Build Summary
echo ============================================
echo Output directory: %OUTPUT_DIR%
echo.
if exist "%OUTPUT_DIR%\*.mll" (
    dir /b "%OUTPUT_DIR%\*.mll"
) else (
    echo No .mll files found!
)
echo.
echo ============================================
echo Build completed!
echo ============================================
pause
goto :eof

REM Function to build for specific version
:build_version
set VERSION=%1
echo.
echo ========================================
echo Building for Maya %VERSION%
echo ========================================

REM Check if DevKit exists
if not exist "%DEVKIT_ROOT%\Maya%VERSION%" (
    echo [ERROR] Maya %VERSION% DevKit not found at: %DEVKIT_ROOT%\Maya%VERSION%
    echo [SKIP] Skipping Maya %VERSION%
    goto :eof
)

REM Clean and create build directory
cd "%PROJECT_ROOT%"
if exist "build_%VERSION%" rmdir /s /q "build_%VERSION%"
mkdir "build_%VERSION%"
cd "build_%VERSION%"

REM Configure with CMake
echo [CMAKE] Configuring...
cmake -G "Visual Studio 17 2022" -A x64 ^
    -DMAYA_VERSION=%VERSION% ^
    -DMAYA_DEVKIT_ROOT="%DEVKIT_ROOT%/Maya%VERSION%" ^
    -DDEMBONES_INCLUDE_DIR="%DEMBONES_DIR%" ^
    -DEIGEN_INCLUDE_DIR="%EIGEN_DIR%" ^
    ..

if errorlevel 1 (
    echo [ERROR] CMake configuration failed for Maya %VERSION%
    goto :eof
)

REM Build
echo [BUILD] Compiling...
cmake --build . --config Release

if errorlevel 1 (
    echo [ERROR] Build failed for Maya %VERSION%
    goto :eof
)

REM Copy output
if exist "src\Release\DemBones.mll" (
    copy "src\Release\DemBones.mll" "%OUTPUT_DIR%\DemBones_%VERSION%.mll"
    echo [SUCCESS] DemBones_%VERSION%.mll created!
) else (
    echo [ERROR] DemBones.mll not found for Maya %VERSION%
)

goto :eof