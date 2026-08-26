# =====================================================================
#  DemBones Maya Plugin - Multi-Version Build
#  Author: Bin & ChatGPT
# =====================================================================

cmake_minimum_required(VERSION 3.15)
project(DemBones_Maya_Plugin)

# ------------------------------------------------------------
# Configurable build parameters
# ------------------------------------------------------------
if(NOT DEFINED MAYA_VERSION)
    message(FATAL_ERROR "❌ Please specify Maya version via -DMAYA_VERSION=XXXX")
endif()

if(NOT DEFINED MAYA_DEVKIT_ROOT)
    message(FATAL_ERROR "❌ Please specify Maya Devkit root via -DMAYA_DEVKIT_ROOT=PATH_TO_DEVKIT")
endif()

message(STATUS "▶ Building for Maya ${MAYA_VERSION}")
message(STATUS "▶ Using Devkit: ${MAYA_DEVKIT_ROOT}")

# ------------------------------------------------------------
# Directories
# ------------------------------------------------------------
set(MAYA_INCLUDE_DIR "${MAYA_DEVKIT_ROOT}/include")
set(MAYA_LIB_DIR     "${MAYA_DEVKIT_ROOT}/lib")

# Thêm thư mục thirdparty
set(THIRDPARTY_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/include")

include_directories(
    ${MAYA_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${THIRDPARTY_DIR}
)

link_directories(${MAYA_LIB_DIR})

# ------------------------------------------------------------
# Source files - Include ALL subdirectories
# ------------------------------------------------------------
file(GLOB_RECURSE SRC_FILES
    "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.h"
)

# Loại trừ các file không cần thiết
list(FILTER SRC_FILES EXCLUDE REGEX ".*/build/.*")
list(FILTER SRC_FILES EXCLUDE REGEX ".*/CMakeFiles/.*")

message(STATUS "▶ Found source files:")
foreach(SRC_FILE ${SRC_FILES})
    message(STATUS "   - ${SRC_FILE}")
endforeach()

# ------------------------------------------------------------
# Build the plugin (.mll)
# ------------------------------------------------------------
add_library(DemBones_maya${MAYA_VERSION} SHARED ${SRC_FILES})

target_link_libraries(DemBones_maya${MAYA_VERSION}
    OpenMaya.lib
    Foundation.lib
    OpenMayaAnim.lib
)

# ------------------------------------------------------------
# Compiler flags
# ------------------------------------------------------------
target_compile_definitions(DemBones_maya${MAYA_VERSION}
    PRIVATE
    _BOOL
    NT_PLUGIN
    REQUIRE_IOSTREAM
    EXPORTING
    MAYA_VERSION=${MAYA_VERSION}
)

# C++ Standard
set_target_properties(DemBones_maya${MAYA_VERSION} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
)

# ------------------------------------------------------------
# Output naming and folder
# ------------------------------------------------------------
set_target_properties(DemBones_maya${MAYA_VERSION} PROPERTIES
    OUTPUT_NAME "DemBones_maya${MAYA_VERSION}"
    SUFFIX ".mll"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/src/Release"
)

# ------------------------------------------------------------
# Post-build message
# ------------------------------------------------------------
message(STATUS "✅ DemBones_maya${MAYA_VERSION}.mll will be built in:")
message(STATUS "   ${CMAKE_BINARY_DIR}/src/Release")