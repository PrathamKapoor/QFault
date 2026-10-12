import * as THREE from 'three';

// Original sculptural double helix. Companion paths follow the same rising
// flow rather than enclosing a volume; there are no rings, rungs or core.
type Point = [number, number, number];
function spiral(index:number):Point[]{
  return Array.from({length:101},(_,i)=>{
    const t=i/100,phase=index%2*Math.PI+(index>1?.24:0);
    const angle=t*Math.PI*2*1.48+phase+.2;
    const radius=.86+.29*Math.sin(t*Math.PI)+.045*Math.sin(t*9+phase)+(index>1?.19:0);
    return [Math.cos(angle)*radius+.12*Math.sin(t*4), (t-.5)*6.1, Math.sin(angle)*radius*.88] as Point;
  });
}
const paths=[0,1,2,3].map(spiral);
function sweep(points: Point[], index: number, low: boolean) {
  const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)), false, 'centripetal');
  const steps = low ? 150 : 260, sides = 20;
  const vertices: number[] = [], indices: number[] = [], uv: number[] = [];
  for (let i = 0; i <= steps; i++) {
    const u = i / steps, center = curve.getPointAt(u), tangent = curve.getTangentAt(u);
    const normal = new THREE.Vector3(-tangent.y, tangent.x, 0).normalize();
    const binormal = new THREE.Vector3().crossVectors(tangent, normal).normalize();
    const twist = .48 * Math.sin(u * Math.PI * 3 + index * .8) + .3;
    normal.applyAxisAngle(tangent, twist); binormal.applyAxisAngle(tangent, twist);
    const taper = .08 + .92 * Math.pow(Math.sin(u * Math.PI), .32);
    const width = (index < 2 ? .23 + .10 * Math.pow(Math.sin(u * Math.PI * 1.4 + index * .6),2) : .045) * taper;
    const thickness = (index < 2 ? .038 : .018) * taper;
    for (let j = 0; j <= sides; j++) {
      const a = j / sides * Math.PI * 2;
      const v = center.clone().addScaledVector(normal, Math.cos(a) * width).addScaledVector(binormal, Math.sin(a) * thickness);
      vertices.push(v.x, v.y, v.z); uv.push(u, j / sides);
      if (i < steps && j < sides) {const k = i * (sides + 1) + j;indices.push(k,k+1,k+sides+1,k+1,k+sides+2,k+sides+1);}
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
  geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
  geometry.setIndex(indices);geometry.computeVertexNormals();
  // Join duplicate vertices at the profile seam for continuous surface shading.
  const normals=geometry.getAttribute('normal');
  for(let i=0;i<=steps;i++){const a=i*(sides+1),b=a+sides;
    const n=new THREE.Vector3().fromBufferAttribute(normals,a).add(new THREE.Vector3().fromBufferAttribute(normals,b)).normalize();
    normals.setXYZ(a,n.x,n.y,n.z);normals.setXYZ(b,n.x,n.y,n.z);}
  return geometry;
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
  const studio=new THREE.Scene();studio.background=new THREE.Color('#020204');
  const panels:[Point,number,number,Point][]=[
    [[-3,4,4],6,1.1,[5,5,5.3]],[[4,1,2],.5,7,[4.5,4.6,5]],
    [[0,-4,2],7,.65,[1.1,1.15,1.3]],[[-2,0,5],4,4,[1.15,1.18,1.3]],
    [[3,2,-4],4,.5,[.5,.28,1.1]],[[-4,-1,-2],.4,5,[.15,.26,.6]]
  ];
  for(const [position,w,h,color] of panels){const panel=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:new THREE.Color(...color),side:THREE.DoubleSide}));panel.position.set(...position);panel.lookAt(0,0,0);studio.add(panel);}
  const pmrem=new THREE.PMREMGenerator(renderer),environment=pmrem.fromScene(studio,.045,.1,20,{size:low?64:128});
  scene.environment=environment.texture;pmrem.dispose();
  studio.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();(o.material as THREE.Material).dispose();}});
  // Fine deterministic roughness variation, without scratches or noisy albedo.
  const data=new Uint8Array(512*128*4);
  for(let y=0;y<128;y++)for(let x=0;x<512;x++){
    // Longitudinal brushing with fine, deterministic variation across the ribbon.
    const line=Math.sin(y*19.731)*.6+Math.sin(y*7.17)*.4;
    const n=Math.round(195+line*12+Math.sin(x*.12+y*3.7)*3);
    data.set([n,n,n,255],(y*512+x)*4);
  }
  const grain=new THREE.DataTexture(data,512,128);grain.wrapS=grain.wrapT=THREE.RepeatWrapping;grain.needsUpdate=true;
  grain.magFilter=THREE.LinearFilter;grain.minFilter=THREE.LinearMipmapLinearFilter;grain.generateMipmaps=true;
  grain.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
  const tones=['#454752','#383a45','#4b4d58','#3d3e4b'];
  paths.forEach((points,i)=>group.add(new THREE.Mesh(sweep(points,i,low),new THREE.MeshPhysicalMaterial({color:tones[i],metalness:1,roughness:i===1?.32:.28,roughnessMap:grain,bumpMap:grain,bumpScale:.00015,anisotropy:.35,anisotropyRotation:0,clearcoat:.22,clearcoatRoughness:.24,envMapIntensity:1.35}))));
  const filament=new THREE.CatmullRomCurve3(paths[1].map(([x,y,z])=>new THREE.Vector3(x-.07,y+.03,z-.06)));
  group.add(new THREE.Mesh(new THREE.TubeGeometry(filament,low?90:150,.008,6,false),new THREE.MeshStandardMaterial({color:'#74668f',metalness:.65,roughness:.35,emissive:'#6d4cc9',emissiveIntensity:.45})));
  group.rotation.set(.05,.13,-.29);scene.add(group);group.updateMatrixWorld(true);
  const bounds=new THREE.Box3().setFromObject(group).getSize(new THREE.Vector3());
  const key=new THREE.DirectionalLight('#eeeef4',1.8);key.position.set(-3,4,5);scene.add(key);
  const rim=new THREE.DirectionalLight('#8e77c8',.3);rim.position.set(4,1,-3);scene.add(rim);
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
