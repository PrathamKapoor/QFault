import * as THREE from 'three';

// Original open sweeps: two broad ribbons, three fine reflective paths and
// one filament. Each path has a distinct silhouette and deliberate depth.
type Point = [number, number, number];
const paths: Point[][] = [
  [[-.2,1.9,-.35],[-1.15,1.5,-.1],[-1.35,.5,.15],[-.7,-.2,.65],[.85,-.65,.45],[1.1,-1.5,-.2],[.3,-1.9,-.5]],
  [[.25,1.8,-.6],[1.2,1.35,.05],[1.25,.4,.4],[.35,-.15,-.25],[-.85,-.65,-.5],[-1,-1.45,-.2],[-.1,-1.8,.1]],
  [[.05,1.85,-.5],[-1.6,1,-.4],[-1.6,-.5,.4],[-.55,-1.75,.2],[.35,-1.9,-.3]],
  [[.2,1.7,-.3],[1.5,1,.15],[.8,.1,-.8],[-.4,-.6,-.35],[-.6,-1.75,.1]],
  [[-.35,1.75,.1],[-.9,.9,.8],[0,.25,.9],[1.4,-.4,-.05],[.75,-1.65,-.7]]
];
function sweep(points: Point[], index: number, low: boolean) {
  const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)), false, 'centripetal');
  const steps = low ? 110 : 190, sides = 12;
  const vertices: number[] = [], indices: number[] = [], uv: number[] = [];
  for (let i = 0; i <= steps; i++) {
    const u = i / steps, center = curve.getPointAt(u), tangent = curve.getTangentAt(u);
    const normal = new THREE.Vector3(-tangent.y, tangent.x, 0).normalize();
    const binormal = new THREE.Vector3().crossVectors(tangent, normal).normalize();
    const twist = .28 * Math.sin(u * Math.PI * 2 + index * .7);
    normal.applyAxisAngle(tangent, twist); binormal.applyAxisAngle(tangent, twist);
    const taper = .08 + .92 * Math.pow(Math.sin(u * Math.PI), .32);
    const width = (index < 2 ? .105 + .025 * Math.sin(u * Math.PI) : .026 + .006 * index) * taper;
    const thickness = (index < 2 ? .016 : .018) * taper;
    for (let j = 0; j <= sides; j++) {
      const a = j / sides * Math.PI * 2;
      const v = center.clone().addScaledVector(normal, Math.cos(a) * width).addScaledVector(binormal, Math.sin(a) * thickness);
      vertices.push(v.x, v.y, v.z); uv.push(u * 12, j / sides);
      if (i < steps && j < sides) {const k = i * (sides + 1) + j;indices.push(k,k+sides+1,k+1,k+1,k+sides+1,k+sides+2);}
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
  geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
  geometry.setIndex(indices);geometry.computeVertexNormals();return geometry;
}
export function createQuantumSculpture(canvas:HTMLCanvasElement,reduced:boolean,onFailure:()=>void){
  const context=canvas.getContext('webgl2',{alpha:true,antialias:true,powerPreference:'low-power'});
  if(!context)return null;
  const renderer=new THREE.WebGLRenderer({canvas,context,alpha:true,antialias:true});
  const low=innerWidth<768||(navigator.hardwareConcurrency||4)<=4;
  renderer.setPixelRatio(Math.min(devicePixelRatio,low?1:1.5));
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(32,1,.1,40),group=new THREE.Group();
  // Dark chrome reflects a dark studio with broad neutral cards, narrow silver
  // strips, and a much dimmer violet rim. No emissive purple body material.
  const studio=new THREE.Scene();studio.background=new THREE.Color('#101016');
  const panels:[Point,number,number,Point][]=[
    [[-3,3,4],4.8,6,[3.5,3.5,3.7]],[[3,1,3],.9,7,[4.5,4.5,4.8]],
    [[0,-4,3],6,1.4,[1.7,1.8,2]],[[0,0,5],6,5,[.3,.32,.36]],
    [[3,2,-4],3,.7,[.48,.28,.9]],[[-4,-1,-2],.6,5,[.18,.3,.55]]
  ];
  for(const [position,w,h,color] of panels){const panel=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:new THREE.Color(...color),side:THREE.DoubleSide}));panel.position.set(...position);panel.lookAt(0,0,0);studio.add(panel);}
  const pmrem=new THREE.PMREMGenerator(renderer),environment=pmrem.fromScene(studio,.045,.1,20,{size:low?64:128});
  scene.environment=environment.texture;pmrem.dispose();
  studio.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();(o.material as THREE.Material).dispose();}});
  // Fine deterministic roughness variation, without scratches or noisy albedo.
  const data=new Uint8Array(64*64*4);
  for(let i=0;i<64*64;i++){const n=225+Math.round(9*Math.sin(i*12.9898));data.set([n,n,n,255],i*4);}
  const grain=new THREE.DataTexture(data,64,64);grain.wrapS=grain.wrapT=THREE.RepeatWrapping;grain.needsUpdate=true;
  const tones=['#4f535e','#717580','#707581','#414752','#9a9faa'];
  paths.forEach((points,i)=>group.add(new THREE.Mesh(sweep(points,i,low),new THREE.MeshPhysicalMaterial({color:tones[i],metalness:1,roughness:i===1?.26:.22,roughnessMap:grain,clearcoat:.3,clearcoatRoughness:.2,envMapIntensity:1.05}))));
  const filament=new THREE.CatmullRomCurve3(paths[0].map(([x,y,z])=>new THREE.Vector3(x+.075,y,z-.035)));
  group.add(new THREE.Mesh(new THREE.TubeGeometry(filament,low?90:150,.008,6,false),new THREE.MeshStandardMaterial({color:'#74668f',metalness:.65,roughness:.35,emissive:'#6d4cc9',emissiveIntensity:.45})));
  group.rotation.set(.05,.13,-.12);scene.add(group);group.updateMatrixWorld(true);
  const bounds=new THREE.Box3().setFromObject(group).getSize(new THREE.Vector3());
  const key=new THREE.DirectionalLight('#eeeef4',1.8);key.position.set(-3,4,5);scene.add(key);
  const rim=new THREE.DirectionalLight('#8e77c8',.55);rim.position.set(4,1,-3);scene.add(rim);
  let raf=0,visible=true,alive=true,paused=false,px=0,py=0,sx=0,sy=0,last=0;
  const draw=(now:number)=>{raf=0;if(!alive||!visible||document.hidden||paused)return;
    if(now-last>32||reduced){last=now;const t=reduced?0:now*.001;sx+=(px-sx)*.03;sy+=(py-sy)*.03;
      group.rotation.y=.13+Math.sin(t*.06)*.018+sx*.045;group.rotation.x=.05+sy*.025;
      group.children.forEach((strand,i)=>{strand.position.y=reduced?0:Math.sin(t*.12+i)*.009;});
      renderer.render(scene,camera);canvas.dataset.rendered='true';}
    if(!reduced)raf=requestAnimationFrame(draw);
  };
  const wake=()=>{if(!raf&&!paused&&visible&&!document.hidden&&alive)raf=requestAnimationFrame(draw);};
  const resize=()=>{const r=canvas.getBoundingClientRect();renderer.setSize(Math.max(1,r.width),Math.max(1,r.height),false);camera.aspect=r.width/Math.max(r.height,1);
    const tan=Math.tan(Math.PI*32/360);camera.position.set(0,0,Math.max(bounds.y/(2*tan*.86),bounds.x/(2*tan*camera.aspect*.86))+bounds.z*.5);camera.lookAt(0,0,0);camera.updateProjectionMatrix();wake();};
  const ro=new ResizeObserver(resize);ro.observe(canvas);
  const io=new IntersectionObserver(([e])=>{visible=e.isIntersecting;if(!visible){cancelAnimationFrame(raf);raf=0;}else wake();});io.observe(canvas);
  const visibility=()=>{cancelAnimationFrame(raf);raf=0;wake();};
  const pointer=(e:PointerEvent)=>{if(!reduced){px=e.clientX/innerWidth*2-1;py=e.clientY/innerHeight*2-1;}};
  const lost=(e:Event)=>{e.preventDefault();cancelAnimationFrame(raf);raf=0;onFailure();};
  document.addEventListener('visibilitychange',visibility);window.addEventListener('pointermove',pointer,{passive:true});canvas.addEventListener('webglcontextlost',lost);resize();
  return {pause(){paused=true;cancelAnimationFrame(raf);raf=0;},destroy(){alive=false;cancelAnimationFrame(raf);ro.disconnect();io.disconnect();document.removeEventListener('visibilitychange',visibility);window.removeEventListener('pointermove',pointer);canvas.removeEventListener('webglcontextlost',lost);group.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();(o.material as THREE.Material).dispose();}});grain.dispose();environment.dispose();renderer.dispose();renderer.forceContextLoss();}};
}
