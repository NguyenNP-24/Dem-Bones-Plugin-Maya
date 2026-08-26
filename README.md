# 🦴 DemBones Maya Plugin

A **Maya plugin** that converts any **mesh or simulation animation** into clean **joint-based animation** using the **DemBones** algorithm — integrated from the open-source project [DemBones by Electronic Arts](https://github.com/electronicarts/dem-bones).

Supports **Maya 2020–2025**

Perfect for converting:
- **Alembic caches**
- **Cloth / fluid simulations**
- **Blendshapes**

…into **optimized skinned animation** ready for **game engines**.

## 🧩 Installation & Uninstallation

| Action | How to Use |
|--------|------------|
| **Install** | Open **Autodesk Maya**, then **drag and drop** `install.py` into the viewport. The plugin, scripts, and icon are copied to your Maya user folder automatically. |
| **Uninstall** | **Drag and drop** `uninstall.py` into the viewport to remove all plugin files and shelf entries. |

---

## 🔀 Modes

### Single Mode
One simulation mesh → one new skeleton + skin cluster.

Select your sim mesh, set the frame range, and hit **Generate Bones**. The bind pose is automatically duplicated from the start frame — no manual setup needed.

### Shared Skeleton Mode
Multiple simulation meshes (same topology) → one shared skeleton.

Each simulation becomes a **separate animation clip** laid out consecutively on the same rig, ready to export as individual clips to a game engine. All meshes must share the same vertex count as the bind pose target.

<img width="1087" height="679" alt="MultipleSimToOneRig" src="https://github.com/user-attachments/assets/98218702-eddc-499f-9d54-7130a351de15" />


---

## ⚙️ Parameters

| Parameter | Description |
|-----------|-------------|
| **Quality** | Controls optimization accuracy (Global Iterations). Draft: `<10` · Good: `50` · Best: `100+` |
| **Num Bones** | Number of bones to generate. More bones = finer deformation but heavier rig. Typical range: `8`–`64` |
| **Custom Root Parent** | Parent the generated skeleton under any existing scene object (joint, group, locator, etc.) instead of world origin |

Higher bone count captures more detail at the cost of runtime performance:

<img width="1087" height="409" alt="NumberBonesComparision" src="https://github.com/user-attachments/assets/b6f90ad9-84c6-46b6-8367-d6fc3eb66ea8" />


---

## 📸 UI Preview

<img width="530" height="488" alt="image" src="https://github.com/user-attachments/assets/1357872e-4b86-496e-b41a-13511c9fff8c" />
<img width="528" height="603" alt="image" src="https://github.com/user-attachments/assets/73edda63-c1c3-4ace-a643-51742f2c578a" />



---

Demo: https://www.youtube.com/watch?v=vK1wJo5-Nlo&t=5s
