# C43 · 眼部 receiver 受控比较：亮度假设没有解决贴片眼

本轮遵循 `scenario-blender-expert`，实际打开批准原图、C20 彩色头图、C38 灰色脸图和本轮 A/B 共四张整身与脸图。没有修改人物几何、眼白、上下睑、cap shader、灯能量、灯位置或网页。

## 可复查输入与输出

- 输入 C38：`artifacts/character-alignment-c38/head-expression-only/miao-c38-coupled-head-gray.blend`，SHA `f481e8a0c00eb4ec5baf5d9c43a6bc250f5a28c4475d9d9cba0ea360ca1c8439`。
- 原色材质来源 C20：`artifacts/character-eye-wet-iris-c20/miao-c20-wet-iris.blend`。按同名物件恢复 87 个物件的材质槽，A/B 完全相同；没有把灰材质图作为彩色对照。
- 执行脚本：`design/character-sculpt-v2/eye-lighting-c43.py`。
- 冻结目录：`artifacts/character-eye-lighting-c43/controlled-ab/`，包括 A/B 原生文件、`*-full.png`、`*-face.png`、`receipt.json`；来源、相机、材质恢复清单、实际灯值和完整网格 hash 在 receipt。
- 毛发在两组中都保持 C38 的隐藏状态，因为它尚未重绑定；此比较不验收全身绒毛。

## 唯一变量

已确认 C20 不透明彩色凸 cap 继承了旧 C7 透明角膜的灯光排除规则：原 Studio key/fill 不照 cap；两盏 optical area 的 diffuse factor 为 0。

A 保持此规则。B 仅把两个 `C7 / clear cornea` cap 加入现有的共享 Studio receiver collection。材质、几何和灯的能量/漫反射/镜面系数/世界变换均一致。两组均为 CPU Cycles、128 samples、seed 17、768 像素、相同 denoise 与相机；所有 mesh/curve 实际坐标、拓扑与世界变换 hash 均不变。

## 实际视觉结论

B 的蓝边和虹膜亮度增加，说明排除规则确实影响了彩色 cap 的受光。但**没有恢复 C20 或批准原图的湿润凸面与自然高光**。脸 crop 中 B 仍像平贴的深色圆片；画面右眼变成较灰、较均匀的一片，不能描述为更可爱或已经有神。全身图中此差别也未消除贴片眼。

因此，本轮保留“原 shader 已由透明角膜换成不透明 cap，receiver 应重新审计”的技术结论，**不把 B 作为眼部艺术通过或生产替换**。原图的圆方脸、耳根、下脸、肩臂和手部 P0 完全未被这项灯光实验解决。

## 下一步的可证伪假设

C38 将所有眼部深度压到 42%，使 cap 的局部曲率和原先被光学灯捕捉的法线范围一起缩小。C43 证明只加漫反射受光不够；它本身未隔离证明曲率就是全部原因。后续 C45 应保持 C38 眼眶/眼白/上下睑与所有灯不变，只从 C20 恢复 cap 相对当前嵌入眼白的局部曲率。先做真实眼/皮肤接触与层级预检，再看相同相机实图。不涂高光、不加发光点、不隐藏眼部。

## 原生重开核验

`controlled-ab/native-readback.json` 来自另进程重开 A/B：47 个 mesh 的实际坐标/拓扑/世界变换 hash 一致；所有有使用者材质的实际节点、输入和连接 hash 一致；全部灯的能量/漫反射/镜面/世界变换一致；唯一 receiver cap 差异为 A 0 个、B 2 个。此为技术受控性核验，不是艺术通过。

## 后续 C47 纠正记录

C47 的实际灯向量与独立 library loader probe 发现：本轮继承的两盏 optical area 世界矩阵都为 identity，位置为 [0,0,0]；源 C20 的灯位置并非原点。旧 assembler 读取未 linked donor.matrix_world 与此异常一致。C47 仅重摆原有两灯后恢复蓝色曲面和真实光点。故本轮失败保留，但其原因不能单归为曲率/receiver；C45 曲率是否必要也尚未被同条件对照证明。详见 `eye-optical-relight-c47-2026-10-29.md`，没有覆盖本轮历史图像与 receipt。
