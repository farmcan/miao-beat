"""Explicit reviewed documents/art only; never exports the repository or runtime files."""
from pathlib import Path
import argparse, hashlib, html, json, shutil, struct
from markdown_it import MarkdownIt
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--target',required=True);p.add_argument('--owner-origin',required=True);args=p.parse_args()
out=Path(args.target).resolve()/'site/reviews/miao-beat';out.mkdir(parents=True,exist_ok=True)
md=MarkdownIt('commonmark',{'html':False}).enable('table')
entries=[('v2','第二版交付与验收','docs/v2-release-2026-10-22.md'),('v2-animation','动画与优秀参考','docs/research/v2-animation-and-guidance-2026-10-22.md'),('v2-scores','九项参考谱来源','docs/research/scores-v2-2026-10-22.md'),('decision','主题与下一步','docs/research/theme-and-release-decision-2026-10-22.md'),('audit','首版交付矩阵','docs/research/first-version-audit-2026-10-22.md'),('hotspots','热点逐项核验','docs/research/hot-meme-evidence-2026-10-22.md'),('bottles','瓶子与优秀参照','docs/research/bottle-instrument-and-theme-2026-10-22.md'),('mobile','手机与全屏演奏','docs/mobile-performance-2026-10-22.md'),('samples','真实采样与许可','docs/research/sample-manifest-2026-10-22.md'),('plan','计划与确认边界','docs/plan.md'),('verification','生产验收历史','docs/verification-2026-10-22.md'),('product','初轮：作品与键位','docs/research/product-and-keyboard.md'),('audio','初轮：声音与节拍','docs/research/audio-and-timing.md'),('animation','初轮：角色与动画','docs/research/animation-and-experience.md'),('recording','初轮：参考谱与小文件','docs/research/scores.md'),('character','初轮：角色生产方案','docs/research/character-production-plan.md')]
archive={'product','audio','animation','recording','character'}
entries = [
 ('character-decision','猫咪：三方案与最终取舍','docs/research/character-design-decision-2026-10-22.md'),
 ('character-visual','造型独立评审','docs/research/character-visual-judge-2026-10-22.md'),
 ('character-motion','动作独立评审','docs/research/character-motion-review-2026-10-22.md'),
 ('character-interaction','互动情绪独立评审','docs/research/character-interaction-judge-2026-10-22.md'),
 ('cross-content','交叉评审：造型','docs/research/character-cross-review-content-2026-10-22.md'),
 ('cross-ux','交叉评审：动作','docs/research/character-cross-review-ux-2026-10-22.md'),
 ('cross-tech','交叉评审：互动','docs/research/character-cross-review-tech-2026-10-22.md'),
 ('pop-songs','三首点歌的来源与缺口','docs/research/pop-song-support-2026-10-22.md'),
] + entries
nav=''.join(f'<a href="#{slug}">{title}</a>' for slug,title,_ in entries if slug not in archive)+'<a href="#research-archive">早期研究归档</a>'
chapter_paths={(root/file).resolve():slug for slug,_,file in entries}
def render_document(text, file):
 tokens=md.parse(text)
 def rewrite(tokens):
  for token in tokens:
   if token.type=='link_open':
    href=token.attrGet('href') or ''
    if href and not href.startswith(('#','https://','http://','mailto:')):
     target=((root/file).parent/href.split('#')[0]).resolve()
     if target in chapter_paths:token.attrSet('href','#'+chapter_paths[target])
     else:raise ValueError('Unexported local reference in '+file+': '+href)
   if token.children:rewrite(token.children)
 rewrite(tokens)
 return md.renderer.render(tokens,md.options,{})
sections=[]
archived=[]
for slug,title,file in entries:
 text=(root/file).read_text()
 assert not any(x in text for x in ['/Users/','oauth_token','xsec_token='])
 if slug in archive:
  text='> 初轮研究快照：下文保留当时的建议、候选与待确认项。用户后续已确认真实音色和毛绒角色路线，并追加吉他/架子鼓；当前实现和验收以本页「计划与确认边界」「实际验收与边界」为准。\n\n'+text
 body=render_document(text,file).replace('<table>','<div class="table-wrap"><table>').replace('</table>','</table></div>')
 section=f'<section id="{slug}" class="chapter"><span class="eyebrow">研究 · 2026-10-22</span><div class="prose">{body}</div></section>'
 (archived if slug in archive else sections).append(section)
