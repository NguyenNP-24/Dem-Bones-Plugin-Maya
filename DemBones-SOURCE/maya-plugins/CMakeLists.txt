cmake_minimum_required(VERSION 3.15)
project(DemBones)

# Maya version configuration
if(NOT DEFINED MAYA_VERSION)
    set(MAYA_VERSION "2025" CACHE STRING "Maya version to build for")
endif()

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake" ${CMAKE_MODULE_PATH})
set(CMAKE_INSTALL_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/install)

# Set Maya DevKit path based on version
if(NOT DEFINED MAYA_DEVKIT_ROOT)
    set(MAYA_DEVKIT_ROOT "C:/Program Files/Autodesk/Maya${MAYA_VERSION}/devkit" CACHE PATH "Maya DevKit root directory")
endif()

include_directories(${PROJECT_SOURCE_DIR}/thirdparty/include)

add_subdirectory(src)
