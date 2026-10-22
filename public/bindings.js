// One chromatic octave on a familiar virtual-piano home-row layout.
// Physical QWERTY locations; input/composition controls are excluded.
const white = [
  ['A',60,'1','C4'],['S',62,'2','D4'],['D',64,'3','E4'],['F',65,'4','F4'],
  ['G',67,'5','G4'],['H',69,'6','A4'],['J',71,'7','B4'],['K',72,'1̇','C5'],
];
const black = [['W',61,'♯1','C♯4',1],['E',63,'♯2','D♯4',2],['T',66,'♯4','F♯4',4],['Y',68,'♯5','G♯4',5],['U',70,'♭7','B♭4',6]];
export const MELODY = [...white.map(v=>[...v,0]),...black].map(([key,midi,label,sub,position])=>({
  code:'Key'+key,key,midi,label,sub,position,black:position>0,kind:'note',id:sub,
  frequency:440*2**((midi-69)/12),paw:midi<66?'left':'right',
}));
export const DRUMS = [
  ['Z','kick','底鼓','KICK','left'],['X','snare','军鼓','SNARE','right'],
  ['C','closed-hat','闭镲','CLOSED HAT','left'],['V','open-hat','开镲','OPEN HAT','right'],
  ['B','tom-low','低通鼓','LOW TOM','left'],['N','tom-high','高通鼓','HIGH TOM','right'],
  ['M','crash','碎音镲','CRASH','left'],['L','ride','叮叮镲','RIDE','right'],
].map(([key,voice,label,sub,paw])=>({code:'Key'+key,key,voice,label,sub,paw,kind:'drum',id:voice}));

// Compact six-note voicings, not physical guitar fingering diagrams. The Am/C
// and G/D inversions keep every voice inside the licensed C3-C5 sample range.
export const CHORDS = [
  ['1','C',[48,52,55,60,64,67],'C'],
  ['2','Am',[48,52,57,60,64,69],'Am/C'],
  ['3','F',[53,57,60,65,69,72],'F'],
  ['4','G',[50,55,59,62,67,71],'G/D'],
].map(([key,label,notes,voicing])=>({code:'Digit'+key,key,label,sub:voicing,voicing,notes:Object.freeze(notes),kind:'chord',id:label,paw:'right'}));

// Keep the original 17 key objects available to the legacy synth playback path:
// v1 C/V events were shaker/bongo, never closed/open hi-hat.
export const LEGACY_KEYS=[...MELODY,...DRUMS.slice(0,4).map(key=>{
  if(key.code==='KeyC')return {...key,voice:'shaker',id:'shaker',label:'沙铃',sub:'SHAKER'};
  if(key.code==='KeyV')return {...key,voice:'bongoHigh',id:'bongoHigh',label:'邦戈',sub:'BONGO'};
  return {...key};
})];
export const KEYS=[...MELODY,...DRUMS,...CHORDS];
