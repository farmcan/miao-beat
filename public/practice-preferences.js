// Fixed, non-sensitive choices only. Invalid/obsolete values fall back safely.
export function normalizePracticePreferences(data,songs){
  if(!data||data.version!==1||!Array.isArray(songs)||!songs.length)return null;
  const instrument=['piano','marimba','guitar','drums'].includes(data.instrument)?data.instrument:'piano';
  const compatible=songs.filter(s=>s.instruments.includes(instrument));
  const song=compatible.find(s=>s.id===data.song)||compatible[0];if(!song)return null;
  const index=typeof data.phrase==='string'&&/^\d+$/.test(data.phrase)?Number(data.phrase):-1;
  return {version:1,instrument,song:song.id,bpm:Number.isInteger(data.bpm)&&data.bpm>=50&&data.bpm<=180?data.bpm:song.bpm,
    meter:[2,3,4].includes(data.meter)?data.meter:song.meter,phrase:index>=0&&index<song.phrases.length?String(index):'all',
    loop:data.loop===true,layout:['original','portrait','square'].includes(data.layout)?data.layout:'original'};
}