sections.append('<details id="research-archive" class="archive"><summary>早期研究归档 · 5篇（保留来源与当时建议）</summary>'+''.join(archived)+'</details>')
concept='character-concept-v1.png';shutil.copy2(root/'design'/concept,out/concept)
candidate_data=json.loads((root/'design/candidates/review.json').read_text())
candidate_files=[]
candidate_cards=[]
for candidate in candidate_data['candidates']:
 name=candidate['file']
 assert Path(name).name == name and name.endswith('.png')
 assert hashlib.sha256((root/'design/candidates'/name).read_bytes()).hexdigest() == candidate['sha256'], 'Candidate provenance differs: '+name
 width,height=struct.unpack('>II',(root/'design/candidates'/name).read_bytes()[16:24])
 shutil.copy2(root/'design/candidates'/name,out/name)
 candidate_files.append(name)
 esc=lambda value:html.escape(value,quote=True)
 candidate_cards.append(f'''<article class="candidate-card" id="candidate-{esc(candidate['id'])}"><header><span class="eyebrow">{esc(candidate['id'])} · 独立设计</span><h3>{esc(candidate['name'])}</h3><p>{esc(candidate['verdict'])}</p></header><a href="./{esc(name)}" target="_blank" rel="noopener" aria-label="查看{esc(candidate['name'])}原图"><img src="./{esc(name)}" width="{width}" height="{height}" alt="{esc(candidate['alt'])}" loading="lazy"></a><p class="candidate-caption">{esc(candidate['detail'])} <a href="./{esc(name)}" target="_blank" rel="noopener">放大看原图 ↗</a></p></article>''')
