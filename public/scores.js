// Independent single-line reference transcription. No copied accompaniment,
// MIDI files or recordings. Miles lyrics were supplied by the user. Provenance: docs/research/scores.md
// and docs/research/scores-v2-2026-10-22.md. One beat = one quarter note.
const phrase=(notes,beats)=>notes.map((note,i)=>({note,beats:beats?.[i]??(i===notes.length-1?2:1)}));
// A line is the synchronization unit; no syllable-by-syllable singing is claimed.
// Continuous verse pickups fill the previous standalone ending, keeping 4/4 phase.
function fullMiles(){
  const first=phrase(['F4','G4'],[1,1]),pickup=phrase(['C4','D4','F4'],[.5,1,1]);
  const opening=phrase(['A4','A4','G4','F4','A4'],[1.5,.5,1,1,2]);
  const second=phrase(['G4','F4','G4','A4','G4','F4','D4'],[1,1,1.5,.5,.5,1.5,2]);
  const closing=phrase(['D4','F4','G4','A4','G4','F4','C4','C4','D4','F4','A4'],[1,1,1.5,.5,.5,1.5,1.5,.5,1,1,5.5]);
  const repeatA=phrase(['C4','D4','F4','A4','A4','G4','F4','A4'],[.5,1,1,1.5,.5,1,1,2]);
  // Repeat words articulate the last held D twice; the phrase remains eight beats.
  const repeatB=[...second.slice(0,-1),...phrase(['D4','D4'],[1,1])];
  const lyrics=[
    "If you missed the train I'm on", "You will know that I am gone", "You can hear the whistle blow a hundred miles",
    "A hundred miles, a hundred miles", "A hundred miles, a hundred miles", "You can hear the whistle blow a hundred miles",
    "Lord, I'm one, Lord, I'm two", "Lord, I'm three, Lord, I'm four", "Lord, I'm five hundred miles away from home",
    "Away from home, away from home", "Away from home, away from home", "Lord, I'm five hundred miles away from home",
    "Not a shirt on my back", "Not a penny to my name", "Lord, I can't go back home this ole way",
    "This ole way, this ole way", "This ole way, this ole way", "Lord, I can't go back home this this ole way",
    "If you missed the train I'm on", "You will know that I am gone", "You can hear the whistle blow a hundred miles",
    "A hundred miles, a hundred miles", "A hundred miles, a hundred miles", "You can hear the whistle blow a hundred miles",
    "You can hear the whistle blow a hundred miles", "You can hear the whistle blow a hundred miles",
  ];
  const phrases=[];
  for(let verse=0;verse<4;verse++)phrases.push([...(verse?pickup:first),...opening],second,closing,repeatA,repeatB,closing);
  for(let reprise=0;reprise<2;reprise++)phrases.push([...pickup,...closing.slice(2)]);
  phrases[phrases.length-1]=[...phrases.at(-1),{rest:true,beats:2.5}];
  return {phrases,lyrics};
}
export const SONGS=[
  {id:'twinkle',name:'小星星',meter:4,bpm:96,key:'C 大调',sourceUrl:'https://imslp.org/wiki/Ah!_vous_dirai-je,_maman_(Traditional)',description:'一行是一句。数字是简谱，字母是键盘；可以先弹一句，再自己接下一句。',
    phrases:[phrase(['C4','C4','G4','G4','A4','A4','G4']),phrase(['F4','F4','E4','E4','D4','D4','C4']),
      phrase(['G4','G4','F4','F4','E4','E4','D4']),phrase(['G4','G4','F4','F4','E4','E4','D4']),
      phrase(['C4','C4','G4','G4','A4','A4','G4']),phrase(['F4','F4','E4','E4','D4','D4','C4'])]},
  {id:'birthday',name:'生日快乐',meter:3,bpm:104,pickupBeats:1,key:'F 大调',difficulty:'试试黑键',sourceUrl:'https://www.lightandmatter.com/music/strings/birthday.pdf',description:'U 是 B♭4，K 是 C5。开头两音合一拍；本曲是 F 大调，琴键上的固定数字不能当作本曲的首调简谱。',
    phrases:[phrase(['C4','C4','D4','C4','F4','E4'],[.75,.25,1,1,1,2]),
      phrase(['C4','C4','D4','C4','G4','F4'],[.75,.25,1,1,1,2]),
      phrase(['C4','C4','C5','A4','F4','E4','D4'],[.75,.25,1,1,1,1,1]),
      phrase(['B♭4','B♭4','A4','F4','G4','F4'],[.75,.25,1,1,1,2])]},
  {id:'painter',name:'粉刷匠',meter:2,bpm:108,key:'C 大调',sourceUrl:'https://hnwy-ecs-backup.oss-cn-beijing.aliyuncs.com/uploads/20190627/2732d7a19671431fbffeb610ee481a4c.pdf#page=125',description:'四句完整旋律。半拍一个音的地方轻快一点，最后空一拍收尾。',
    phrases:[phrase(['G4','E4','G4','E4','G4','E4','C4','D4','F4','E4','D4','G4'],[.5,.5,.5,.5,.5,.5,1,.5,.5,.5,.5,2]),
      phrase(['G4','E4','G4','E4','G4','E4','C4','D4','F4','E4','D4','C4'],[.5,.5,.5,.5,.5,.5,1,.5,.5,.5,.5,2]),
      phrase(['D4','D4','F4','F4','E4','C4','G4','D4','F4','E4','D4','G4'],[.5,.5,.5,.5,.5,.5,1,.5,.5,.5,.5,2]),
      [...phrase(['G4','E4','G4','E4','G4','E4','C4','D4','F4','E4','D4','C4'],[.5,.5,.5,.5,.5,.5,1,.5,.5,.5,.5,1]),{rest:true,beats:1}]]},
  {id:'five-hundred-miles',name:'500 Miles · 五键简化版',meter:4,bpm:80,pickupBeats:2,key:'F 大调',difficulty:'五键慢弹',sourceUrl:'https://www.tan8.com/yuepu-84439.html',sourceLabel:'参考钢琴谱',description:'只用 A、S、F、G、H 五个键。四段都在，最后一句唱三遍；歌词跟着谱子走。先从 F、G 开始。',...fullMiles()},
  {id:'mary-lamb',name:'玛丽小羊',meter:4,bpm:88,key:'C 大调',sourceUrl:'https://archive.org/details/carminayalensiac00garr',description:'只用 C、D、E、G 四个白键。八小节短旋律；长音留足拍子，不用赶着弹下一音。',
    phrases:[phrase(['E4','D4','C4','D4','E4','E4','E4'],[1,1,1,1,1,1,2]),
      phrase(['D4','D4','D4','E4','G4','G4'],[1,1,2,1,1,2]),
      phrase(['E4','D4','C4','D4','E4','E4','E4','E4'],[1,1,1,1,1,1,1,1]),
      phrase(['D4','D4','E4','D4','C4'],[1,1,1,1,4])]},
  {id:'ode-to-joy',name:'欢乐颂 · 主题',meter:4,bpm:88,key:'C 大调',difficulty:'试试半拍',sourceUrl:'https://imslp.org/wiki/Symphony_No.9,_Op.125_(Beethoven,_Ludwig_van)',description:'第九交响曲中的完整十六小节主题，移到 C 大调。第三行有半拍，先放慢听节拍，再自己接着弹。',
    phrases:[phrase(['E4','E4','F4','G4','G4','F4','E4','D4','C4','C4','D4','E4','E4','D4','D4'],[1,1,1,1,1,1,1,1,1,1,1,1,1.5,.5,2]),
      phrase(['E4','E4','F4','G4','G4','F4','E4','D4','C4','C4','D4','E4','D4','C4','C4'],[1,1,1,1,1,1,1,1,1,1,1,1,1.5,.5,2]),
      phrase(['D4','D4','E4','C4','D4','E4','F4','E4','C4','D4','E4','F4','E4','D4','C4','D4','G4'],[1,1,1,1,1,.5,.5,1,1,1,.5,.5,1,1,1,1,2]),
      phrase(['E4','E4','F4','G4','G4','F4','E4','D4','C4','C4','D4','E4','D4','C4','C4'],[1,1,1,1,1,1,1,1,1,1,1,1,1.5,.5,2])]},
  {id:'moonlight-folk',name:'月光下 · 法国童谣',meter:4,bpm:88,key:'F 大调',sourceUrl:'https://www.gutenberg.org/ebooks/42711',description:'Au clair de la lune 的一段完整曲调，不是德彪西的《月光》。移到 F 大调后仍只用白键；句末长音包含原谱的停顿时间。',
    phrases:[phrase(['F4','F4','F4','G4','A4','G4','F4','A4','G4','G4','F4'],[1,1,1,1,2,2,1,1,1,1,4]),
      phrase(['F4','F4','F4','G4','A4','G4','F4','A4','G4','G4','F4'],[1,1,1,1,2,2,1,1,1,1,4]),
      phrase(['G4','G4','G4','G4','D4','D4','G4','F4','E4','D4','C4'],[1,1,1,1,2,2,1,1,1,1,4]),
      phrase(['F4','F4','F4','G4','A4','G4','F4','A4','G4','G4','F4'],[1,1,1,1,2,2,1,1,1,1,4])]},
  {id:'frere-jacques',name:'两只老虎 · 单八度版',meter:4,bpm:88,key:'C 大调',difficulty:'试试半拍',sourceUrl:'https://www.gutenberg.org/ebooks/42711',description:'Frère Jacques 的完整八小节单线改编。末句的低音 G 升了八度，适配这排琴键；第三行两个音占一拍。',
    phrases:[phrase(['C4','D4','E4','C4','C4','D4','E4','C4'],[1,1,1,1,1,1,1,1]),
      phrase(['E4','F4','G4','E4','F4','G4'],[1,1,2,1,1,2]),
      phrase(['G4','A4','G4','F4','E4','C4','G4','A4','G4','F4','E4','C4'],[.5,.5,.5,.5,1,1,.5,.5,.5,.5,1,1]),
      phrase(['C4','G4','C4','C4','G4','C4'],[1,1,2,1,1,2])]},
  {id:'drum-first-bar',name:'底鼓和军鼓 · 四拍',kind:'rhythm',instruments:['drums'],meter:4,bpm:80,key:'鼓组',description:'原创一小节：底鼓、军鼓轮流来。每次一拍，先找到稳稳走路的感觉。',
    phrases:[[{code:'KeyZ',beats:1},{code:'KeyX',beats:1},{code:'KeyZ',beats:1},{code:'KeyX',beats:1}]]},
  {id:'drum-hat-pulse',name:'加上踩镲 · 八拍',kind:'rhythm',instruments:['drums'],meter:4,bpm:88,key:'鼓组',difficulty:'试试双手',description:'原创两小节：踩镲每拍响，底鼓和军鼓轮流加入。加号表示两只一起敲。',
    phrases:[[{codes:['KeyZ','KeyC'],beats:1},{codes:['KeyX','KeyC'],beats:1},{codes:['KeyZ','KeyC'],beats:1},{codes:['KeyX','KeyC'],beats:1}],
      [{codes:['KeyZ','KeyC'],beats:1},{codes:['KeyX','KeyC'],beats:1},{codes:['KeyZ','KeyC'],beats:1},{codes:['KeyX','KeyC'],beats:1}]]},
].map(song=>{
  const totalBeats=song.phrases.flat().reduce((total,event)=>total+event.beats,0);
  return {kind:'melody',difficulty:'入门',instruments:['piano','marimba','guitar'],...song,totalBeats,durationSeconds:totalBeats*60/song.bpm};
});
export function scoreEvents(song,bpm){
  let time=0,index=0;return song.phrases.flatMap((row,lyricIndex)=>row.map(event=>{
    const out={...event,...(song.lyrics?{lyricIndex}:{}),index:index++,offset:time};time+=event.beats*60/bpm;return out;
  }));
}
