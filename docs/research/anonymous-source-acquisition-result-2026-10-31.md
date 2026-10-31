# 免登录取源：实际取得两个文件，未通过角色门槛

2026-10-31。用户无法完成Google验证，明确选择免登录源。本轮不再请求邮箱/登录、不购买、不创建账户，实际取得下列文件并以Blender5.2.3后台factory-startup/disable-autoexec原样导入；没有修改模型几何、颜色、绑定或制作动作，没有应用发布。

## 1. Muru Cat：CC-BY公开衍生文件直链

[说明与署名](https://renderlyst.site/models/stylised-cat)、[匿名GLB直链](https://renderlyst.site/library/models/stylised-cat.glb)，实际无凭据HTTP200，558,040字节，SHA256 `b4213fd4bb016b2880520033d13ff5ee6c8798b93d4c322f8369ea02f6051bc9`。不是绕过Sketchfab登录或从viewer提取；分发页明确经Objaverse再分发、缩小/重编码贴图，文件extras也保留Muru/原SketchfabURL/CCBY4。公开原作者metadata独立核实CCBY4及concept作者Su Jian；若进一步分发须保留两者署名及修改说明。数据库ODC-BY不能替代逐模型许可。

实物GLB两mesh/六内嵌图、无skin/action。Blender原样导入，彩色与灰模正背三分之四以及线框都已实际查看。当前是带矛与武器的固定静态角色，关节和手部没有成熟绑定；诊断彩色显示眼部/表面异常，但未完成作者原效果与镜像/导入材质的归因，不能把这一点宣称为上游模型失败。它证明匿名获取/导入路径可用，**不是已合格演奏模板**，不为它重建手身。

## 2. Grigory_Petrov Cat Warrior Pack：作者正常免费入口

[作者页](https://grigory-petrov.itch.io/cat-warrior-pack) → Download Now → No thanks, just take me to the downloads → Download。实际无需登录、邮箱或付款；浏览器返回本地ZIP路径，已复制不可变原包并核对内容。不是以网站Free标签或下载页代替文件成功。临时下载标识不入文档。

ZIP273,890,100字节，SHA256 `a0385919b98ff1b03dfa542773e17d90787940847435548ba0382dfe2a37d1f7`。原包有静态GLB、基础FBX和Idle/Running/Death各自FBX、贴图/预览/README；不含原生.blend，Blender可实际导入。源名含Meshy_AI，不能冒称人工建模或源码开源。包内README与作者页均给游戏/项目RF含商用，禁原样转卖、NFT与AI训练；**不是CC0**。原包/模型不加入公开站点或Release，仅本地研究；本次只分享取源步骤、诊断和评审。

实物核对：GLB44,274,816字节，SHA `a1269a4a3f24b71678e9123af9573fa7b40af336161c010bae32d67bc93a852a`，一mesh20,593三角面、无骨骼/动画；Idle FBX另有33骨、蒙皮及1-408帧现有动作，未播放。不能由静态GLB推断整个包无rig，也不能把原包自带Idle当作已经完成弹琴。

## 实际评审结果

三位非builder均看完整正背/3Q、灰模/线框、脸和左右爪近图；root只做原样导入和诊断相机，不是原资产builder。

| 独立角色 | 结论 | 主要证据 |
|---|---|---|
| [形象](cat-warrior-source-identity-2026-10-31.md) | HOLD | 彩色可爱、新Q版身份成立，但灰脸眼眶/口鼻/面颊折面、后脑与甲片揉皱，近景精致度未签GO |
| [工艺](cat-warrior-source-craft-2026-10-31.md) | NO-GO | 彩色细节不能替代灰模；手爪两团圆突、右掌被盾挡，是当前明确手部P0；不靠重建脸手救源 |
| [接触](cat-warrior-source-contact-2026-10-31.md) | HOLD | 两叶爪可能整爪一键，不强求五指；但右掌面与腕甲/抱琴工作区尚未证明，不能签演奏通过 |

因此不进入乐器适配或动作优化。角色不同于旧橘猫/穿甲本身不是否决理由。文件取得是真进展，**新增合格角色仍为0**。待选下一模板时优先作者能展示清楚可弯掌指及原生材质的源，不再为免费降低标准或继续大改失败底模。

## 本地复核与跨电脑交接

原包、解包清单、sourceSHA、GLB/FBX审计和原样.blend在`artifacts/anonymous-cat-source-2026-10-31/`。完整场景front/3Q/back和灰wire审看板、掌脸近景同目录。用[原样导入脚本](../../design/anonymous-cat-source-2026-10-31/inspect_muru.py)复核静态；[FBX数据脚本](../../design/anonymous-cat-source-2026-10-31/inspect_fbx.py)只读rig/action结构；[诊断近景](../../design/anonymous-cat-source-2026-10-31/render_details.py)不能作生产分离肢体帧。三个脚本不重建角色，不播放新动作；需本机Blender和既有Blender expert审图helper，helper路径在脚本内明示。

其他电脑从上述公开来源重新下载，先比SHA，再按同目录放置；不要把本地273MB原包当作已经push或公开授权再分发。源文件不需Google会话。主站仍是此前版本，没有部署新猫。
