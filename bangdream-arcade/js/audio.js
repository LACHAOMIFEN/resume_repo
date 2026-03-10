window.BDAudio = (() => {
  let ctx=null, started=false, timer=null, step=0, bgmAudio=null;
  const ensure=()=>{ if(!ctx) ctx=new (window.AudioContext||window.webkitAudioContext)(); };
  const beep=(f,l=.1,t='square',v=.02,w=0)=>{ try{ensure();const tt=ctx.currentTime+w;const o=ctx.createOscillator(),g=ctx.createGain();o.type=t;o.frequency.value=f;o.connect(g);g.connect(ctx.destination);g.gain.setValueAtTime(.0001,tt);g.gain.exponentialRampToValueAtTime(v,tt+.01);g.gain.exponentialRampToValueAtTime(.0001,tt+l);o.start(tt);o.stop(tt+l+.01);}catch(e){} };
  const startBgm=(url='')=>{
    if(started) return; started=true;
    if(url){ try{ bgmAudio=new Audio(url); bgmAudio.loop=true; bgmAudio.volume=.45; bgmAudio.play().catch(()=>{}); return; }catch(e){} }
    const melody=[523,659,784,659,587,659,494,392], bass=[131,131,147,131,98,98,110,98];
    timer=setInterval(()=>{const i=step%melody.length;beep(melody[i],.11,'square',.022);beep(bass[i],.16,'triangle',.014,.01);step++;},180);
  };
  const playItem=(url)=>{ if(!url) return; try{const a=new Audio(url); a.volume=.8; a.play().catch(()=>{});}catch(e){} };
  const playYukina=()=>{ [659,784,1047].forEach((f,i)=>beep(f,.24,'sawtooth',.12,i*.08)); };
  const playVoice=(url)=>{ if(!url) return; try{const a=new Audio(url);a.volume=.75;a.play().catch(()=>{});}catch(e){} };
  return { startBgm, playItem, playYukina, playVoice };
})();