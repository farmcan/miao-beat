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
  ['C','shaker','沙铃','SHAKER','left'],['V','bongoHigh','邦戈','BONGO','right'],
].map(([key,voice,label,sub,paw])=>({code:'Key'+key,key,voice,label,sub,paw,kind:'drum',id:voice}));
export const KEYS=[...MELODY,...DRUMS];
