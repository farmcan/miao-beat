# 分支合并与本地约束求解的实际预检

## 头部与按弦爪可以按来源身份合并

`character-branch-merge-preflight.py`只读打开原C8、C20与C25，没有生成合并候选。

- C8与C20的求值body都为609383点/609060面，逐序拓扑hash相同。
- C20相对C8只改38210个头部点，原Z范围2.5002–3.4655；C25保留全部这些点的源身份。
- C25保留585434个C8源点，位置误差0。C20发生变化而被C25裁掉的源点为0。
- 因而可以经`C23 source vertex id`传递精确C20−C8形变，不需要最近点猜配，也不覆盖新手。
- 17个脸部feature名字一致，但10个眼/眼睑/角膜和鼻子数据确有差异，后续必须按C20恢复完整feature几何，不能只搬眼材质。

以上只是合并可行性，不是已经合并、颜色/毛/眼动态通过。新手UV、groom和绑定仍需独立重建或验证；不能把来源ID当这些能力的证明。原生来源SHA和具体字段在local `artifacts/character-branch-merge-preflight/receipt.json`。

## 使用真实本地QP库

先前五点RBF能闭合五个gap却会推掌入琴。C29因此复用[OSQP](https://osqp.org/docs/)稀疏QP，以实际contact等式、木件/弦tube外侧不等式及平滑位移界求可行性。OSQP为Apache2.0，Python接口支持稀疏约束与warm start；算法能力不等于本模型已无碰撞。

隔离venv位于local `artifacts/c29-qp-env/`，CPython3.14.2、OSQP1.1.1、SciPy1.17.1；锁定依赖在`design/character-sculpt-v2/requirements-qp.txt`。使用外部CPU进程读写NPZ，避免把不兼容wheel塞进Blender Python。没有hosted solver、API key、订阅或新增现金。

```sh
python3 -m venv artifacts/c29-qp-env
artifacts/c29-qp-env/bin/python -m pip install --only-binary=:all: --index-url https://pypi.org/simple -r design/character-sculpt-v2/requirements-qp.txt
```

初装沿用了机器已有公共镜像配置；最终显式以官方PyPI force reinstall，全部wheel SHA又独立与官方version JSON逐项匹配。许可证证据保留唯一编号路径，避免macOS大小写不敏感把多个LICENSE文件覆盖；SciPy传统dist-info/LICENSE.txt也纳入。具体版本、官方URL、hash、license路径在local setup receipt，早期错误路径清单保留不当权威证据。

官方示例小QP已真实实跑，解[.3,.7]，primal residual0、dual约4.44e-16。它只证明环境/库可用，不能替代猫的actual BVH、内部parity、self-intersection和真实渲染门禁。
