# 原图对齐与结构优化：当前断点

执行计划见 `docs/character-engine-comparison-plan-2026-10-28.md`。用户仍拒绝当前粗糙度；旧技术样机、C5条件放行、C8锚点对齐、工具能运行，都不能代替原图美术或实际动作验收。

## 可在别的电脑直接看的证据

- `evidence/C8r2-gray/`：实际相机/琴/连体抱持调整；三方只允许继续彩色观察。
- `evidence/C8r2-color/`：完整彩色基准，手爪/头耳仍有P0，未接受。
- `evidence/C9-failed/`：使用新本地helper的局部primary试验，三方失败，未扩彩色/动作；保留实际执行脚本快照与receipt。
- `evidence/D0-3-failed/`：此前眼睑盖帽失败，不复用为闭眼成品。

这些图都是完整猫/双臂爪/琴同帧；没有分离手臂贴片。原图一直是 `public/character/instrument-scenes-v1/guitar/idle.jpg`。原生临时工程在忽略的artifacts，不把80MB失败版本重复入Git。

## 免费本地工具

`vendor/scenario-blender/`是固定 `scenario-labs/skills@d44410f058991f677ccf733a8e86ce95110857eb` 的三个**未修改**MIT helper及许可、sha。核心为 `bx_sculpt.py` / `bx_retopo.py`；第三个 `bx_audit.py` 是拓扑函数的局部依赖。上游技能不是自动美术服务，也不需要Scenario API/key/MCP。版权声明保留，第三方脚本不冒充本项目原创。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
  --python-exit-code 1 --python design/character-sculpt-v2/local-skill-probe.py
```

probe在609k完整模型的临时副本上实际测射线/曲率、mask/grab/shape key和关节stations，源文件sha不变；并不输出“精致度分数”。抱琴不对称，关闭symmetry，不套人头head_guides。`on_surface`射线miss会nearest fallback：C9一笔偏落约0.217单位，因此后续必须明确ray hit/miss和残差、错位停止，不能只数changed_vertices。

## 从Git内C5母工程重建研究基准

已有 `miao-plush-static-study.blend` 仅作拥有权/原生源checkpoint，不是已通过最终美术。按顺序运行以下脚本；所有命令都用上面相同Blender路径及 `-b --factory-startup --python-exit-code 1 --python`。脚本在CPU/GPU本机运行，不调用模型API；会真实渲染多张检查图，耗时视机器而定。

1. `d0-rest-binding.py`，默认得到 `artifacts/character-sculpt-d0/miao-d0-rest-bound.blend`。
2. `d0-groom-binding.py`，默认得到 `artifacts/character-sculpt-d0-groom/baseline-attached.blend`。
3. `eye-inset-study.py`，当前默认输出 `artifacts/character-eye-inset-v4/`；只静态眼部重建，不含blink。
4. `eye-cornea-study.py`，输出 `artifacts/character-eye-cornea-v2/`；实际角膜/linked光卡，透明阴影有已注明近似。
5. `eye-optics-light-tune.py`，输出 `artifacts/character-eye-cornea-v3/`。
6. `fidelity-hold-study.py -- --out artifacts/character-fidelity-c8-r2-color --size 1024 --samples 64`，生成本次彩色原生基准。另用 `--gray --out artifacts/character-fidelity-c8-r2` 可生成灰模副本和probe所需路径。

不要将失败研究脚本直接连正式首页。C9若需复现，仅作失败诊断：`anatomy-primary-study.py`使用上面C8彩色路径与vendored工具，不依赖当前电脑全局skills安装。旧raw receipt/hash与“后续评审未通过”分开保留。

## 下一项制作

唯一先行最弱环节是完整按弦掌趾重建：掌背穹顶→短趾根→弯趾/趾腹→腕，按原图与真实琴颈构造连续环线，不再整体拉伸旧袋掌。制作人不做judge。后续拨弦爪、口鼻、耳壳的已知P0也要逐项修；换拓扑后原UV/groom/shape/接触证据失效，需重绑重验。全部静态关过后才扩真实动作和随机行为。

Godot已安装且有独立中性材质probe，见 `design/godot-character-lab/README.md`；这不是已做出的Godot猫版本。最终Blender/Godot必须同角色、同机位、同事件，实际看片和点击验证一次触弦/连续/停止，不以日志替代动作judge。
