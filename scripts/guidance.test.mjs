import test from 'node:test';
import assert from 'node:assert/strict';
import {guidePosition} from '../public/guidance.js';
import {BeatClock} from '../public/clock.js';
test('uneven note lengths, count-in and skipped frames resolve directly from the audio-clock position',()=>{
 const events=[{offset:0},{offset:.375},{offset:.5},{offset:1.5}];
 assert.equal(guidePosition(events,-.9,2,120,3).countIn,2);
 assert.deepEqual([guidePosition(events,.4,2,120,3).index,guidePosition(events,.4,2,120,3).next],[1,2]);
 const jumped=guidePosition(events,1.8,2,120,3);assert.equal(jumped.index,3);assert.equal(jumped.next,-1);assert.equal(jumped.bar,2);assert.equal(jumped.beat,0);assert.equal(jumped.progress,.9);
 assert.equal(guidePosition(events,5,2,120,3).progress,1);
});
test('resuming a guided metronome catches the shared origin and keeps bar phase after a long stall',t=>{
 const calls=[],context={currentTime:10.1};const clock=new BeatClock({context},()=>{});
 t.after(()=>clock.stop());clock.click=(time,accent)=>calls.push({time,accent});
 clock.start(120,3,.1); // origin is in the past: beat20, third beat of the bar
 assert.equal(clock.history.at(-1).time,10.1);assert.equal(clock.history.at(-1).beat,2);
 context.currentTime=13.2;clock.schedule();assert.equal(clock.next,13.6);assert.equal(clock.history.at(-1).time,10.1); // outside lookahead, no event yet
 clock.stop();
});


test('fractional phrase pickup crosses beat and bar boundaries at the right time',()=>{
 const events=[{offset:0},{offset:1}],bpm=120,meter=4;
 assert.equal(guidePosition(events,0,2,bpm,meter,1.5).beat,1);
 assert.equal(guidePosition(events,.25,2,bpm,meter,1.5).beat,2);
 assert.equal(guidePosition(events,1.25,2,bpm,meter,1.5).beat,0);
 assert.equal(guidePosition(events,1.25,2,bpm,meter,1.5).bar,2);
});
