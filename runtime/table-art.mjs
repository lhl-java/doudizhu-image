const hand = [
  'spades-2', 'hearts-A', 'spades-A', 'hearts-K', 'spades-K', 'hearts-Q',
  'clubs-Q', 'clubs-J', 'hearts-10', 'spades-9', 'hearts-9', 'clubs-8',
  'spades-7', 'hearts-7', 'diamonds-7', 'clubs-6', 'spades-5',
  'hearts-4', 'clubs-4', 'diamonds-3',
];
const originalHand = hand.filter(card => !['spades-A', 'hearts-K', 'diamonds-3'].includes(card));
const bottom = ['spades-A', 'hearts-K', 'diamonds-3'];
const puzzle = ['spades-A', 'hearts-A', 'spades-K', 'hearts-K', 'diamonds-9', 'clubs-8', 'spades-7', 'hearts-6'];
const tablePhases = {
  '11-deal-bid': { label: '叫地主', detail: '底牌未公开', waiting: true },
  '12-rob-landlord': { label: '抢地主', detail: '等待确认地主', waiting: true },
  '13-double': { label: '明牌与加倍', detail: '底分 100　倍数 ×2' },
  '14-play-turn': { label: '轮到你出牌', detail: '底分 100　倍数 ×4', interactive: true },
  '15-follow-pass': { label: '跟牌或不出', detail: '底分 100　倍数 ×4', interactive: true, previous: ['clubs-10', 'spades-10'] },
  '16-trustee': { label: '托管中', detail: '系统代为出牌' },
  '17-reconnect': { label: '正在重连', detail: '本局座位保留' },
  '22-replay-history': { label: '回放 · 第 4 手', detail: '底分 100　倍数 ×4', previous: ['clubs-10', 'spades-10'] },
  '31-puzzle-play': { label: '残局挑战', detail: '练习关 · 击败两位牌友', interactive: true, puzzle: true },
};
const ordinary = { label: '经典牌局', detail: '底分 100　倍数 ×4' };
const labels = { spades: '黑桃', hearts: '红桃', clubs: '梅花', diamonds: '方块' };
const cardLabel = id => {
  const [suit, rank] = id.split('-');
  return labels[suit] + rank;
};

export function renderTableArt(page, { I, actorId, tableSkin, art, actorImg, button, escape }) {
  const phase = tablePhases[page.id] || ordinary;
  const cards = phase.waiting ? originalHand : phase.puzzle ? puzzle : hand;
  const opponents = Object.keys(I.actors).filter(id => id !== actorId);
  const cardsSource = 'assets/ui/cards-source/';
  const peach = tableSkin === 'peach';
  const back = cardsSource + (peach ? 'back-ivory.png' : 'back-jade.png');
  const role = name => phase.waiting ? '' : art(cardsSource + name + '.png',
    'class="seat-role" alt="' + (name === 'landlord' ? '地主' : '农民') + '"');
  const seat = (id, side, count) => actorImg(id, 'master', 'table-player ' + side)
    + '<div class="table-name ' + side + '">'
    + art(I.actors[id].expressions.smile, 'class="seat-avatar" alt=""')
    + '<span>' + escape(I.actors[id].name) + '<small>' + count + ' 张</small></span>'
    + role('farmer') + '</div>';
  const reserve = phase.puzzle ? '' : '<div class="bottom-cards" aria-label="底牌">'
    + bottom.map(key => phase.waiting ? art(back, 'alt="未公开底牌"')
      : art(I.cards[key], 'alt="' + cardLabel(key) + '"')).join('') + '</div>';
  const previous = phase.previous ? '<div class="played-cards" aria-label="上手出牌">'
    + phase.previous.map(key => art(I.cards[key], 'alt="' + cardLabel(key) + '"')).join('') + '</div>' : '';
  const handCards = cards.map((key, i) => {
    const face = art(I.cards[key], 'alt="' + cardLabel(key) + '"');
    const pos = 'style="--position:' + i / (cards.length - 1) + '"';
    return phase.interactive
      ? '<button type="button" class="card" data-card="' + i + '" aria-pressed="false" ' + pos + '>' + face + '</button>'
      : '<span class="card" ' + pos + '>' + face + '</span>';
  }).join('');
  const actions = page.actions.map((label, i) => button(label, i < page.actions.length - 1,
    'data-action="' + escape(label) + '"' + (label === '出牌' ? ' disabled' : ''))).join('');
  return art(I.tables[tableSkin] || I.tables.jade, 'class="table-layer" alt="' + (peach ? '桃花牌桌' : '玉绿牌桌') + '"')
    + seat(opponents[0], 'left', phase.puzzle ? 6 : 17)
    + seat(opponents[1], 'right', phase.puzzle ? 5 : 17)
    + actorImg(actorId, 'master', 'self')
    + '<div class="bottom-name">' + role('landlord') + '<span>' + escape(I.actors[actorId].name)
    + '<small><span id="handCount">' + cards.length + '</span> 张</small></span></div>'
    + reserve + previous
    + '<div class="table-phase"><strong>' + phase.label + '</strong><small>' + phase.detail + '</small></div>'
    + (phase.interactive && !phase.puzzle ? '<span class="table-clock" aria-label="示例倒计时 18 秒">18</span>' : '')
    + (phase.interactive ? '<div class="table-selection" id="tableSelection" aria-live="polite">已选 0 张</div>' : '')
    + '<div class="table-actions">' + actions + '</div>'
    + '<div class="hand' + (phase.puzzle ? ' short-hand' : '') + '">' + handCards + '</div>';
}
