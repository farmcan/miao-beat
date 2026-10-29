# 薄琴身电吉他 · 单一最强几何备选

2026-10-30。**找到成熟、真实六弦的41.33mm薄琴身备选，原包已合法下载并只读核验。仅候选，不代表替换已获批准。原包含 royalty_free 材质，保持私有，不能进入 CC0 素材 release。** 本轮没有改猫 / 场景 / pose，没有新 rig，没有重建材质、导出 GLB 或渲染。

## 候选与作者原色图

**[HH Guitar with stand — Rexodus](https://www.blendkit.com/asset-gallery-detail/e641b80c-75ec-4888-b900-d63ef76057fe/)**（BlenderKit / Blendkit）。asset base `e641b80c-75ec-4888-b900-d63ef76057fe`，固定 version ID `73aaeeda-0e93-41de-8145-dccb68ee919f`，版本1。原生 Blender **4.0.1**，最后 native upload **2023-11-22**；没有用平台2026自动检查字段冒称作者持续维护。现有 Blender5.2.3可在 factory startup、disable autoexec 下打开并评估几何。

已实际看作者1024²原图：完整双拾音器蓝色电吉他，六弦、金属琴桥 / 品丝 / 旋钮、琴头卷弦和清楚的前后形体，成熟度足以交独立素材 judge。蓝色火纹是原图 / 材质的一部分；以后自建简单蓝 PBR 后不会自动保留这种效果。

![作者原色预览](/Users/levi/wrksp/miao-beat/artifacts/thin-guitar-alternative-2026-10-30/author-preview.png)

原色图确切本机路径：`/Users/levi/wrksp/miao-beat/artifacts/thin-guitar-alternative-2026-10-30/author-preview.png`。

## 下载、几何与尺寸实测

原包 `/Users/levi/wrksp/miao-beat/artifacts/thin-guitar-alternative-2026-10-30/hh-guitar-with-stand-original.blend`，**56,877,972 bytes**，SHA256 **`6a3cb4ad3124240e6d812c52b8ce25bb105e79de9a3ba1648544251f9f61a0ef`**。沿官方 anonymous download API + 随机 scene_uuid 协议下载，没有登录 / 插件 / 付费 / 签新条款；临时签名已从归档响应移除。原包前后 SHA 不变。

| 项目 | 只读实测 |
|---|---|
| `Body` 琴身真厚度 | 沿自身表面法线 **41.33410mm**；.70比例 **28.93387mm**，在原尺寸30–50mm目标内 |
| Body 主轴尺寸 | 宽362.95 × 长523.30 × 厚41.33mm |
| 作者摆位法线 | 约 **(0,−.99452412,.10450720)**；有约6°站立倾斜，因此 Body world Y bbox **87.25mm不能当厚度** |
| 去Stand后整琴 world bbox | min **(−.17541122,−.14737201,.01587138)**，max **(.18753836,.04271344,1.13272357)**m；size **(.36294958,.19008545,1.11685219)**m。包括琴头 / 五金 / 字标，排除名为`Stand`的对象和无面辅助路径 |
| 全琴沿Body法线总包络 | **101.18656mm**；.70后70.83mm。摇把 / 五金 / 琴头后件仍会突出，不能把整把含附件都称41mm薄 |
| 六弦 | `Spiral`、`.001`–`.005`，**6条独立真实Curve**，各1 spline，可评估出1548–2712个面；不是贴图线，也不把UV seam当多根弦 |
| 品丝 | 按Body轴投影判别 **24个真实横向品丝对象**，宽约49–65mm，截面约2mm；清单见测量JSON |
| 材质 / 纹理 | 17个材质；9张packed图（2K–6K）+1个未packed checker。存在Principled、复杂汽车漆 / 金属程序组与贴图，不能假设直接转标准GLB就等于原作者Cycles效果 |
| 原包结构 | 139 Mesh / 8 Curve / 8 Font / 1 Empty；没有 armature / 新 rig。9个嵌入文本 use_module=false，未执行 |

和当前琴作同口径区别：原古典琴**琴身壳体**厚约122.16mm，.70后85.51mm；本候选壳体.70后28.93mm，壳体减少约56.58mm。当前古典琴**整琴**.70包络约97.49mm，而此候选整琴五金包络约70.83mm。更薄的接触主体可能改善短臂 / 粗掌适配，但不会自动消除42.5mm掌核穿入；摇把、琴侧与实际掌腕依然要在独立选用后验证。

## 几何、材质许可必须分开

- **模型 / 几何声明：CC0。** 官方页面与API `license=cc_zero` 均已归档；固定资产信息、原URL、下载API在 `PROVENANCE.json`，CC0原文另存 `CC0-1.0-legalcode.html`。这不是 GitHub 代码许可推导。
- **原材质并非全包CC0。** native `asset_data` 的 Back / RIm（Blue Car Paint）、Black Painted Wood、Black Plastic、Car chrome、Car paint、Rubber、Sea Pearl、Simple Crystal、Steel round brushed等明确带 `royalty_free`；完整id / assetBaseId / license清单在 `material-license-tags.json`。原图还引用了单独下载的图像文件，未逐张独立追溯许可。
- [官方许可说明](https://www.blendkit.com/docs/licenses/)和[FAQ](https://www.blendkit.com/docs/licenses/licensing-faq/)允许渲染与较高层作品，也允许自制模型使用其材料；这**不能把嵌入材料单独重标CC0**。按本任务明确边界：原包及保留原材料 / 原图的GLB不公开再发，不放CC0 release。
- **只有实际选用后**才复制CC0琴几何，另用项目自建简单PBR / 程序节点重建全部材质，移除全部原图与相关上游节点 / 文本，然后重新核验衍生。此步骤本轮没有做。

## Stand / 字标与突出件清单

- 琴架：单独 Mesh **`Stand`**；根 Empty **`HH Guitar with stand`**。不能把架子一起装配到猫上。
- 八个Font字标：`Text` / `Text.001` / `Text.002` = **HH**；`Text.003` / `.004` / `.005` = **Noiseblaster**；`Text.006` = **Noiseblaster MK II**；`Text.008` = **Hendrik Haverkamp**。CC0不代表这些名称 / 字标已获商标授权；若选用应在衍生中排除，当前未移除。
- 五金总包络最高的 **`Tremelo.001`** 沿Body法线达164.87mm，而Body正面为125.47mm，相对面板突出约39.40mm；**`Killer`** 等件也跨较大深度。结构清单见 `accessory-brand-inventory.json`，只记录、不擅自删改。

## 下一步只到素材 judge

交独立素材 judge 看这张原色作者图 + source audit / 薄身量测，决定是否值得作为prop路线。即便通过，也先做不含原图 / 受限材料的干净几何衍生，再谈任何猫装配。没有把候选外观、薄身数字、原生打开成功当成成熟短臂猫已经可握持。

所有证据在 **`/Users/levi/wrksp/miao-beat/artifacts/thin-guitar-alternative-2026-10-30/`**（不是 upstream-guitar-candidates）：`source-audit.json`、`body-string-material-measurement.json`、`material-license-tags.json`、`accessory-brand-inventory.json`、原页面、官方条款、`PROVENANCE.json`与`SHA256SUMS`。源原包私有不改；没有泛找第二把。

## 后续受控准备

root随后明确授权仅CC0几何的清理与原创简单PBR适配。已完成独立后续记录：`docs/research/thin-guitar-clean-prop-2026-10-30.md`。原包仍私有不变；clean native / 兼容GLB与三张评审图在 `artifacts/miao-reuse-v1/thin-electric-clean/`，0原图 / 原材料，实际3.6导入通过，待独立craft；未装配猫。补充：原名`Killer`实为独立琴架U形颈托，clean中同Stand排除，非琴本体五金。
