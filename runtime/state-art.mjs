// Native state visuals over independent generated skins. No server calls or gameplay adjudication.
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function renderStateArt(v,{index:I,url,actorId='daotong',skinId='daotong_base'}){
 const img=(f,cl='')=>f?`<img class="${cl}" src="${url(f)}" alt="">`:'';
 const buttons=v.actions.map(a=>`<button class="artbutton ${/取消|返回|关闭|不出/.test(a.label)?'secondary':''}" data-stateaction="${esc(a.label)}" ${a.disabled?'disabled aria-disabled="true"':''}>${esc(a.label)}</button>`).join('');
 const text=`<h2>${esc(v.title)}</h2><div class="state-copy">${esc(v.body)}</div>`;
 const reason=v.disabledReasons.length?`<div class="state-disabled-reason">${esc(v.disabledReasons.join('；'))}</div>`:'';
 const icon=img(I.icons[v.icon],'state-icon');let content='';
 const costume=I.costumes.find(c=>c.id===skinId),actor=I.actors[actorId]||I.actors.daotong;
 switch(v.layout){
 case 'inline':case 'badge':content=`<div class="state-inline">${icon}<div>${text}${reason}</div><div class="state-actions">${buttons}</div></div>`;break;
 case 'table':content=`<div class="state-table-note">${text}${reason}<div class="state-actions">${buttons}</div></div>`;break;
 case 'loading':content=`<div class="state-focus">${img(I.icons.refresh,'state-icon state-spin')}${text}<div class="progress-track"><i></i></div><div class="state-actions">${buttons}</div></div>`;break;
 case 'seats':content=`<div class="state-focus state-wide">${text}<div class="state-seat-row">${['daotong','taohua','hulu'].map((a,i)=>`<div class="state-seat">${img(I.actors[a].expressions.smile)}<b>${esc(I.actors[a].name)}</b><span>${v.name==='空座'&&i>0?'等待入座':esc(v.name)}</span></div>`).join('')}</div><div class="state-actions">${buttons}</div></div>`;break;
 case 'result':{const loss=/负|失败|淘汰/.test(v.name),pose=loss?'lose':'win';content=`<div class="state-result">${img(costume?.poses?.[pose]||actor[pose],'state-result-actor')}<section>${icon}${text}${reason}<div class="state-actions">${buttons}</div></section></div>`;break;}
 case 'empty':content=`<div class="state-focus">${icon}${text}<div class="state-actions">${buttons}</div></div>`;break;
 case 'reward':content=`<div class="state-focus">${text}<div class="state-rewards">${['coin','token','gift'].map(k=>`<div>${img(I.icons[k])}</div>`).join('')}</div>${reason}<div class="state-actions">${buttons}</div></div>`;break;
 case 'resource':content=`<div class="state-focus">${text}<div class="state-rewards"><div>${img(I.icons.coin)}<b>铜钱</b></div><div>${img(I.icons.token)}<b>玉牌</b></div></div>${reason}<div class="state-actions">${buttons}</div></div>`;break;
 case 'locked':content=`<div class="state-focus">${img(I.icons.lock,'state-icon')}${text}${reason}<div class="state-actions">${buttons}</div></div>`;break;
 case 'progress':content=`<div class="state-focus">${text}<div class="state-stars">★　★　★</div><div class="progress-track"><i style="width:${/未达/.test(v.name)?'32':'100'}%"></i></div>${reason}<div class="state-actions">${buttons}</div></div>`;break;
 case 'settings':content=`<div class="state-focus state-wide">${text}<div class="state-native-fields"><label>音乐<input type="range" aria-label="音乐音量" min="0" max="100" value="60"></label><label>音效<input type="range" aria-label="音效音量" min="0" max="100" value="80"></label><label><input type="checkbox" checked> 震动提示</label></div><div class="state-actions">${buttons}</div></div>`;break;
 case 'login':content=`<div class="state-focus">${text}<label class="state-consent"><input type="checkbox" data-state-consent> 已阅读并同意用户协议与隐私政策</label>${reason}<div class="state-actions">${buttons.replace(/<button /g,'<button data-login-button disabled ')}</div></div>`;break;
 case 'form':content=`<div class="state-focus state-wide">${text}<div class="state-native-fields">${v.screen==='08-join-room'?'<label>房号<input inputmode="numeric" maxlength="6" aria-label="六位房号" placeholder="输入六位房号"></label>':v.screen==='49-support-notices'?'<label>反馈内容<textarea maxlength="500" aria-label="反馈内容"></textarea></label>':'<label>昵称<input maxlength="12" aria-label="昵称" placeholder="输入昵称"></label>'}</div><div class="state-actions">${buttons}</div></div>`;break;
 case 'cards':content=`<div class="state-focus state-wide">${text}<div class="state-card-row">${['spades-A','hearts-K','diamonds-3'].map(k=>img(/牌背/.test(v.name)?'assets/ui/cards-source/back-jade.png':I.cards[k],/选中/.test(v.name)?'state-card-selected':'')).join('')}</div>${reason}<div class="state-actions">${buttons}</div></div>`;break;
 case 'components':content=`<div class="state-focus state-wide">${text}<div class="state-actions"><button class="artbutton" ${v.name==='禁用'?'disabled':''}>主要操作</button><button class="artbutton secondary">次要操作</button><input aria-label="输入框焦点状态" placeholder="输入内容" ${v.name==='焦点'?'autofocus':''}></div>${reason}<div class="state-actions">${buttons}</div></div>`;break;
 case 'costume':case 'selection':content=`<div class="state-focus state-wide state-selection">${img(costume?.file||actor.master,'state-selection-actor')}<section>${text}${reason}<div class="state-actions">${buttons}</div></section></div>`;break;
 case 'voice':content=`<div class="state-focus">${img(I.icons[v.name==='静音'?'mute':'voice'],'state-icon')}${text}<div class="state-voice-bars">▂ ▆ ▃ █ ▅ ▂ ▇ ▃</div><div class="state-actions">${buttons}</div></div>`;break;
 case 'chat':content=`<div class="state-focus state-wide">${text}<div class="state-rewards">${['smile','laugh','surprise'].map(e=>img(actor.expressions[e])).join('')}</div><div class="state-actions">${buttons}</div></div>`;break;
 case 'list':case 'mail':case 'profile':content=`<div class="state-focus state-wide">${text}<div class="state-actions">${buttons}</div>${reason}</div>`;break;
 case 'rules':content=`<div class="state-focus state-wide state-rules">${text}<div class="state-actions">${buttons}</div></div>`;break;
 case 'confirm':case 'error':content=`<div class="state-focus">${icon}${text}${reason}<div class="state-actions">${buttons}</div></div>`;break;
 default:throw new Error('Missing state art layout '+v.layout);
 }
 return `<div class="state-art state-art-${v.layout}" data-state-art="${esc(v.id)}" role="${['inline','badge','table'].includes(v.layout)?'status':'dialog'}" aria-label="${esc(v.title)}">${content}<button class="state-dismiss" data-stateaction="关闭" aria-label="关闭状态预览">×</button></div>`;
}
