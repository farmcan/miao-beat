import test from 'node:test';import assert from 'node:assert/strict';
import {normalizePracticePreferences as normalize} from '../public/practice-preferences.js';import {SONGS} from '../public/scores.js';
test('stored preferences keep bounded compatible choices and reject executable/free text fields',()=>{
 const data=normalize({version:1,instrument:'drums',song:'five-hundred-miles',phrase:'999',bpm:Infinity,meter:9,loop:'true',layout:'evil',title:'secret',events:[]},SONGS);
 assert.equal(data.song,'drum-first-bar');assert.equal(data.phrase,'all');assert.equal(data.bpm,80);assert.equal(data.meter,4);assert.equal(data.loop,false);assert.equal(data.layout,'original');assert.equal('title' in data,false);assert.equal('events' in data,false);assert.equal(normalize({version:99},SONGS),null);
});