gallery='''<section id="character-lab" class="character-lab"><span class="eyebrow">CHARACTER LAB · 三位独立设计 / 三位交叉评审</span><h2>先让它像一只爱玩音乐的猫。</h2><p>以下是原创静态概念板，不是已接入游戏的动画。三个方向都展示钢琴、吉他、架子鼓，比较角色本身的可爱度、演奏意图和可实施性。</p><aside class="decision"><strong>本轮选择：'''+html.escape(candidate_data['selection'])+'''</strong><p>'''+html.escape(candidate_data['reason'])+'''</p><a href="#character-decision">看取舍、交叉评审与落地顺序 ↓</a></aside>'''+''.join(candidate_cards)+'''</section>'''
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Miao Beat首版、竹知了与滑动变祖器核验、瓶子乐器方案和传播实验，保留来源与验收边界。"><title>Miao Beat · 轻量音乐创作研究</title><link rel="icon" href="/icons/miaoti.svg"><link rel="canonical" href="OWNER_ORIGIN/reviews/miao-beat/"><link rel="stylesheet" href="/reviews/style.css"><link rel="stylesheet" href="./review.css"></head><body><header class="topbar"><a class="brand" href="/reviews/">项目复盘与优化</a><a href="https://miao-beat.pages.dev/">去演奏 ↗</a></header><main class="reference"><header class="chapter-header"><span class="eyebrow">MIAO BEAT · 2026-10-22</span><h1>让猫把身边的声音弹成歌。</h1><p>第二版已上线：九项可选参考谱、音频时钟时间线、跟弹亮键与更自然的连续猫爪。这里保留优秀作品的源码研究、主题判断、素材来源和实际验收边界。</p><div class="actions"><a href="https://miao-beat.pages.dev/">打开音乐工作台 ↗</a><a href="https://github.com/farmcan/miao-beat">独立仓库 ↗</a><a href="#v2">第二版验收 ↓</a><a href="#decision">主题结论 ↓</a></div></header><aside class="decision"><h2>第二版：先听一遍，再跟着亮起的键弹</h2><p><strong>“听一遍”会播示范，“跟着弹”只给节拍与提示；不判分，随时自由发挥。</strong>选谱放进演奏区，手机全屏也可用。稳定猫咪主题，下一步优先试听瓶子乐器；瓶子仍为提案，没有加入线上音库。当前采用 smplr + 自托管真实钢琴、马林巴、尼龙弦吉他与八件架子鼓。角色已接入原创四组件2.5D毛绒猫，头部、左右爪和节拍反应分开；不依赖GIF切换，不是真3D。</p><p>当前新版采用四组自托管真实采样；旧事件文件保留原合成引擎。自动解码/音量检查和浏览器发声验证不等于主观听感或手机端延迟已验收。事件文件只保存时间与按键，导出/导入/回放不需要上传音频。</p></aside><figure class="concept"><img src="./character-concept-v1.png" width="1254" height="1254" alt="原创黑色毛绒小猫戴绿色耳机，前爪放在小键盘上，静态角色方向图"><figcaption><strong>原创角色方向图 v1</strong><br>内置 imagegen 生成，提示词与哈希保存在独立仓库 design/。这是静态概念图，尚不是3D模型或完成动画；试玩已使用由该方向衍生的四组件毛绒猫：头部轻跟随、左右爪可独立重打。这张旧图仍仅作美术方向对照。用户提供的追光猫笔记已核对制作描述，来源与未知项见动画章。</figcaption></figure><nav class="review-nav" aria-label="研究目录">'''+nav+'''</nav>'''+''.join(sections)+'''<footer class="footer"><a href="/reviews/">全部项目</a><span>研究快照 2026-10-22 · 事实、建议、待验证分开</span><a href="https://miao-beat.pages.dev/">去演奏 ↗</a></footer></main></body></html>'''
assert args.owner_origin.startswith('https://')
page=page.replace('<h1>让猫把身边的声音弹成歌。</h1>','<h1>一只真的爱玩音乐的小猫。</h1>')
page=page.replace('<p>第二版已上线：九项可选参考谱、音频时钟时间线、跟弹亮键与更自然的连续猫爪。这里保留优秀作品的源码研究、主题判断、素材来源和实际验收边界。</p>','<p>新增三种猫乐手设计与交叉评审：先选有性格、有演奏神态的角色，再制作可打断的轻量动画。下方保留已上线第二版的验收与来源。</p>')
page=page.replace('<a href="#v2">第二版验收 ↓</a>','<a href="#character-lab">三种猫乐手设计 ↓</a><a href="#v2">第二版验收 ↓</a>')
page=page.replace('<aside class="decision"><h2>第二版：',gallery+'<aside class="decision"><h2>已上线第二版：',1)
page=page.replace('OWNER_ORIGIN',html.escape(args.owner_origin.rstrip('/'),quote=True))
(out/'index.html').write_text(page)
(out/'review.css').write_text('''.reference{max-width:1120px}.archive{margin:36px 0;border:1px solid #cbd1c8;border-radius:12px;padding:18px}.archive summary{cursor:pointer;font-weight:700}.prose{overflow-wrap:anywhere}.review-nav{max-height:160px;overflow-y:auto}.actions{display:flex;flex-wrap:wrap;gap:12px;margin:20px 0}.actions a{border:1px solid #cbd1c8;border-radius:8px;padding:10px 14px;text-decoration:none}.decision{padding:22px;background:#f3f4eb;border:1px solid #cbd1c8;border-radius:12px;margin:25px 0;line-height:1.9}.decision h2{margin:0 0 12px}.concept{display:flex;align-items:center;gap:24px;background:#eeeee5;border-radius:12px;margin:25px 0;padding:20px}.concept img{width:240px;height:240px;object-fit:contain}.concept figcaption{font-size:14px;line-height:1.9;max-width:560px}.review-nav{display:flex;gap:8px;flex-wrap:wrap;padding:14px 0;border-block:1px solid #d5d7ce;background:#fafaf6;position:sticky;top:0;z-index:2}.review-nav a{padding:8px;font-size:13px}.chapter{padding-top:32px;scroll-margin-top:85px;border-bottom:1px solid #d8dace}.prose h1{font-size:28px;line-height:1.4}.prose h2{margin-top:32px}.table-wrap{overflow-x:auto;margin:22px 0}.prose table{font-size:13px;min-width:680px;line-height:1.8}.prose td,.prose th{padding:12px;vertical-align:top}.prose pre{overflow:auto;padding:16px;background:#f1f1eb}.prose a{overflow-wrap:anywhere}@media(max-width:600px){.concept{display:block}.concept img{display:block;margin:auto;width:220px;height:220px}.review-nav{position:static}.prose h1{font-size:23px}.decision{padding:16px}.actions{gap:8px}.actions a{font-size:12px}}''')
with (out/'review.css').open('a') as css:
 css.write('''.character-lab{margin:40px 0;scroll-margin-top:24px}.character-lab h2{font-size:30px;line-height:1.35}.character-lab>p{line-height:1.8;color:#536257}.candidate-card{background:#f6f3eb;border:1px solid #d6d8ca;border-radius:20px;overflow:hidden;margin:24px 0}.candidate-card header{padding:24px 24px 0}.candidate-card h3{font-size:24px;margin:8px 0}.candidate-card header p,.candidate-caption{line-height:1.8}.candidate-card img{display:block;width:100%;height:auto}.candidate-caption{padding:0 24px 20px;color:#526050;margin:12px 0 0}.candidate-caption a{white-space:nowrap}@media(max-width:600px){.character-lab h2{font-size:26px}.candidate-card header{padding:18px 18px 0}.candidate-caption{padding:0 18px 18px}.candidate-card h3{font-size:21px}}''')
files={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['index.html','review.css',concept]+candidate_files}
(out/'build-manifest.json').write_text(json.dumps({'source_repository':'https://github.com/farmcan/miao-beat','generated_date':'2026-10-22','files':files},indent=2)+'\n')
print(f'Exported {len(files)} reviewed Miao Beat files; repository and recordings excluded')
