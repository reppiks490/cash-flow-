// Deterministic DOM-contract checks; this is not a browser or device test.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=require('node:path').resolve(process.argv[2]||require('node:path').resolve(__dirname,'../../../../apps/offer-page/index.html'));
const html=fs.readFileSync(source,'utf8');const code=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
function environment({gpu=true,reduced=false}={}){
 let focus=null,draws=0,seq=0,clip='',download=null,revoked=false;
 const callbacks=new Map(),elements=[],listeners={},mediaListeners=[];
 class El{
  constructor(tag,attrs={}){this.tagName=tag.toUpperCase();this.attrs={...attrs};this.id=attrs.id;this.dataset={};Object.keys(attrs).filter(k=>k.startsWith('data-')).forEach(k=>this.dataset[k.slice(5)]=attrs[k]);this.hidden='hidden'in attrs;this.disabled=false;this.value=attrs.value||'';this.textContent='';this.innerHTML='';this.events={};this.offsetWidth=10;this.open=false;this.children=[];this.parentNode=null;this.nextSibling=null;this.style={setProperty:(k,v)=>this.attrs[k]=v};const cs=new Set((attrs.class||'').split(' '));this.classList={add:x=>cs.add(x),remove:x=>cs.delete(x),contains:x=>cs.has(x),toggle:(x,on)=>on===false?cs.delete(x):on===true?cs.add(x):cs.has(x)?cs.delete(x):cs.add(x)};}
  setAttribute(k,v){this.attrs[k]=String(v)} getAttribute(k){return this.attrs[k]??null}
  addEventListener(n,f){(this.events[n]??=[]).push(f)}fire(n,e={}){return(this.events[n]||[]).map(f=>f({target:this,preventDefault(){},...e}))}
  appendChild(x){this.children.push(x);x.parentNode=this;return x}insertBefore(x){this.appendChild(x)}
  remove(){}focus(){focus=this}select(){this.selected=true}click(){download=this.download;this.fire('click')}
  showModal(){this.open=true}close(){this.open=false;this.fire('close')}
  getBoundingClientRect(){return{width:this.hidden?0:1000,height:this.hidden?0:630,left:0,top:0,right:1000,bottom:630}}
  setPointerCapture(){}getContext(){return gpu?gl:null}reportValidity(){return true}setCustomValidity(v){this.validationMessage=v}
 }
 for(const match of html.matchAll(/<([a-z][\w-]*)\b([^>]*)>/gi)){
  const attrs={};for(const [,k,v]of match[2].matchAll(/([\w-]+)="([^"]*)"/g))attrs[k]=v;
  if(/(?:^|\s)hidden(?:\s|$)/.test(match[2]))attrs.hidden='';elements.push(new El(match[1],attrs));
 }
 const ids={};for(const e of elements)if(e.id){assert(!ids[e.id],'duplicate ID '+e.id);ids[e.id]=e;}
 const body=new El('body');for(const e of elements)e.parentNode=body;
 function all(s){if(s[0]==='#')return elements.filter(e=>e.id===s.slice(1));if(s[0]==='.')return elements.filter(e=>e.classList.contains(s.slice(1)));const m=s.match(/^\[([^\]]+)\]$/);return m?elements.filter(e=>m[1]in e.attrs):[];}
 const uniforms={};const gl={VERTEX_SHADER:1,FRAGMENT_SHADER:2,HIGH_FLOAT:3,COMPILE_STATUS:4,LINK_STATUS:5,ARRAY_BUFFER:6,STATIC_DRAW:7,FLOAT:8,TRIANGLES:9,createShader:()=>({}),shaderSource(){},compileShader(){},getShaderParameter:()=>true,deleteShader(){},getShaderPrecisionFormat:()=>({precision:23}),createProgram:()=>({}),attachShader(){},linkProgram(){},getProgramParameter:()=>true,useProgram(){},createBuffer:()=>({}),bindBuffer(){},bufferData(){},getAttribLocation:()=>0,enableVertexAttribArray(){},vertexAttribPointer(){},getUniformLocation:(p,n)=>n,viewport(){},uniform2f:(n,...v)=>uniforms[n]=v,uniform3f:(n,...v)=>uniforms[n]=v,uniform1f:(n,v)=>uniforms[n]=v,drawArrays:()=>draws++};
 const media={matches:reduced,addEventListener:(n,f)=>mediaListeners.push(f)};
 const doc={body,hidden:false,documentElement:{scrollHeight:3000,style:{setProperty(){}},classList:{add(){}}},execCommand:()=>false,querySelector:s=>all(s)[0],querySelectorAll:all,getElementById:id=>ids[id],createElement:t=>new El(t),addEventListener:(n,f)=>(listeners[n]??=[]).push(f)};
 const context={document:doc,console,Math,Float32Array,Blob,encodeURIComponent,URL:{createObjectURL:()=> 'blob:test',revokeObjectURL:()=>revoked=true},navigator:{clipboard:{writeText:async s=>{clip=s}}},innerWidth:1000,innerHeight:700,scrollY:0,devicePixelRatio:2,performance:{now:()=>0},IntersectionObserver:class {constructor(f){this.f=f;}observe(){}},matchMedia:()=>media,requestAnimationFrame:f=>{callbacks.set(++seq,f);return seq},cancelAnimationFrame:id=>callbacks.delete(id),setTimeout:f=>f()};
 context.window={matchMedia:()=>media,innerHeight:700,scrollY:0,addEventListener:(n,f)=>(listeners[n]??=[]).push(f)};
 vm.createContext(context);vm.runInContext(code,context);
 return{ids,all,callbacks,context,doc,uniforms,media,get draws(){return draws},get focus(){return focus},get clip(){return clip},get download(){return download},get revoked(){return revoked},run(t){const fns=[...callbacks.values()];callbacks.clear();fns.forEach(f=>f(t))},fire(n){(listeners[n]||[]).forEach(f=>f())},mediaChange(v){media.matches=v;mediaListeners.forEach(f=>f({matches:v}))}};
}


