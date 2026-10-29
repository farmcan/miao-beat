# C45 · 只恢复 cap 曲率，保持 C38 的眼眶与眼白嵌入

这是继 C43 receiver 比较后的独立几何实验，不覆盖 C43。原图仍为 `public/character/instrument-scenes-v1/guitar/idle.jpg`。全身身份、耳根、肩臂和手部未在本实验中更改，未发布。

## 输入与唯一几何变量

输入 `artifacts/character-eye-lighting-c43/controlled-ab/A-original-routing.blend`，保留 C38 的头、眉、眼白、上下睑、iris、鼻嘴、身体、琴和 C20 彩色材质；全部灯光、receiver、能量、镜面和漫反射系数均保持 A。

仅将两个 `C7 / clear cornea` 不透明彩色 cap 的原 C20 局部曲率恢复到当前 C38 已内嵌眼白前方。先逆共同 7.5 度 yaw，分别拟合源与目标 cap 后沿的局部平面，再把源 cap 相对其后沿的真实曲率移到目标平面，最后施回同一 yaw。不是替换整颗眼球，也没有把下睑、眼白一并推回外贴球。

从源 cap 到候选是正行列式为 1 的连续仿射 shear/translation；实际拓扑仍需单独检查，不能仅凭公式宣称无交。

## 冻结的首次失败

`artifacts/character-eye-cap-c45/preflight.json` 与 `executed-script.py` 保留首次候选。cap 自身闭合、正体积、自交 0，头皮无交，但后沿处穿当前 iris / sclera，最大约 .00104u。没有进入该失败版本的渲染，也没有改门槛掩盖它。

## r2 必要层级修正与实际预检

`artifacts/character-eye-cap-c45/r2-layer-clearance/`。仅将整片 cap 沿原眼视轴向前移动由实际最小层级净距算出的距离，保持曲率/法线/shader/灯不变：L .00107997u，R .00090412u。上限 .002u，目标 iris 净距 .00004u。

实际结果：

- 除两片 cap 外，所有 scene mesh 的世界坐标 hash 与输入 exact。
- 每片 4610 顶点；closed、nonmanifold 0、self-intersection 0、正体积。
- cap 与各自 iris、sclera 及整块头身的完整三角相交均为 0。
- 对每层的 4610 个实际顶点射线均命中，无 miss；iris 最小净距 L .0000397665u / R .0000395277u，sclera 至少 .000383888u，头皮至少 .00380752u。
- 只移动 cap，最大位移 L .01165286u / R .01133540u。没有 custom normals、发光点、贴图高光、眼件隐藏或灯光修正。

数值通过只代表本次静态 cap 层级检查；不证明眨眼、所有角度、动态或网页表现。

## 实图与判断

已实际打开 r2 的 `c45-full.png` 与 `c45-face.png`，并与 C43 A/B、原 C20 头图及批准原图比较。

相比 C43 A，cap 下缘出现少量曲面反光/转面，局部体积不再完全一样；但两眼仍读成很深的黑色圆片，**未恢复原 C20 或批准图的蓝色层次、自然光点和温润眼神**。全身观看也没有足以宣布“眼睛有神”的提升。白眼的平贴、缺少软睑包裹仍在。

**艺术结论：不通过，不生产替换。** 这一实验只保留已无穿插的局部曲率候选和明确的否证：单独恢复 cap 原曲率，在继承的光学灯/新头转向组合下仍不足以完成眼神。不能以 geometry gate true 覆盖此结论。

若继续，应先审计真实 cap 法线、共同头转向、相机和实际反射灯方向之间的关系，恢复参考所需的真实镜面读法；仍不应涂高光或用发光点。不要把本轮未通过的结果直接叠加到整体资产后称完成。静态原图配准、整体身份和独立三角色门禁继续未通过。

## 保存后重开核验

`r2-layer-clearance/native-readback.json` 来自另进程重开，native SHA `2ca04f2f8a8e82471fa2a14d81b0efa007be1096505b632c068db26c1ef4a9b3`。只有两个 cap 的实际几何 hash 改变；其他 mesh 与 curve 的几何和世界变换、所有材质槽以及灯值/receiver 均 exact。重新建立的实际 BVH 再次确认与 iris / sclera / 整块头身的六项三角相交全 0。艺术结论仍为不通过。

## 后续 C47 纠正记录

C47 的实际灯向量与独立 library loader probe 发现：本轮继承的两盏 optical area 世界矩阵都为 identity，位置为 [0,0,0]；源 C20 的灯位置并非原点。旧 assembler 读取未 linked donor.matrix_world 与此异常一致。C47 仅重摆原有两灯后恢复蓝色曲面和真实光点。故本轮失败保留，但其原因不能单归为曲率/receiver；C45 曲率是否必要也尚未被同条件对照证明。详见 `eye-optical-relight-c47-2026-10-29.md`，没有覆盖本轮历史图像与 receipt。
