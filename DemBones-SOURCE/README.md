# DemBones Source — Build from Scratch

This folder contains the C++ source code used to build `DemBones.mll` (Maya plugin) and the `DemBones` core library. It is provided for anyone who needs to recompile the plugin for a different Maya version or extend the C++ side.

```
DemBones-SOURCE/
  dem-bones/          Core algorithm library (header-only C++, BSD-3 license, from EA/Binh Huy Le)
  maya-plugins/       Maya plugin source — compiles to DemBones_maya<VERSION>.mll
    thirdparty/
      include/
        DemBones/     DemBones headers (already bundled — no download needed)
        Eigen/        Eigen 3.3.7 (already bundled — no download needed)
```

---

## Build the Maya Plugin (`DemBones.mll`)

### Requirements

| Tool | Version | Download |
|---|---|---|
| CMake | 3.15+ | https://cmake.org/download/ |
| Visual Studio | 2019 or 2022 (Windows) | https://visualstudio.microsoft.com/ |
| Maya DevKit | Match your Maya version | https://www.autodesk.com/developer-network/platform-technologies/maya |

> **Eigen and DemBones headers are already bundled** in `maya-plugins/thirdparty/include/`.  
> You do **not** need to download them separately for the Maya plugin build.

### Steps

```bat
cd maya-plugins
mkdir build
cd build

cmake .. -DMAYA_VERSION=2025 -DMAYA_DEVKIT_ROOT="C:/Program Files/Autodesk/Maya2025/devkit"

cmake --build . --config Release
```

Replace `2025` and the DevKit path with your actual Maya version. The output `.mll` will be at:
```
maya-plugins/build/src/Release/DemBones_maya2025.mll
```

### Where to find the Maya DevKit

1. Go to https://www.autodesk.com/developer-network/platform-technologies/maya
2. Log in with your Autodesk account
3. Download the DevKit that matches your Maya version exactly
4. Extract it — the `devkit/` folder inside is your `MAYA_DEVKIT_ROOT`

---

## Build the dem-bones CLI Tool (optional)

The `dem-bones/` folder is the original standalone command-line tool by EA. It reads/writes FBX and Alembic files directly. You only need this if you want to use DemBones outside of Maya (e.g. from Blender via subprocess, or for batch processing).

### Additional dependencies (NOT bundled — download manually)

| Library | Version | Path expected by CMake | Download |
|---|---|---|---|
| Eigen | 3.3.9 | `dem-bones/ExtLibs/Eigen/Eigen/Dense` | https://eigen.tuxfamily.org/ |
| Alembic | from Maya DevKit | `dem-bones/ExtLibs/Alembic/include/Alembic/Abc/All.h` | Inside Maya DevKit |
| FBX SDK | 2020.0.1 | `dem-bones/ExtLibs/FBXSDK/include/fbxsdk.h` | https://www.autodesk.com/developer-network/platform-technologies/fbx-sdk-2020-0 |
| tclap | 1.2.4 | `dem-bones/ExtLibs/tclap/include/tclap/CmdLine.h` | http://tclap.sourceforge.net/ |

After placing those libraries, build:

```bat
cd dem-bones
mkdir build
cd build
cmake ..
cmake --build . --config Release --target install
```

On Linux you may also need:
```bash
sudo apt-get install libxml2-dev zlib1g-dev
```

On macOS, Apple Clang does not support OpenMP. Use LLVM:
```bash
brew install llvm libomp
cmake -DCMAKE_C_COMPILER=/usr/local/opt/llvm/bin/clang \
      -DCMAKE_CXX_COMPILER=/usr/local/opt/llvm/bin/clang++ ..
```

---

## Blender integration (future / pybind11)

The `pybind11` folder is **not included** in this repo (too large). If you want to build Python bindings to call DemBones from Blender:

1. Download pybind11: https://github.com/pybind/pybind11
2. Place it at `DemBones-SOURCE/pybind11/`
3. The DemBones core (`dem-bones/include/DemBones/`) is header-only, so you only need to expose it via a pybind11 wrapper — no extra linking required beyond Eigen.

---

## License

- `dem-bones/` — BSD-3-Clause © Electronic Arts / Binh Huy Le
- `maya-plugins/` — see `maya-plugins/LICENSE.md`
- Eigen — Mozilla Public License 2.0
- pybind11 (not included) — BSD-style
