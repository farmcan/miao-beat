# 八键装配同姿态原色 · 待独立 shaded gate

2026-10-30。灰门禁三个独立角色均只允许保留八键prop/准备位并进入同pose彩色；完整Miao角色相对原图仍production identity/精致度HOLD，不允许新动画或网页扩展。此文件是builder执行证据，不是第四位judge或最终美术签署。

灰源：`artifacts/miao-eight-key-prop-probe-2026-10-30/gray-gate/eight-key-gray-static-native36.blend`，SHA `42eae3f8eee59f60eeb8d1194f6d979ae55cf0e3140271eb5453be1b32c2fda8`。许可/原作者/八键唯一适配沿[probe报告](miao-eight-key-prop-probe-2026-10-30.md)，没有替换上游素材或修改其许可。

## 唯一呈现变化与六图

只把原生compositor `Render Layers.Image` 直接连回 `Composite.Image`，绕过灰度节点，恢复原本的灰猫、蓝服、红袖/护目镜、青眼、原象牙白/石墨琴和橡木桌。未改材质节点或纹理、角色/键/琴壳几何、两腕准备位、光源、相机角度或渲染质量。

同gray相同六机位、分辨率与原生helper同步：`color-gate/front.png`、`three-quarter.png`、`left-hand.png`、`right-hand.png`、`key-front-edge.png`、`key-rear.png`。完整图是同一完整猫/双掌/乐器/支撑场景；近景只供诊断，不作为生产帧。Builder已实际逐张打开所有六图；本轮没有以近景或灰技术PASS取代独立彩色判断。

待审native：`artifacts/miao-eight-key-prop-probe-2026-10-30/color-gate/eight-key-color-static-native36.blend`，SHA `8bd535e772477f70d6ea85e208329b1aca7fff77fe6088185c442eaf5d442801`。

- pose保留 `40d5a61366db61d6149ad01d26f5ce4310dead1a7951fc5098620b5e1a7ae3fb`。
- 原base mesh坐标/面拓扑/材质槽hash `10809e9e58fd1f8f1b7753c0d4d44de776e07afb56282af2d1e98c4c3a44d67f`，与gray及其源一致。
- 材质节点/连线graph hash `fd3ad65f6a756b392c6e5f5bf84216068a3ee5514c8ee6a682557fa552e8098e` 前后及复开一致。没有把原生表面变成统一灰材质再伪称恢复。
- 相机/helper之外全部scene世界矩阵、光源type/energy/color均与gray一致；render subdivision保持原值，Quality1、simplify=False。六view helper逐轴误差均0。
- 原27actions不增、newmesh0、无新pose；当前没有八键动作、头眼动作或GLB/web修改。
- source gray SHA前后一致。禁上游脚本在官方Blender3.6.23复开color native，确认全部六图hash、pose、mesh/材质graph、原色连接、lights/fixedworld/Quality和动作数量均PASS。

脚本：`design/miao-reuse-keyboard-v1/render_eight_key_color_gate.py`，`-- --verify`只读复开；证据在 `color-gate/inspection-manifest.json` 与 `native-reopen-verification.json`。只运行本机新写bpy，未运行embedded Python，未修改用户偏好或源下载。

## 未签署的范围

较大的白键和2+3黑键分组有利于读键，但本组彩色still没有证明真实按压/八键触达/1.5mm行程可见性、连续实体碰撞或浏览器性能。原黑白键安装交叠与near-boundary unknown保留，数值probe的matched-proxy限制不变。

飞行员服装、过大的正视青眼、小穿衣躯干、张口表情、短绒/梨形轮廓差距完全未处理。无论三角色是否允许保留本八键prop，均不能宣称完整角色通过，也不能让prop的窄GO解除生产身份HOLD。root实际看图后应交identity/craft/motion三个非builder做同pose彩色装配门禁，再决定保留或冻结；本轮到此停止，不新增参数候选、动作或发布。

## 彩色三评之后的独立乐器作者资产

三角色彩色评审只允许保留八键prop/准备位，整角色继续HOLD。随后从本页固定8bd…源导出**仅18乐器mesh**，没有猫/桌/rig/隐藏键/文本脚本/灯/相机/动画。资产不是完整角色生产帧；CC0原乐器数据可复用，用户要求的角色+双掌+乐器同帧约束没有因此改变。

`artifacts/miao-eight-key-prop-probe-2026-10-30/prop-export/eight-key-cc0-prop.glb`，214,480字节，SHA `d4f3ea60171f8275f02b59d9c3c8754234287f058b09cfd2fb047c6eaf6ceae6`。只读重导核对18mesh名映射、18矩阵、真实世界bounds/top、55.675mm键距、5,560三角形、3材质、4内嵌图；最大矩阵误差4.17e−9、bounds4.66e−9m、双向最近点1.50e−8m，top与pitch误差0。之后才拍一张全prop3Q诊断，builder已实际查看，无明显导出丢边/丢键或材质退化；root仍需实际看。

另用dependency-only `libraries.write`生成最小数据资产库 `eight-key-cc0-prop-native36.blend`（176,270字节，SHA `a37df130055401bcadfb2e7096763bfd5685143235873aeb1c92e77fd44bf150`）。独立禁脚本复开确认1Scene/18objects/18meshes/3materials/4packed images，rig/action/camera/light/text全0，不把混合源Scene中的CC BY猫或旧藏键混入CC0 prop包。该native是用于Append/Link的data-only资产库，不提供UI或camera；不是另一套已过角色终验的成品场景。

同目录 `note-map.json`记录原fit Z180朝向：猫/玩家升音C4→C5为source白014→021，观众front world-X升序实际上C5→C4，不能按worldX升序直接赋升音。五黑键音高由实际相邻白键间隙推导，非单凭物体序号猜测；仅语义映射，没有新增动画或指法教学。导出脚本 `export_eight_key_prop.py`、README、`reimport-verification.json`、`minimal-native-verification.json`保留源SHA/许可/确切改动和误差。原8bd…源字节不变，未改public或发布。
