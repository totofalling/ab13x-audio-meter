class Ab13xAudioMeter extends HTMLElement {
  setConfig(config) {
    this.config = config || {};
    this.attachShadow({mode:'open'});
    this.shadowRoot.innerHTML = `
      <style>
      ha-card{padding:16px}.title{font-size:18px;font-weight:600;margin-bottom:12px}.row{margin:14px 0}.bar{height:22px;border-radius:6px;background:#333;overflow:hidden}.fill{height:100%;width:0%;transition:width .12s linear}.peak{background:linear-gradient(90deg,#4caf50 0%,#8bc34a 60%,#ffc107 80%,#f44336 100%)}.rms{background:linear-gradient(90deg,#2196f3,#00bcd4,#4caf50)}.stats{display:flex;justify-content:space-between;font-size:13px;margin:5px 0 10px}.controls{display:flex;align-items:center;gap:10px}.controls input{flex:1}.mute{min-width:80px}.section{margin-top:8px}.label{font-weight:600;margin-bottom:5px}.sep{border-top:1px solid var(--divider-color,#444);margin:18px 0}.small{font-size:12px;opacity:.75}
      </style>
      <ha-card>
        <div class="title">AB13X Audio</div>
        <div class="section"><div class="label">🎙 Input</div>
          <div class="stats"><span>RMS <b id="ir">-60</b> dBFS</span><span>Peak <b id="ip">-60</b> dBFS</span></div>
          <div class="bar"><div id="irm" class="fill rms"></div></div><div class="small">Peak</div>
          <div class="bar"><div id="ipm" class="fill peak"></div></div>
          <div class="controls"><input id="iv" type="range" min="0" max="100" step="1"><span id="ivt">0%</span><button id="im" class="mute">Mute</button></div>
        </div>
        <div class="sep"></div>
        <div class="section"><div class="label">🔊 Output</div>
          <div class="stats"><span>RMS <b id="or">-60</b> dBFS</span><span>Peak <b id="op">-60</b> dBFS</span></div>
          <div class="bar"><div id="orm" class="fill rms"></div></div><div class="small">Peak</div>
          <div class="bar"><div id="opm" class="fill peak"></div></div>
          <div class="controls"><input id="ov" type="range" min="0" max="100" step="1"><span id="ovt">0%</span><button id="om" class="mute">Mute</button></div>
        </div>
      </ha-card>`;
  }
  set hass(hass) {
    this._hass = hass;
    if (!this.config || !this.shadowRoot) return;
    const e = id => this.config[id];
    const set = (id, val) => { const n=this.shadowRoot.getElementById(id); if(n)n.textContent=val; };
    const pct = db => Math.max(0, Math.min(100, ((Number(db)+60)/60)*100));
    const state = id => hass.states[id]?.state;
    const ir=state(e('input_rms')), ip=state(e('input_peak')), or=state(e('output_rms')), op=state(e('output_peak'));
    set('ir', ir ?? '-60'); set('ip', ip ?? '-60'); set('or', or ?? '-60'); set('op', op ?? '-60');
    this.shadowRoot.getElementById('irm').style.width=pct(ir)+'%'; this.shadowRoot.getElementById('ipm').style.width=pct(ip)+'%';
    this.shadowRoot.getElementById('orm').style.width=pct(or)+'%'; this.shadowRoot.getElementById('opm').style.width=pct(op)+'%';
    const iv=Number(state(e('input_volume'))||0), ov=Number(state(e('output_volume'))||0);
    this.shadowRoot.getElementById('iv').value=iv; this.shadowRoot.getElementById('ivt').textContent=iv+'%';
    this.shadowRoot.getElementById('ov').value=ov; this.shadowRoot.getElementById('ovt').textContent=ov+'%';
    this.shadowRoot.getElementById('im').textContent=state(e('input_mute'))==='on'?'Unmute':'Mute';
    this.shadowRoot.getElementById('om').textContent=state(e('output_mute'))==='on'?'Unmute':'Mute';
    this._bind();
  }
  _bind(){
    if(this._bound)return; this._bound=true;
    const h=this._hass;
    const call=(entity,service,data)=>h.callService(service.split('.')[0],service.split('.')[1],{...data,entity_id:entity});
    const iv=this.shadowRoot.getElementById('iv'), ov=this.shadowRoot.getElementById('ov');
    iv.oninput=()=>{this.shadowRoot.getElementById('ivt').textContent=iv.value+'%';};
    ov.oninput=()=>{this.shadowRoot.getElementById('ovt').textContent=ov.value+'%';};
    iv.onchange=()=>call(this.config.input_volume,'number.set_value',{value:Number(iv.value)});
    ov.onchange=()=>call(this.config.output_volume,'number.set_value',{value:Number(ov.value)});
    this.shadowRoot.getElementById('im').onclick=()=>call(this.config.input_mute,'switch.toggle',{});
    this.shadowRoot.getElementById('om').onclick=()=>call(this.config.output_mute,'switch.toggle',{});
  }
  getCardSize(){return 6;}
}
customElements.define('ab13x-audio-meter', Ab13xAudioMeter);
window.customCards=window.customCards||[];window.customCards.push({type:'ab13x-audio-meter',name:'AB13X Audio Meter',description:'Live input/output meter and controls'});
