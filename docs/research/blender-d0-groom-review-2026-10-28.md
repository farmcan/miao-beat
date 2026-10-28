# D0.2真实猫体短毛跟随：三方独立窄范围复核

2026-10-28。Builder为`modelr_trial`。三位非builder各自实际打开最终512px `baseline-attached.png`与`local-paw-perturbation.png`，对照C5 1024px静帧和原图`idle.jpg`，并读receipt／官方native validity记录。本次与独立小平面probe不同：真正609383点猫体、180000根四点native groom已实际执行。

**三方未见本次小扰动引入新P0，允许继续窄范围眼睑闭合／一次拨弦验证。D0整体、正式演奏和角色精修没有据此完成。**

| 非builder评审 | 实图／证据结论 | 保留边界 |
| --- | --- | --- |
| `reference_geometry`：身份／轮廓 | 未见大块脱毛、色块归零、断纹或前臂亮缝复现；猫、相连双爪和琴仍在同帧。 | C5所有精致度P1保留；512px及此微小形变不能替代1024材质复验，也不能把小平面probe当同一资产通过。 |
| `gpu_route`：材质／工艺 | 条纹、cream、木材及完整画面保持；读最终180000 valid、单根修复和累计4张渲染，图SHA与receipt相符。 | 数值仅定位变化，不是审美分；没有证明真实眨眼／完整触弦／头动／连续防泳动或网页组合。 |
| `modelr_contact_judge`：爪体／跟随 | 未发现新增明显爪体塌陷、腕部断裂、脱毛或滞留毛团；支持本次小扰动的毛根跟随技术结果。 | 长扁前爪、较大握掌P1保留；正面512静图不能排除细小脱根或全局碰撞，不证明自然拨弦或大角度关节形变。 |

## 实际结果及错误没有省略

- 保留已有`UVMap`及hash，另建专用不重叠guard-band `BindUV`；首轮“无UV”的假设被实际预检纠正，不覆盖原数据。官方NEAREST生成根UV，内建Deform Curves on Surface实际求值。
- 早期自定义解码检查通过后，额外官方`Sample UV Surface.Is Valid`仍找到1根invalid（139545）；不能据有限距离或图片看不到就忽略。只在同一polygon／triangle内轻推该根UV约1.507e-6，保留原NEAREST快照，未删毛／放宽阈值。最终及重开最终blend均为180000／180000 valid、0 invalid。
- 最终根到求值表面最大最近距离约4.74e-5场景单位，UV目标最大误差约8.22e-5，原1e-4门槛未放宽。720000点rest属性hash在静止及扰动中保持。
- 此技术扰动的参数上限.02u，实际最大Z位移.01149u；6187根实际随动。不是有正确时序、接触和回收的一次真实拨弦。
- 最终pair真实重渲染2张，之前有2张在native唯一invalid发现前渲染，旧pair保留在`attempt-3-pre-native-fix`。**本小项累计4张GPU渲染，不能称总共2张。**
- D0.1→最终D0.2静止图RGBA平均绝对差约.004301／255，最大6，仅6像素RGB差>3、0像素>12；小扰动较大变化集中在拨弦臂ROI。仅为变化定位及外观保持证据，不作为自然度评分或hair专属shader AOV插值证明。

[说明与复现](../../design/character-sculpt-v2/d0-groom-binding-README.md) · [最终图／receipt](../../design/character-sculpt-v2/evidence/D0-2/)。独立hair着色器AOV、真实闭眼、单次触弦／离弦、头眼身体配合、网页和音视频导出仍需完成相应验证；C5不能因此被称最终美术交付。
