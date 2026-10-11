import * as THREE from 'three';

/** Original QFAULT geometry. Closed asymmetric sweeps with flattened, tapered
 * cross sections. No torus primitives or rigid continuous rotation. */
function ribbon(index:number,low:boolean){
  const points:THREE.Vector3[]=[];
  for(let i=0;i<100;i++){
    const t=i/100*Math.PI*2,p=index*1.57;
    const radius=1.05+.24*Math.cos(3*t+p);
    points.push(new THREE.Vector3(
      radius*Math.sin(t+p)+.36*Math.sin(2*t+.3*p),
      1.5*Math.cos(t)+.32*Math.sin(2*t+p),
      .65*Math.sin(2*t+p)+.18*Math.cos(3*t)));
  }
  const curve=new THREE.CatmullRomCurve3(points,true,'centripetal');
  const steps=low?150:280,sides=low?10:16,frames=curve.computeFrenetFrames(steps,true);
  const vertices:number[]=[],indices:number[]=[];
  for(let i=0;i<=steps;i++){
    const u=i/steps,center=curve.getPointAt(u),twist=Math.sin(u*Math.PI*4+index)*.5;
    const n=frames.normals[i].clone().applyAxisAngle(frames.tangents[i],twist);
    const b=frames.binormals[i].clone().applyAxisAngle(frames.tangents[i],twist);
    const width=(.15+.045*Math.sin(u*Math.PI*6+index))*(index===3?.65:1);
    for(let j=0;j<=sides;j++){
      const a=j/sides*Math.PI*2;
      const v=center.clone().addScaledVector(n,Math.cos(a)*width).addScaledVector(b,Math.sin(a)*.052);
      vertices.push(v.x,v.y,v.z);
      if(i<steps&&j<sides){const k=i*(sides+1)+j;indices.push(k,k+sides+1,k+1,k+1,k+sides+1,k+sides+2)}
    }
  }
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geometry.setIndex(indices);geometry.computeVertexNormals();
  return geometry;
}

export function createQuantumSculpture(canvas:HTMLCanvasElement,reduced:boolean,onFailure:()=>void){
  const context=canvas.getContext('webgl2',{alpha:true,antialias:true,powerPreference:'low-power'});
  if(!context)return null;
  const renderer=new THREE.WebGLRenderer({canvas,context,alpha:true,antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<768?1:1.5));
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(35,1,.1,40),group=new THREE.Group();
  const low=innerWidth<768||(navigator.hardwareConcurrency||4)<=4;
  const studio=new THREE.Scene();studio.background=new THREE.Color('#080810');
  const panels:[number,number,number,number,number,THREE.Color][]=[
    [-3,4,3,4,6,new THREE.Color(5,5,5.5)],
    [4,1,2,1.3,7,new THREE.Color(3,3.2,4)],
    [-4,-2,1,2,5,new THREE.Color(.65,.3,1.7)],
    [1,3,-4,4,1,new THREE.Color(1.4,.8,3)],
    [0,-4,2,5,1,new THREE.Color(.8,.9,1.2)]];
  panels.forEach(([x,y,z,w,h,c])=>{const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:c,side:THREE.DoubleSide}));m.position.set(x,y,z);m.lookAt(0,0,0);studio.add(m)});
  const pmrem=new THREE.PMREMGenerator(renderer),environment=pmrem.fromScene(studio,.06,.1,20);scene.environment=environment.texture;pmrem.dispose();
  studio.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();(o.material as THREE.Material).dispose()}});
  for(let i=0;i<4;i++)group.add(new THREE.Mesh(ribbon(i,low),new THREE.MeshPhysicalMaterial({color:i===3?'#4b4260':'#3a3941',metalness:1,roughness:.19+i*.018,clearcoat:.75,clearcoatRoughness:.13,envMapIntensity:1.6})));
  group.rotation.set(.13,-.35,-.34);scene.add(group);
  const key=new THREE.DirectionalLight('#ffffff',3);key.position.set(-3,5,4);scene.add(key);
  const rim=new THREE.DirectionalLight('#7b5cff',1.5);rim.position.set(3,-2,-3);scene.add(rim);
  let raf=0,visible=true,alive=true,paused=false,px=0,py=0,sx=0,sy=0,last=0;
  const draw=(now:number)=>{
    raf=0;if(!alive||!visible||document.hidden||paused)return;
    if(now-last>32||reduced){last=now;const t=reduced?0:now*.001;sx+=(px-sx)*.035;sy+=(py-sy)*.035;
      group.rotation.y=-.35+Math.sin(t*.08)*.035+sx*.09;group.rotation.x=.13+sy*.055;
      group.position.y=Math.sin(t*.13)*.025;renderer.render(scene,camera);canvas.dataset.rendered='true'}
    if(!reduced)raf=requestAnimationFrame(draw);
  };
  const wake=()=>{if(!raf&&!paused&&visible&&!document.hidden&&alive)raf=requestAnimationFrame(draw)};
  const resize=()=>{const r=canvas.getBoundingClientRect();renderer.setSize(Math.max(1,r.width),Math.max(1,r.height),false);camera.aspect=r.width/Math.max(r.height,1);camera.position.set(0,0,Math.max(6.8,3.0/(Math.tan(Math.PI*35/360)*camera.aspect)));camera.lookAt(0,0,0);camera.updateProjectionMatrix();wake()};
  const ro=new ResizeObserver(resize);ro.observe(canvas);
  const io=new IntersectionObserver(([e])=>{visible=e.isIntersecting;if(!visible){cancelAnimationFrame(raf);raf=0}else wake()});io.observe(canvas);
  const visibility=()=>{cancelAnimationFrame(raf);raf=0;wake()};
  const pointer=(e:PointerEvent)=>{if(reduced)return;px=e.clientX/innerWidth*2-1;py=e.clientY/innerHeight*2-1};
  const lost=(e:Event)=>{e.preventDefault();cancelAnimationFrame(raf);raf=0;onFailure()};
  document.addEventListener('visibilitychange',visibility);window.addEventListener('pointermove',pointer,{passive:true});canvas.addEventListener('webglcontextlost',lost);resize();
  return {pause(){paused=true;cancelAnimationFrame(raf);raf=0},destroy(){alive=false;cancelAnimationFrame(raf);ro.disconnect();io.disconnect();document.removeEventListener('visibilitychange',visibility);window.removeEventListener('pointermove',pointer);canvas.removeEventListener('webglcontextlost',lost);group.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();(o.material as THREE.Material).dispose()}});environment.dispose();renderer.dispose();renderer.forceContextLoss()}};
}
