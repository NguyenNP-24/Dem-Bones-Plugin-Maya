# 🦴 DemBones Maya Plugin

A **Maya plugin** that converts any **mesh or simulation animation** into clean **joint-based animation** using the **DemBones** algorithm — integrated from the open-source project [DemBones by Electronic Arts](https://github.com/electronicarts/dem-bones).

Supports **Maya 2020–2025**  
Build your own `.mll` version for native integration directly in Maya.

Perfect for converting:
- **Alembic caches**  
- **Blendshapes**  
- **Simulation meshes**  

…into **optimized skinned animation** ready for **game engines**.

---

## ⚙️ Parameters

| Name | Description |
|------|--------------|
| **Global Iterations** | Number of optimization passes in the DemBones algorithm. Higher values improve accuracy but increase computation time. *(Recommended: ~50)* |
| **Number of Bones** | Number of bones to generate. More bones capture more motion detail but may reduce runtime performance. *(Typical: 10-50)* |

---

## 🧩 Installation & Uninstallation

| Action | How to Use |
|--------|-------------|
| **Install Plugin** | Open **Autodesk Maya**, then **drag and drop** `install.py` into the viewport. The plugin will automatically be copied to your user folder and loaded. |
| **Uninstall Plugin** | To remove all plugin files and settings, simply **drag and drop** `uninstall.py` into the viewport. |

---

## 📸 Preview

<img width="100%" alt="DemBones Maya Plugin UI" src="https://github.com/user-attachments/assets/d19c474d-c1fa-4526-9e55-81df5b086a5f" />

---
Detail demo process: https://www.youtube.com/watch?v=vK1wJo5-Nlo&t=5s
