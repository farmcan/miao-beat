# C35：三个quad的明确三角化，真实静态工程门槛通过

2026-10-29。仅接C33冻结native `bae5552b97cf890c0ceab4a2368cf7665cc3defe60a3ec26234f38c7f9a361f4`，原失败与内部诊断不变。没有继续QP、改U界、移动全掌／目标，也未新增顶点。

## 有限拓扑修复

修区只包括原polygon590434／590446／590443。每quad两种原循环绕序的对角线，解析全部2³=8组合，按“最少原对角线改变，再字典序”排序；只将一个组合写入完整mesh、只渲一个结果。

| 组合（依590434/590446/590443） | actual skin非邻三角对 | actual第三弦交对 | 全门槛资格 |
| --- | ---: | ---: | --- |
| 0,0,1（原隐式diag） | 3 | 8 | 否 |
| 0,0,0 | 3 | 0 | 否 |
| 0,1,1 | 3 | 8 | 否 |
| 1,0,1 | 0 | 8 | 否 |
| 0,1,0 | 3 | 0 | 否 |
| **1,0,0** | **0** | **0** | **选定，最少2条diag改变** |
| 1,1,1 | 0 | 8 | 否 |
| 1,1,0 | 0 | 0 | 合格但改变3条diag，不选 |

模式0=(0,1,2)+(0,2,3)；模式1=(1,2,3)+(1,3,0)。三个quad均真正替换为显式三角面，590434和590443改对角线，590446显式固定原对角线。不是在原几何上仅改审计措辞；实际渲染的三角面已改变。

初始解析中builder曾额外用“新三角normal必须与原非平面quad平均normal同向”作代理合法性门槛，连原隐式diag也被全部挡下。这不是合法三角化的可靠定义；保留未应用几何的输入检查于`initial-mean-normal-proxy-guard/`，纠正为原循环绕序／非零面积及实际self/flip/琴弦验证。没有渲多个候选或引入美术参数扫。有限combo已找到真解，无需双线性细分。

## 最终完整mesh与实际碰撞

- 全部590793原顶点：顺序、float32坐标逐位相同，最大位移 **0**。面数590465→590468，恰为3quad→6tri；单连通闭合，边界0、非流形0。
- 三个原面的source ID、所有原int face属性、material和smooth属性逐项保留；新增`C35 original polygon id`仅用于明确来源。未修改角色外形、接触目标、身体或另一只爪。
- actual hand+邻接原collar审计：**self0、flipped0**。与actual evaluated指板、neck、六根弦tube逐一三角面交对均 **0**。
- 5359手部点分别对真实指板／neck做双方向parity：内部0、分歧0。无木体穿入、自交或弦管穿入容差豁免。
- 保存后重开readback：全点坐标hash相同，`C23 source vertex id`、source opening local id、actual upper local id、C11 source vertex id逐整数值相同；头部精确source-ID merge路径保留，不需nearest。

## 五个真实目标与数值边界

所有原世界目标保持、actual ray仍命中声明upper／wrist源区，正确朝向normal。实际gaps：

1. 趾1 +.0005280850455u
2. 趾2 +.0020000813529u
3. 趾3 +.0002730963752u
4. 内掌托1 +.0019998277421u
5. 内掌托2 +.0020001604571u

**严格nominal≤.002仍为false**，不能写成精确通过。父任务明确授权：对这类固定顶点正间隙，使用nominal[0,.002]+**2.5e-7u fp32容差**；最高超差1.60457e-7u，在768/ortho1.25 inside约.0000986px。此授权只覆盖正间隙数值上界，不覆盖任何真实自交／穿弦／穿木；它们最终均actual0。`receipt.json`分别保存strict nominal与authorized roundoff两个布尔值。

## 两张灰图与审美边界

native `miao-c35-fixed-vertex-tessellation.blend` SHA **3097d74a3f932d6dd61e60b7ab12bd40c5c53cd09b7c94aaf93170a03ec25cce**。几何真实门槛通过后才从该完整场景出`gray-front.png`、`gray-inside.png`。front为完整猫／双爪／吉他单帧；inside是作者诊断crop，不是生产动画。

Builder已实际打开原idle、C33内部两图及本C35两图：短圆三趾、连续掌背保持，无可见新增横唇或拉长；微小修区在正常尺寸不突出。此为builder观察，**不代替身份／craft／motion三角色独立灰模评审**。当前只称静态工程门槛通过，不称整角色艺术完成、精致完成、绑定可动画或实际演奏通过；C8旧头、其它角色P0和动态仍独立未验。

## 冻结与范围

源码、8组合全数值、完整receipt、保存后source-ID readback、两图、native、输入检查纠正历史、逐文件manifest均在本目录。docs同步`docs/research/paw-grip-local-tessellation-c35-2026-10-29.md`。原C25/C27/C29/C32/C33未改；未改hair/vendor、颜色、rig、动作、GLB、引擎或Cloudflare，无新增费用。

使用Blender本地bmesh/mesh API与vendored Scenario MIT审计helpers（固定commit d44410f058991f677ccf733a8e86ce95110857eb）；没有新云服务。拓扑改变后旧UV/groom/shape绑定仍须重建／验证，原坐标未动不等于旧面绑定自动有效。
