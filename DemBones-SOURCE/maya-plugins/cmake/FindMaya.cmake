# FindMaya.cmake - Find Autodesk Maya SDK

set(MAYA_VERSION ${MAYA_VERSION} CACHE STRING "Maya version")

if(WIN32)
    set(MAYA_INSTALL_BASE_DEFAULT "C:/Program Files/Autodesk")
    set(MAYA_COMPILE_DEFINITIONS "NT_PLUGIN;REQUIRE_IOSTREAM;_BOOL")
    set(MAYA_PLUGIN_EXTENSION ".mll")
    set(MAYA_TARGET_TYPE RUNTIME)
endif()

set(MAYA_INSTALL_BASE_PATH ${MAYA_INSTALL_BASE_DEFAULT} CACHE STRING "Maya installation base path")

find_path(MAYA_BASE_DIR
    include/maya/MFn.h
    HINTS
        "${MAYA_ROOT}"
        "${MAYA_INSTALL_BASE_PATH}/Maya${MAYA_VERSION}"
        "$ENV{MAYA_LOCATION}"
    DOC "Maya installation root directory"
)

find_path(MAYA_INCLUDE_DIR
    maya/MFn.h
    HINTS
        "${MAYA_BASE_DIR}"
    PATH_SUFFIXES
        include
    DOC "Maya include directory"
)

find_path(MAYA_LIBRARY_DIR
    OpenMaya.lib
    HINTS
        "${MAYA_BASE_DIR}"
    PATH_SUFFIXES
        lib
    DOC "Maya library directory"
)

set(MAYA_LIBS
    OpenMaya
    OpenMayaAnim
    OpenMayaFX
    OpenMayaRender
    OpenMayaUI
    Foundation
)

foreach(MAYA_LIB ${MAYA_LIBS})
    find_library(MAYA_${MAYA_LIB}_LIBRARY
        NAMES ${MAYA_LIB}
        HINTS ${MAYA_LIBRARY_DIR}
        DOC "Maya ${MAYA_LIB} library"
    )
    list(APPEND MAYA_LIBRARIES ${MAYA_${MAYA_LIB}_LIBRARY})
endforeach()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Maya
    REQUIRED_VARS MAYA_BASE_DIR MAYA_INCLUDE_DIR MAYA_LIBRARY_DIR
    VERSION_VAR MAYA_VERSION
)

if(Maya_FOUND)
    set(MAYA_FOUND TRUE)
endif()

# Macro to create Maya plugin
macro(MAYA_PLUGIN target)
    set_target_properties(${target} PROPERTIES
        PREFIX ""
        SUFFIX ${MAYA_PLUGIN_EXTENSION}
    )
    
    target_compile_definitions(${target} PRIVATE ${MAYA_COMPILE_DEFINITIONS})
    
    target_include_directories(${target} PRIVATE ${MAYA_INCLUDE_DIR})
    target_link_libraries(${target} ${MAYA_LIBRARIES})
    
    if(WIN32)
        set_target_properties(${target} PROPERTIES
            LINK_FLAGS "/export:initializePlugin /export:uninitializePlugin"
        )
    endif()
endmacro()