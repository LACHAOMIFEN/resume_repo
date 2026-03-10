(()=>{
  const C=window.BD_CONFIG;
  const game=document.getElementById('game');
  const ui={
    score:document.getElementById('score'),
    hp:document.getElementById('hp'),
    stack:document.getElementById('stack'),
    buff:document.getElementById('buff'),
    yukina:document.getElementById('yukina'),
    diffText:document.getElementById('difficultyText'),
    best:document.getElementById('best'),
    menu:document.getElementById('menu')
  };
  const W=960,H=540;
  const sx=()=>game.clientWidth/W, sy=()=>game.clientHeight/H;
  const mk=(cls,html='')=>{const d=document.createElement('div');d.className='obj '+cls;d.innerHTML=html;game.appendChild(d);return d};
  const place=(el,x,y)=>{el.style.left=(x*sx())+'px';el.style.top=(y*sy())+'px'};
  const pick=a=>a[(Math.random()*a.length)|0];
  const hit=(a,b,ra,rb)=>{const dx=a.x-b.x,dy=a.y-b.y;return dx*dx+dy*dy<=(ra+rb)*(ra+rb)};
  const keys=new Set();
  let hold={l:false,r:false,u:false,d:false};
  const DIFF={
    normal:{name:'普通',enemySpawn:0.55,eliteCd:14,enemyBullet:180,eliteBullet:250,playerHp:5},
    hard:{name:'困难',enemySpawn:0.42,eliteCd:11,enemyBullet:220,eliteBullet:290,playerHp:4},
    hell:{name:'地狱',enemySpawn:0.32,eliteCd:8,enemyBullet:260,eliteBullet:340,playerHp:3}
  };
  const BEST_KEY='bd_arcade_best';
  let selectedDiff='normal';
  let g;
  let playing=false;

  function init(){
    game.innerHTML='';
    if(C.bgUrl){
      game.style.background=`linear-gradient(rgba(3,5,12,.86), rgba(3,5,12,.92)),url('${C.bgUrl}') center/cover no-repeat,#090d19`;
    }
    const p=mk('player',`<img src="${C.playerIcon}">`);
    const d=DIFF[selectedDiff];
    g={t:0,score:0,hp:d.playerHp,yukina:0,player:{x:W/2,y:H-70,el:p},en:[],bul:[],eb:[],drop:[],spawn:0,elite:6,shoot:0,buffs:[],shield:0,over:false};
    drawUI();
  }

  const active=()=>g.buffs.filter(b=>b.until>g.t);
  const count=(k)=>active().filter(b=>b.kind===k).length;
  const addBuff=(kind)=>{ if(g.buffs.length>=5) g.buffs.sort((a,b)=>a.until-b.until).shift(); g.buffs.push({kind,until:g.t+8}); };

  function addEnemy(){ const el=mk('enemy',`<img src="${pick(C.enemyIcons)}">`); g.en.push({x:40+Math.random()*(W-80),y:-28,vx:Math.random()*100-50,vy:85+Math.random()*55,hp:2,elite:false,el,fire:.8+Math.random()*1.2}); }
  function addElite(){ const el=mk('enemy elite',`<img src="${pick(C.enemyIcons)}">`); g.en.push({x:120+Math.random()*(W-240),y:66,vx:(Math.random()<.5?-1:1)*85,vy:0,hp:22,elite:true,el,fire:.45}); }
  function addDrop(x,y){ const kinds=['guitar','keyboard','drum','bass','violin']; const kind=pick(kinds); const icon={guitar:'🎸',keyboard:'🎹',drum:'🥁',bass:'🪕',violin:'🎻'}[kind]; const el=mk('drop',icon); g.drop.push({x,y,vy:90,kind,el}); }
  function addEB(x,y,vx,vy){ const el=mk('eb'); g.eb.push({x,y,vx,vy,el}); }

  function shoot(){
    const gtr=count('guitar'), key=count('keyboard'), vio=count('violin');
    const spread=Math.min(7,1+gtr*2), dmg=1+key, pierce=key>0?key+1:0, speed=500+key*60+(gtr?40:0);
    for(let i=0;i<spread;i++){
      const off=i-(spread-1)/2; const el=mk('bullet');
      el.style.background = key? '#8ff' : gtr? '#ffb7ff' : '#ffe46f';
      if(key){el.style.width='12px';el.style.height='20px';}
      g.bul.push({x:g.player.x+off*10,y:g.player.y-28,vx:off*48,vy:-speed,dmg,pierce,homing:vio>0,homingPower:18+vio*12,el});
    }
  }

  function castYukina(){
    if(g.yukina<100) return;
    g.yukina=0;
    g.eb=[];
    let killed=0;
    for(const e of g.en){ if(e.hp>0){e.hp=0;e.dead=true;killed++;} }
    g.score += 50 + killed*10;
    for(let i=0;i<10;i++){const fx=mk('skillfx','🌹');place(fx,60+Math.random()*(W-120),120+Math.random()*(H-220));setTimeout(()=>fx.remove(),700);}
    BDAudio.playYukina();
    BDAudio.playVoice(C.voiceUrl);
  }

  function step(dt){
    g.t+=dt;
    if(hold.l||keys.has('ArrowLeft')||keys.has('a')) g.player.x-=320*dt;
    if(hold.r||keys.has('ArrowRight')||keys.has('d')) g.player.x+=320*dt;
    if(hold.u||keys.has('ArrowUp')||keys.has('w')) g.player.y-=280*dt;
    if(hold.d||keys.has('ArrowDown')||keys.has('s')) g.player.y+=280*dt;
    g.player.x=Math.max(24,Math.min(W-24,g.player.x));
    g.player.y=Math.max(40,Math.min(H-24,g.player.y));

    const key=count('keyboard'), bas=count('bass');
    const enemySlow=Math.max(.45,1-bas*.12);
    const d=DIFF[selectedDiff];

    g.spawn-=dt; if(g.spawn<=0){ addEnemy(); g.spawn=d.enemySpawn; }
    g.elite-=dt; if(g.elite<=0 && !g.en.some(e=>e.elite&&!e.dead)){ addElite(); g.elite=d.eliteCd; }
    g.shoot-=dt; if(g.shoot<=0){ shoot(); g.shoot=Math.max(.08,.16-key*.015); }

    for(const e of g.en){
      if(e.elite){ e.x+=e.vx*dt*enemySlow; e.y=66+Math.sin(g.t*1.4)*8; if(e.x<70||e.x>W-70)e.vx*=-1; }
      else{ e.x+=e.vx*dt*enemySlow; e.y+=e.vy*dt*enemySlow; if(e.x<20||e.x>W-20)e.vx*=-1; }
      e.fire-=dt; if(e.fire<=0){ e.fire=e.elite?.7:1.2; const dx=g.player.x-e.x,dy=g.player.y-e.y,l=Math.hypot(dx,dy)||1; const sp=e.elite?d.eliteBullet:d.enemyBullet; addEB(e.x,e.y,dx/l*sp,dy/l*sp); if(e.elite){addEB(e.x-24,e.y+8,dx/l*sp*.9-40,dy/l*sp);addEB(e.x+24,e.y+8,dx/l*sp*.9+40,dy/l*sp);} }
    }

    for(const b of g.bul){ if(b.homing&&g.en.length){let t=null,m=1e9;for(const e of g.en){const d=(e.x-b.x)**2+(e.y-b.y)**2;if(d<m){m=d;t=e;}} if(t)b.vx+=Math.sign(t.x-b.x)*b.homingPower*dt;} b.x+=b.vx*dt; b.y+=b.vy*dt; }
    for(const b of g.eb){ b.x+=b.vx*dt*enemySlow; b.y+=b.vy*dt*enemySlow; }
    for(const d of g.drop){ d.y+=d.vy*dt; }

    for(const b of g.bul){
      for(const e of g.en){
        if(e.hp>0 && hit(b,e,7,16)){ e.hp-=b.dmg; if(b.pierce>0)b.pierce--; else b.dead=true;
          if(e.hp<=0){e.dead=true;g.score+=e.elite?80:10;g.yukina=Math.min(100,g.yukina+(e.elite?25:8)); if(e.elite){addDrop(e.x-20,e.y);addDrop(e.x+20,e.y+6);} else if(Math.random()<.25)addDrop(e.x,e.y);} }
      }
    }

    for(const b of g.eb){ if(hit(b,g.player,6,14)){ b.dead=true; if(g.shield>0)g.shield--; else g.hp--; if(g.hp<=0){g.over=true; onGameOver();} } }
    for(const d of g.drop){ if(hit(d,g.player,16,14)){ d.dead=true; addBuff(d.kind); if(d.kind==='drum')g.shield=Math.min(5,g.shield+3); if(d.kind==='violin')g.yukina=Math.min(100,g.yukina+22); BDAudio.playItem(C.itemSfx[d.kind]); } }

    g.en=g.en.filter(e=>!e.dead&&e.y<H+40); g.bul=g.bul.filter(b=>!b.dead&&b.y>-30); g.eb=g.eb.filter(b=>!b.dead&&b.y<H+30&&b.x>-30&&b.x<W+30); g.drop=g.drop.filter(d=>!d.dead&&d.y<H+30);

    for(const e of g.en) place(e.el,e.x,e.y);
    for(const b of g.bul) place(b.el,b.x,b.y);
    for(const b of g.eb) place(b.el,b.x,b.y);
    for(const d of g.drop) place(d.el,d.x,d.y);
    place(g.player.el,g.player.x,g.player.y);

    [...game.children].forEach(el=>{const live=[...g.en,...g.bul,...g.eb,...g.drop,g.player].some(o=>o.el===el); if(!live)el.remove();});
    drawUI();
  }

  function getBest(){ return Number(localStorage.getItem(BEST_KEY)||0); }
  function setBest(v){ localStorage.setItem(BEST_KEY,String(v)); }

  function drawUI(){
    const ab=active();
    ui.score.textContent=g.score; ui.hp.textContent=g.hp; ui.stack.textContent=`${ab.length}/5`;
    ui.buff.textContent=(ab.length?Math.max(...ab.map(b=>b.until-g.t)):0).toFixed(1)+'s';
    ui.yukina.textContent=Math.floor(g.yukina)+'%';
    ui.diffText.textContent=DIFF[selectedDiff].name;
    ui.best.textContent=getBest();
  }

  function onGameOver(){
    playing=false;
    if(g.score>getBest()) setBest(g.score);
    drawUI();
    setTimeout(()=>{ ui.menu.classList.remove('hidden'); }, 300);
  }

  let last=performance.now();
  function loop(n){ const dt=Math.min(.033,(n-last)/1000); last=n; if(playing && g && !g.over) step(dt); requestAnimationFrame(loop); }

  const bindHold=(id,key)=>{ const el=document.getElementById(id); el.onpointerdown=()=>{BDAudio.startBgm(C.bgmUrl); hold[key]=true;}; el.onpointerup=()=>hold[key]=false; el.onclick=()=>{BDAudio.startBgm(C.bgmUrl); if(!g)return; if(key==='l')g.player.x-=80; if(key==='r')g.player.x+=80; if(key==='u')g.player.y-=60; if(key==='d')g.player.y+=60; }; };
  bindHold('left','l'); bindHold('right','r'); bindHold('up','u'); bindHold('down','d');
  document.getElementById('fire').onclick=()=>BDAudio.startBgm(C.bgmUrl);
  document.getElementById('yukinaBtn').onclick=()=>{ if(g) castYukina(); };
  document.getElementById('restart').onclick=()=>{ init(); playing=true; ui.menu.classList.add('hidden'); };

  document.querySelectorAll('[data-diff]').forEach(btn=>{
    btn.onclick=()=>{
      selectedDiff=btn.dataset.diff;
      document.querySelectorAll('[data-diff]').forEach(x=>x.classList.remove('active'));
      btn.classList.add('active');
      if(g) drawUI();
    };
  });
  document.querySelector('[data-diff="normal"]').classList.add('active');
  document.getElementById('startBtn').onclick=()=>{ init(); playing=true; ui.menu.classList.add('hidden'); BDAudio.startBgm(C.bgmUrl); };

  window.addEventListener('keydown',e=>{BDAudio.startBgm(C.bgmUrl); keys.add(e.key); if(e.key==='k'||e.key==='K'){ if(g) castYukina(); }});
  window.addEventListener('keyup',e=>keys.delete(e.key));
  window.addEventListener('pointerup',()=>hold={l:false,r:false,u:false,d:false});

  init();
  drawUI();
  requestAnimationFrame(loop);
})();