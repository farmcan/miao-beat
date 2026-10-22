# 毛绒猫 2.5D 分层小样交付

日期：2026-10-22。生成工具：内置 `image_gen.imagegen`，没有调用 CLI/API fallback。采用项目已有 `character-concept-v1.png` 作身份与材质参考，镜头改为正面；第一次 atlas 有越格问题，针对排版重生成一次，采用第二张原始透明 PNG。

交付文件：

- `public/character/plush-atlas-v1.png`：原样 RGBA PNG，1254×1254，1,563,258 字节，SHA256 `def3d68c71fc6d288325a0e61284cb909bb581a2c8de53dbad36329454611c48`。
- `public/character/rig.css`：外部同源样式，兼容现有严格 CSP。
- `public/character/manifest.json`：生成提示词、来源概念 SHA、各文件 SHA、四格坐标、舞台位置/pivot、实际检查与未验证边界。
- `public/character/README.md`：不包含个人站点或机器路径的公开说明。
- `public/character.js`：导出 `mountCharacter(scene)` 与 `CHARACTER_LAYOUT`；不修改应用、页面或构建文件。

接入：

```js
import {mountCharacter} from './character.js';
const character=mountCharacter(scene);
// 在已有 visual(key) 中调用；左右爪分别 cancel/restart，不依赖 hit class 重加。
character.strike(key.paw);
// ready Promise 仅在 PNG 和外部 CSS 均成功时 resolve(true)。
// character.destroy() 会取消动画、去掉新层与 stylesheet，并恢复旧角色。
```

四组件是独立 SVG group，用 nested SVG viewBox 取 atlas 四个 627×627 tile；共用同一缓存图片。使用现有 viewBox 640×300。新躯干在道具后、双爪在道具前、头盖住短前臂的根部；旧头/躯干/尾/爪仅在加载成功后隐藏。没有把完整静态猫图整张摇动当成关节控制。

指针仅驱动头的小幅位移/转角；头图包含固定眼睛，未做独立瞳孔层、眨眼或真实 3D 骨骼。单爪打击用独立 190ms Web Animations 对象；同侧快速触发会取消并重开，不影响另一只爪。`fill:none` 结束后回到 held CSS 状态。reduced-motion 关闭呼吸、点头、爪动画与指针跟随。

实际 Chrome 浅底检查了钢琴、吉他、架子鼓三种组合：毛绒猫可见，道具与新层遮挡合理，正常比例下没有发现黑底图预览中那些可疑红黄点。客观 alpha 检查表明约59.25%像素完全透明；躯干细毛有19个 alpha>8 像素触到上右 tile 最下一行，已在 manifest 明记，没有伪称四格各有10%净空。未验证任意大比例/暗背景的边缘质量与手机帧率。

只读 DOM 镜像不暴露 `getAnimations()`，未以它当失败或通过证据。另用 JSDOM + 可控 Image/load/animate 进行了可重复检查：四层独立、重复 mount 复用 controller、PNG/CSS 均就绪后才切换、无 inline SVG style、同侧重复 strike 取消旧动画/保持对侧独立、190ms/fill:none、destroy 恢复旧场景，全部通过。最终生产 CSP、真实按键/导出导入整体闭环由根任务继续验收。

开发检查页已移出产品目录到 `artifacts/character/preview.html`，不会进入公开构建。从仓库根静态服务时可用于再次查看；它不加载音频。没有个人站点回链。
