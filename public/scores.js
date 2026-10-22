// Independent single-line reference transcription. No copied accompaniment,
// lyrics, MIDI files, or recordings. Provenance: docs/research/scores.md.
const phrase=(notes,beats)=>notes.map((note,i)=>({note,beats:beats?.[i]??(i===notes.length-1?2:1)}));
export const SONGS=[
  {id:'twinkle',name:'小星星',meter:4,bpm:96,key:'C 大调',description:'一行是一句。数字是简谱，字母是键盘；可以先弹一句，再自己接下一句。',
    phrases:[phrase(['C4','C4','G4','G4','A4','A4','G4']),phrase(['F4','F4','E4','E4','D4','D4','C4']),
      phrase(['G4','G4','F4','F4','E4','E4','D4']),phrase(['G4','G4','F4','F4','E4','E4','D4']),
      phrase(['C4','C4','G4','G4','A4','A4','G4']),phrase(['F4','F4','E4','E4','D4','D4','C4'])]},
  {id:'birthday',name:'生日快乐',meter:3,bpm:104,key:'F 大调',description:'U 是降 Si（♭7），K 是高音 Do。开头两音合一拍；这里只看参考，不催你也不判分。',
    phrases:[phrase(['C4','C4','D4','C4','F4','E4'],[.75,.25,1,1,1,2]),
      phrase(['C4','C4','D4','C4','G4','F4'],[.75,.25,1,1,1,2]),
      phrase(['C4','C4','C5','A4','F4','E4','D4'],[.75,.25,1,1,1,1,1]),
      phrase(['B♭4','B♭4','A4','F4','G4','F4'],[.75,.25,1,1,1,2])]},
  {id:'painter',name:'粉刷匠 · 开头',meter:4,bpm:108,key:'C 大调',description:'先用两小节开头找手感，再接上自己的节奏。本轮提供开头参考；没有歌词或原曲录音。',
    phrases:[phrase(['G4','E4','G4','E4','G4','E4','C4'])]},
];
export function scoreEvents(song,bpm){
  let time=0,index=0;return song.phrases.flatMap(row=>row.map(event=>{
    const out={...event,index:index++,offset:time};time+=event.beats*60/bpm;return out;
  }));
}
