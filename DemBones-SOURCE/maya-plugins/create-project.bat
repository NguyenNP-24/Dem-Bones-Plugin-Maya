
set CURRENT_DIR=%cd%
echo %CURRENT_DIR%

echo "Creating project for Maya 2020"
rmdir /S /Q project_2020
mkdir project_2020
cd project_2020
cmake -G "Visual Studio 15 2017 Win64" -DMAYA_VERSION=2020 ..

pause