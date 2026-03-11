(()=>{
  const lanesEl=document.getElementById('lanes');
  const scoreEl=document.getElementById('score');
  const comboEl=document.getElementById('combo');
  const maxComboEl=document.getElementById('maxCombo');
  const judgeEl=document.getElementById('judge');
  const startBtn=document.getElementById('start');
  const autoBtn=document.getElementById('auto');
  const songSel=document.getElementById('song');
  const keyEls=[...document.querySelectorAll('.keys div')];

  const KEYS=['d','f','j','k'];
  const SPAWN_Y=-24;
  const HIT_Y=630;
  const SPEED=320; // px/s
  const WINDOW={perfect:20, great:42, good:70};

  let notes=[];
  let score=0,combo=0,maxCombo=0;
  let started=false,last=0,auto=false,songStart=0;
  let bgm=null;
  const laneEls=[];

  for(let i=0;i<4;i++){
    const lane=document.createElement('div');
    lane.className='lane';
    lane.dataset.i=i;
    lane.addEventListener('pointerdown',()=>hitLane(i));
    lanesEl.appendChild(lane);
    laneEls.push(lane);
  }

  function loadChart(kind='default'){
    const arr=[];
    if(kind==='fast'){
      let t=0.7; const p=[0,1,2,3,2,1,0,3];
      for(let i=0;i<140;i++){const lane=p[i%p.length];arr.push({lane,time:t,hit:false,el:null}); if(i%6===0)arr.push({lane:(lane+2)%4,time:t+0.1,hit:false,el:null}); t+=0.24;}
      return arr;
    }
    if(kind==='swing'){
      let t=0.8; const p=[0,2,1,3,0,1,2,3];
      for(let i=0;i<110;i++){const lane=p[i%p.length];arr.push({lane,time:t,hit:false,el:null}); t += (i%2?0.42:0.28);} 
      return arr;
    }
    let t=0.8; const p=[0,1,2,3,1,2,0,3,0,2,1,3,1,0,2,3];
    for(let i=0;i<96;i++){const lane=p[i%p.length];arr.push({lane,time:t,hit:false,el:null}); if(i%8===7)arr.push({lane:(lane+1)%4,time:t+0.15,hit:false,el:null}); t+=0.35;}
    return arr;
  }

  function reset(){
    lanesEl.querySelectorAll('.note').forEach(n=>n.remove());
    notes=loadChart(songSel.value);
    score=0;combo=0;maxCombo=0;
    started=true;
    songStart=performance.now()/1000;
    judge('-');
    syncUI();
    startBgm();
  }

  function startBgm(){
    if(bgm){ bgm.pause(); bgm=null; }
    // 你可替换成自己的邦多利授权音乐
    // const url='./source/your-song.mp3';
    const url='';
    if(!url) return;
    bgm=new Audio(url); bgm.currentTime=0; bgm.volume=0.5; bgm.play().catch(()=>{});
  }

  function time(){ return performance.now()/1000 - songStart; }
  function laneX(i){ return lanesEl.clientWidth*(i+0.5)/4; }

  function spawn(note){
    const el=document.createElement('div');
    el.className=`note l${note.lane}`;
    el.style.top=SPAWN_Y+'px';
    laneEls[note.lane].appendChild(el);
    note.el=el;
  }

  function syncUI(){
    scoreEl.textContent=score;
    comboEl.textContent=combo;
    maxComboEl.textContent=maxCombo;
  }

  function judge(text){ judgeEl.textContent=text; }

  function doJudge(delta){
    const a=Math.abs(delta);
    if(a<=WINDOW.perfect){ score+=1000+combo*2; combo++; judge('Perfect'); }
    else if(a<=WINDOW.great){ score+=650+combo; combo++; judge('Great'); }
    else if(a<=WINDOW.good){ score+=300; combo=0; judge('Good'); }
    else { combo=0; judge('Miss'); }
    maxCombo=Math.max(maxCombo,combo);
    syncUI();
  }

  function hitLane(lane){
    if(!started) return;
    flashKey(lane);
    const now=time();
    const cand=notes.filter(n=>!n.hit&&n.lane===lane);
    if(!cand.length) return;
    cand.sort((a,b)=>Math.abs(a.time-now)-Math.abs(b.time-now));
    const n=cand[0];
    const d=n.time-now;
    if(Math.abs(d)<=WINDOW.good){
      n.hit=true;
      n.el&&n.el.remove();
      doJudge(d);
    }
  }

  function flashKey(i){
    const el=keyEls[i];
    el.classList.add('active');
    setTimeout(()=>el.classList.remove('active'),90);
  }

  function update(ts){
    if(!started){ requestAnimationFrame(update); return; }
    const now=time();

    for(const n of notes){
      if(n.hit) continue;
      const spawnAt=n.time-(HIT_Y-SPAWN_Y)/SPEED;
      if(!n.el && now>=spawnAt) spawn(n);
      if(n.el){
        const y=HIT_Y-(n.time-now)*SPEED;
        n.el.style.top=y+'px';
        if(y>HIT_Y+WINDOW.good+40){
          n.hit=true;
          n.el.remove();
          combo=0; judge('Miss'); syncUI();
        }
      }
    }

    if(auto){
      for(const n of notes){
        if(!n.hit && Math.abs(n.time-now)<=0.01){
          n.hit=true; n.el&&n.el.remove();
          score+=800; combo++; maxCombo=Math.max(maxCombo,combo); judge('AUTO'); syncUI();
        }
      }
    }

    if(notes.every(n=>n.hit)){
      started=false;
      judge('结束');
    }

    requestAnimationFrame(update);
  }

  window.addEventListener('keydown',e=>{
    const k=e.key.toLowerCase();
    const i=KEYS.indexOf(k);
    if(i>=0){ e.preventDefault(); hitLane(i); }
  });

  startBtn.onclick=reset;
  autoBtn.onclick=()=>{ auto=!auto; autoBtn.textContent='自动演奏: '+(auto?'开':'关'); };

  requestAnimationFrame(update);
})();