(async()=>{
let failed=0;
async function check(label,fn){try{await fn();console.log('PASS '+label)}catch(error){failed++;console.error('FAIL '+label+': '+error.message)}}
await check('Reduced-motion startup presents a visible still',()=>{
const e=environment({reduced:true});assert(e.draws>0||!e.ids['webgl-fallback'].hidden,'zero draws while fallback is hidden');
});
await check('Immersive open preserves selected material and lighting',()=>{
const e=environment();e.ids['material-vellum'].fire('click');e.ids['light-toggle'].fire('click');e.ids['open-immerse'].fire('click');e.run(100);
assert.equal(e.uniforms.u_mode,0,'dialog should retain Vellum');assert.equal(e.uniforms.u_light,1,'dialog should retain changed lighting');
});
await check('Visibility synchronization keeps a closed dialog paused',()=>{
const e=environment();e.ids['open-immerse'].fire('click');e.ids['immersive-dialog'].close();const before=e.callbacks.size;e.fire('visibilitychange');assert.equal(e.callbacks.size,before,'closed dialog scheduled a new frame');
});
await check('Failed legacy copy does not report success',async()=>{
const e=environment();for(const key of ['brief-business','brief-audience','brief-message','brief-cta'])e.ids[key].value='Example';e.ids['brief-form'].fire('submit');await Promise.all(e.ids['brief-copy'].fire('click'));
assert(!/Brief copied/.test(e.ids['brief-status'].textContent),'execCommand false was reported as copied');
});
console.log(`${4-failed}/4 runtime contracts passed; DOM simulation, not browser/device QA.`);process.exitCode=failed?1:0;
})().catch(e=>{console.error(e);process.exitCode=1});
