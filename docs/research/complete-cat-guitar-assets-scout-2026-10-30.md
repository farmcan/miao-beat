# 完整抱琴猫现成资产 · 一次 focused scout

2026-10-30。**本轮没有找到同时满足“成熟可爱猫 + 已完整抱吉他 + 模型可合法下载 + CC0/CC BY 或开放再分发”的可直接 import 强候选，推荐数为0。** 不能据此说这种资产不存在；只说明此次限定搜索没有获得可用结果。也不能据此推导必须继续自行拼装当前猫。

范围：一次聚焦检索 `cat playing guitar 3D model download`、`cat guitarist 3D blend download license`、`bard cat Sketchfab download`，再到同一官方 Sketchfab 目录核对标题与公开 metadata。没有改已有 pose / blend，没有继续量测参数，没有新引擎调研。最多保留以下三个最接近的**排除记录**，不是凑出的三项推荐。

## 最近的整套抱电吉他资产：下载 / 许可不满足

[Cat Guitarist Character Animated — KamillaKraus](https://sketchfab.com/3d-models/cat-guitarist-character-animated-bbfb78e6183e417c8e8d71e7d8d4c467)，2023-06-02 发布。[官方 metadata](https://api.sketchfab.com/v3/models/bbfb78e6183e417c8e8d71e7d8d4c467)。

实际看过作者1920×1080预览：完整角色、双臂 / 人形手和电吉他已在同一场景里，左手位于颈部、右手在琴身一侧，比“只有一只猫、另配一把琴”更接近整体复用方向。但角色是猫耳 / 耳机 / 面罩造型的拟人角色，人手细长，视觉方向与温暖橘猫差距大；单一预览也不能证明所有手指落弦无穿模。

官方字段：`isDownloadable=false`，license **Standard**，非 CC0 / CC BY；API 标 `animationCount=1` 只证明有一条发布动画记录，本轮没有实际检查动画接触或源 rig。公开 metadata 有 GLB / glTF / USDZ / source archive 描述，但这些是服务侧展示 / 转码信息，**不能把 viewer archive 当成公开下载授权**。没有确认原生 `.blend` / FBX 类型，没有可合法取得的开放源包，不能作为当前直接 import 路线。未买、未签新条款、未抓取 viewer 模型。

![作者完整抱琴预览](../../artifacts/complete-cat-guitar-assets-scout-2026-10-30/bbfb78e6183e417c8e8d71e7d8d4c467-author-preview.jpg)

## Bard Cat：成熟整套雕像，但乐器和使用许可都不匹配

[Bard Cat — Rupert Dyn](https://sketchfab.com/3d-models/bard-cat-8cb85dfb5ead427997e571ee0ba93030)，2023-03-16 发布。[官方 metadata](https://api.sketchfab.com/v3/models/8cb85dfb5ead427997e571ee0ba93030)。

作者预览实际显示猫吟游诗人完整雕像、服装 / 口部表情 / 双手与乐器一体，雕刻制作比粗糙 low-poly 替代品成熟；**抱的是手风琴 / 风箱类乐器，不是吉他**，不能替代握颈与拨弦链路。作者说明是28mm以上打印雕像，原提供格式 **STL**，另有底座；没有可动 rig 证据，API animationCount=0。

`isDownloadable=false`，license **Editorial**。不满足本项目可修改、渲染并公开再分发所需的开放模型许可；展示侧 archives 中列出的 GLB 不改变这一边界。不把高质量打印雕像冒称现成动画 rig。

![Bard Cat作者预览：手风琴雕像](../../artifacts/complete-cat-guitar-assets-scout-2026-10-30/8cb85dfb5ead427997e571ee0ba93030-author-preview.jpg)

## Catatomic：许可较开放，但实物没有抱琴

[Catatomic — spartancat70968](https://sketchfab.com/3d-models/catatomic-70c30481ebb7424c9ecb481f0c11aa47)，2022-03-23 发布。[官方 metadata](https://api.sketchfab.com/v3/models/70c30481ebb7424c9ecb481f0c11aa47)。

作者描述称角色是 lead guitarist，但实际作者预览是红色机械猫 **T pose，没有吉他、没有双手接触乐器**。因此不属于“整体已经抱琴”的资产。没有因为名称 / 描述命中就当作成熟抱琴成品。

官方 `isDownloadable=true`、license **CC Attribution / CC BY 4.0**，可在署名等条件下商用 / 修改；目录列 **GLB、glTF、USDZ、source**，GLB约28.7MB，1条动画记录。原生 source 具体是 `.blend` 还是FBX，本轮未取得源包，未知；公开可下载标志也不等于本机下载 / 格式 / rig 实测成功。没有下载模型或进行接入，因为视觉预筛已不符合完整抱琴目标。

![Catatomic作者预览：无琴T pose](../../artifacts/complete-cat-guitar-assets-scout-2026-10-30/70c30481ebb7424c9ecb481f0c11aa47-author-preview.jpg)

## 结论与证据边界

- 当前0个强候选，无直接替换建议。不拿猫耳人物、手风琴雕像、只有“吉他手”背景故事的 T pose 代替完整抱木吉他的成熟猫。
- 其他搜索结果以[付费 OBJ 打印猫](https://cults3d.com/en/3d-model/art/cat-playing-guitar-3d-model)、PNG / AI 图片、付费成片为主；搜索摘要不是源模型交付，也未进入推荐。
- 作者网页在 web 文本抓取中403；没有把403当成不存在。许可 / 下载状态使用无需登录的**官方公开 model API**核验，预览取作者官方 thumbnail URL，并实际打开本机查看。没有访问用户账号、创建账号、接受条款或绕过下载控制。
- 下载了公开作者预览与 metadata，**没有下载三维模型、没有 import / Blender 验证**；因此没有声称手部成熟 rig 或动画已实测通过。没有以 GitHub 仓库代码许可代替模型许可。
- 证据目录：`artifacts/complete-cat-guitar-assets-scout-2026-10-30/`，保留本轮目录结果、三份 model detail JSON、三张作者预览、provenance 与 SHA256。浏览器 / API 中的 `Standard`、`Editorial`、CC BY 信息按模型逐项保留，没有合并为同一许可。

本轮到此停止，不扩散搜索，不开启付费或联系作者流程，也不对当前失败抱琴 pose 追加迭代。
