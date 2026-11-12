"""Prepare a user-operated review page. No browser is launched or controlled."""
from pathlib import Path
from html import escape
from urllib.parse import urlencode
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'preview/review-20261111'
OUT.mkdir(parents=True,exist_ok=True)
screens=json.loads((ROOT/'runtime/screens.json').read_text(encoding='utf-8-sig'))['screens']
batches=[(1,10,'登录、大厅与好友房'),(11,22,'牌局、结算与回放'),(23,32,'排位、赛事与残局'),(33,35,'角色与六套道童服装'),(36,40,'商城、背包与资料'),(41,50,'社交、任务与系统'),(51,60,'公共控件、牌组、聊天与特殊状态')]
def link(p,state=None,aspect='wide',label=None,**params):
    query={'screen':p['id'],'aspect':aspect,**params}
    if state is not None:query['state']=state
    return '<a target="_blank" rel="noopener" href="../../runtime/art-preview.html?'+escape(urlencode(query),quote=True)+'">'+escape(label or p['title'])+'</a>'
parts=['''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>道友请出牌 · 请审核这一批</title><style>
body{margin:0;background:#f5f0e2;color:#173f32;font:16px/1.65 "Microsoft YaHei",sans-serif}main{max-width:1240px;margin:auto;padding:28px}h1{margin-bottom:8px}a{color:#166145}a:hover{color:#9a5e19}.notice{border:2px solid #c2984c;background:#fff8e8;padding:16px;border-radius:10px}.links{display:flex;gap:8px;flex-wrap:wrap}.links a,nav a{display:inline-block;padding:5px 10px;border:1px solid #beaa79;border-radius:5px;background:#fffcf4;text-decoration:none}section{margin:26px 0;padding:20px;background:#fffcf5;border:1px solid #d1c29c;border-radius:10px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:10px;border-bottom:1px solid #ddd0af;vertical-align:top}td:first-child{min-width:190px}.states{display:flex;flex-wrap:wrap;gap:7px}.states a{white-space:nowrap}small{color:#65715f}h2{font-size:22px}@media(max-width:700px){main{padding:12px}table,tbody,tr,td{display:block}th{display:none}td{border:0}.states{padding-bottom:12px}section{padding:12px}}</style><main>
<h1>请审核这一批</h1><p>《道友请出牌》斗地主美术候选版 · 2026-11-11 · 待用户审核</p>
<div class="notice">本批修复了列表和卡片裁切、特效切页残留，以及角色、服装和状态的显示绑定。请检查两种横屏比例、动作实速及状态内容。文件与来源检查通过不等于用户视觉批准；整款客户端终验仍未完成。</div>
<p>点击界面或状态会打开当前候选版。状态链接明确包含第 0 态；也可在预览顶部切换角色、动作、场景和牌桌。审核结果请按“页号 / 状态 / 问题”反馈。</p>
<nav class="links"><a href="../../runtime/art-preview.html" target="_blank">当前分层预览</a><a href="../../assets/animations/characters/index.html" target="_blank">角色与六套服装播放器</a><a href="motion/index.html">已有实速录像（待审核）</a><a href="../index.html" target="_blank">原 UI 设计索引</a></nav>
<section><h2>这一批优先检查</h2><ol><li>05/08/09/27/28/30/33/34/35/37/40/47/48/55：面板内控件、人物和列表不被裁断；长列表能滚到底，数字键盘十二键可用。</li><li>25 掉星显示失败姿势；33/34 桃花角色、35 春衣试穿与文字一致；43 未完成进度与已完成有区别。</li><li>51 按下、选中、禁用、焦点可辨；52 正面、两种牌背、选中、禁用、身份、特效各自正确；53 快捷语、表情、录音和静音不同；54 投票按钮与状态一致。</li><li>三角色五动作、六套道童服装五动作、12 FX：正常实速、肢体完整、胜负姿势保持服装；循环 FX 切页后消失。动画为静态独立姿势加整体关键帧变换。</li></ol></section>''']
counts=[]
for number,(first,last,title) in enumerate(batches,1):
    group=[p for p in screens if first<=int(p['id'][:2])<=last]
    n=sum(len(p['states']) for p in group);counts.append({'batch':number,'first':first,'last':last,'screens':len(group),'states':n})
    parts.append(f'<section id="batch-{number}"><h2>第 {number} 批：{escape(title)}</h2><p>{len(group)} 界面 / {n} 状态，均待用户审核。</p><table><tr><th>界面</th><th>当前候选状态</th></tr>')
    for p in group:
        parts.append('<tr><td>'+link(p,label=p['id'][:2]+' '+p['title'])+'<br><small>'+link(p,aspect='standard',label='16:9 基础界面')+'</small></td><td><div class="states">')
        for i,st in enumerate(p['states']):parts.append(link(p,i,label=f'{i} {st["name"]}')+' '+link(p,i,aspect='standard',label='16:9'))
        parts.append('</div></td></tr>')
    parts.append('</table></section>')
parts.append('<p>源游戏按用户提供的“QQ斗地主”记录；平台、准确版本及目标接入工程尚待锁定。历史《欢乐斗地主》网页记录仅作历史功能参考。</p><p><small>现有浏览器截图和录像在用户停止自动操作前获取，固定版本与来源哈希另存交接记录。后续修改未再自动操作浏览器，当前候选版请由用户审核。</small></p></main></html>')
(OUT/'index.html').write_text('\n'.join(parts),encoding='utf-8')
(OUT/'batches.json').write_text(json.dumps({'schemaVersion':1,'status':'pending_user_review','userApproval':False,'screens':len(screens),'states':sum(len(p['states']) for p in screens),'batches':counts},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'entry':'preview/review-20261111/index.html','screens':len(screens),'states':sum(len(p['states']) for p in screens)},ensure_ascii=False))
