# Three.js 速查手册

> 一份通俗易懂的 Three.js 文档，从零开始到实战场景，每个知识点都有可运行的代码示例。

---

## 目录

- [1. 基础概念](#1-基础概念)
- [2. 环境搭建](#2-环境搭建)
- [3. 三大组件：场景/相机/渲染器](#3-三大组件场景相机渲染器)
- [4. 几何体](#4-几何体)
- [5. 材质与光照](#5-材质与光照)
- [6. 纹理与贴图](#6-纹理与贴图)
- [7. 动画与渲染循环](#7-动画与渲染循环)
- [8. 交互控制](#8-交互控制)
- [9. 加载 3D 模型](#9-加载-3d-模型)
- [10. 粒子系统](#10-粒子系统)
- [11. 后期处理](#11-后期处理)
- [12. 性能优化](#12-性能优化)
- [13. 实战场景](#13-实战场景)
- [14. 常见问题排查](#14-常见问题排查)
- [15. 配置属性速查](#15-配置属性速查)

---

## 1. 基础概念

### Three.js 是什么？

Three.js 是一个基于 **WebGL** 的 JavaScript 3D 库，让你在浏览器中创建和显示 3D 图形，而无需直接操作复杂的 WebGL API。

### 核心概念

| 概念 | 说明 | 类比 |
|------|------|------|
| **Scene（场景）** | 所有物体的容器 | 舞台 |
| **Camera（相机）** | 观察场景的视角 | 眼睛/摄像机 |
| **Renderer（渲染器）** | 把场景画出来 | 画笔 |
| **Geometry（几何体）** | 物体的形状 | 骨架 |
| **Material（材质）** | 物体的表面外观 | 皮肤 |
| **Mesh（网格）** | 几何体 + 材质 = 物体 | 完整的人 |
| **Light（光源）** | 照亮场景 | 灯光 |
| **Texture（纹理）** | 物体表面的贴图 | 印花 |

### 坐标系统

```
        Y (上)
        │
        │
        │
        └─────── X (右)
       /
      /
     /
    Z (前，屏幕外)
```

- Three.js 使用**右手坐标系**
- X 轴：向右
- Y 轴：向上
- Z 轴：向前（屏幕外方向）

---

## 2. 环境搭建

### 方式 1：CDN（最快上手）

```html
<!DOCTYPE html>
<html>
<head>
    <title>Three.js Demo</title>
</head>
<body>
    <script type="importmap">
    {
        "imports": {
            "three": "https://unpkg.com/three@0.170.0/build/three.module.js",
            "three/addons/": "https://unpkg.com/three@0.170.0/examples/jsm/"
        }
    }
    </script>
    <script type="module">
        import * as THREE from 'three';
        console.log('Three.js 版本:', THREE.REVISION);
    </script>
</body>
</html>
```

### 方式 2：npm（推荐项目使用）

```bash
npm create vite@latest my-3d-app -- --template vanilla
cd my-3d-app
npm install three
```

```js
// main.js
import * as THREE from 'three';
```

### 方式 3：Vite + React 项目

```bash
npm create vite@latest my-3d-app -- --template react
cd my-3d-app
npm install three
```

---

## 3. 三大组件：场景/相机/渲染器

### 第一个 3D 场景 — 旋转的立方体

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; overflow: hidden; }
        canvas { display: block; }
    </style>
</head>
<body>
<script type="importmap">
{
    "imports": {
        "three": "https://unpkg.com/three@0.170.0/build/three.module.js"
    }
}
</script>
<script type="module">
import * as THREE from 'three';

// ===== 1. 创建场景 =====
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);  // 深蓝色背景

// ===== 2. 创建相机 =====
// PerspectiveCamera(视角角度, 宽高比, 近裁面, 远裁面)
const camera = new THREE.PerspectiveCamera(
    75,                                   // 视角：75度（人眼约60度）
    window.innerWidth / window.innerHeight, // 宽高比
    0.1,                                  // 近裁面：0.1米内的看不见
    1000                                  // 远裁面：1000米外的看不见
);
camera.position.z = 5;                    // 相机往后移5米

// ===== 3. 创建渲染器 =====
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio); // 高清屏适配
renderer.shadowMap.enabled = true;                // 开启阴影
document.body.appendChild(renderer.domElement);

// ===== 4. 创建物体 =====
const geometry = new THREE.BoxGeometry(1, 1, 1);       // 1x1x1 立方体
const material = new THREE.MeshStandardMaterial({       // 标准材质
    color: 0x00ff88,
    roughness: 0.3,
    metalness: 0.8,
});
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// ===== 5. 添加光源 =====
// 环境光：均匀照亮所有面
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

// 平行光：模拟太阳光
const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 5, 5);
scene.add(directionalLight);

// ===== 6. 渲染循环 =====
function animate() {
    requestAnimationFrame(animate);

    // 旋转物体
    cube.rotation.x += 0.01;
    cube.rotation.y += 0.01;

    // 渲染
    renderer.render(scene, camera);
}
animate();

// ===== 7. 窗口自适应 =====
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

### 两种相机对比

```js
// 透视相机（近大远小，3D 场景首选）
const perspectiveCamera = new THREE.PerspectiveCamera(
    75, window.innerWidth / window.innerHeight, 0.1, 1000
);

// 正交相机（无透视，适合 CAD/工程图/2.5D）
const orthographicCamera = new THREE.OrthographicCamera(
    -5, 5,   // 左右
    5, -5,   // 上下
    0.1, 100 // 远近
);
```

| | PerspectiveCamera | OrthographicCamera |
|------|-------------------|-------------------|
| 视觉效果 | 近大远小（真实） | 无透视（等距） |
| 适合场景 | 游戏、VR、建筑漫游 | CAD、策略游戏、UI |
| 视锥体 | 金字塔形 | 长方体 |

---

## 4. 几何体

### 内置几何体速览

```js
// ===== 基础几何体 =====
// 立方体 (宽, 高, 深, 宽分段, 高分段, 深分段)
new THREE.BoxGeometry(1, 1, 1);

// 球体 (半径, 水平分段, 垂直分段)
new THREE.SphereGeometry(1, 32, 16);

// 圆柱体 (顶半径, 底半径, 高, 分段)
new THREE.CylinderGeometry(1, 1, 2, 32);

// 圆锥体
new THREE.ConeGeometry(1, 2, 32);

// 圆环体 (半径, 管半径, 径向分段, 管分段)
new THREE.TorusGeometry(1, 0.3, 16, 100);

// ===== 进阶几何体 =====
// 平面 (宽, 高)
new THREE.PlaneGeometry(5, 5);

// 圆环结
new THREE.TorusKnotGeometry(1, 0.3, 100, 16);

// 二十面体
new THREE.IcosahedronGeometry(1, 0);  // detail=0 是基本型

// ===== 自定义形状 =====
// 通过定义顶点和面来创建形状
const shape = new THREE.Shape();
shape.moveTo(0, 0);
shape.lineTo(1, 0);
shape.lineTo(0.5, 1);
shape.closePath();
new THREE.ShapeGeometry(shape);

// 拉伸体（给平面形状加深度）
new THREE.ExtrudeGeometry(shape, { depth: 0.5, bevelEnabled: true });
```

### 实战：几何体陈列

```html
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111122);

const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 50);
camera.position.set(0, 3, 10);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// 轨道控制器（鼠标旋转/缩放/平移）
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// 光照
scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const dirLight = new THREE.DirectionalLight(0xffffff, 1);
dirLight.position.set(5, 10, 5);
scene.add(dirLight);

// 地面网格（辅助线）
const gridHelper = new THREE.GridHelper(10, 10);
scene.add(gridHelper);

// 排列 8 种几何体
const geometries = [
    { name: 'Box',             geo: new THREE.BoxGeometry(0.6, 0.6, 0.6) },
    { name: 'Sphere',          geo: new THREE.SphereGeometry(0.4, 32, 16) },
    { name: 'Cylinder',        geo: new THREE.CylinderGeometry(0.3, 0.3, 0.8, 32) },
    { name: 'Cone',            geo: new THREE.ConeGeometry(0.35, 0.8, 32) },
    { name: 'Torus',           geo: new THREE.TorusGeometry(0.35, 0.15, 16, 32) },
    { name: 'TorusKnot',       geo: new THREE.TorusKnotGeometry(0.3, 0.1, 64, 8) },
    { name: 'Icosahedron',     geo: new THREE.IcosahedronGeometry(0.35, 0) },
    { name: 'Dodecahedron',    geo: new THREE.DodecahedronGeometry(0.35, 0) },
];

const colors = [0xff6b6b, 0x4ecdc4, 0x45b7d1, 0xf9ca24, 0x6ab04c, 0xe056a0, 0x686de0, 0xbe2edd];

geometries.forEach((item, i) => {
    const material = new THREE.MeshStandardMaterial({
        color: colors[i],
        roughness: 0.3,
        metalness: 0.5,
    });
    const mesh = new THREE.Mesh(item.geo, material);

    // 2 行 4 列排列
    const row = Math.floor(i / 4);
    const col = i % 4;
    mesh.position.set(col * 2 - 3, 1 - row * 2, 0);

    mesh.castShadow = true;
    scene.add(mesh);
});

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();
</script>
```

---

## 5. 材质与光照

### 材质类型速查

| 材质 | 特点 | 需要光源 | 适用场景 |
|------|------|---------|---------|
| **MeshStandardMaterial** | PBR 物理渲染，最真实 | ✅ | 通用，物理正确的材质（推荐） |
| **MeshPhongMaterial** | 镜面高光 | ✅ | 需要高光反射的物体 |
| **MeshLambertMaterial** | 漫反射，无高光 | ✅ | 哑光表面 |
| **MeshBasicMaterial** | 不受光影响，纯色 | ❌ | 线框、调试、纯色物体 |
| **MeshNormalMaterial** | 法线方向彩色显示 | ❌ | 调试法线方向 |
| **MeshMatcapMaterial** | 烘焙光照贴图 | ❌ | 性能要求高的场景 |
| **MeshToonMaterial** | 卡通风格 | ✅ | 卡通渲染 |

### 实战：材质对比面板

```js
import * as THREE from 'three';

function createMaterialShowcase(scene) {
    const sphereGeo = new THREE.SphereGeometry(0.4, 32, 16);

    const materials = [
        { name: 'Standard', mat: new THREE.MeshStandardMaterial({ color: 0xff6b6b, roughness: 0.2, metalness: 0.8 }) },
        { name: 'Phong',    mat: new THREE.MeshPhongMaterial({ color: 0x4ecdc4, shininess: 100, specular: 0xffffff }) },
        { name: 'Lambert',  mat: new THREE.MeshLambertMaterial({ color: 0x45b7d1 }) },
        { name: 'Basic',    mat: new THREE.MeshBasicMaterial({ color: 0xf9ca24 }) },
        { name: 'Normal',   mat: new THREE.MeshNormalMaterial() },
        { name: 'Toon',     mat: new THREE.MeshToonMaterial({ color: 0x6ab04c }) },
    ];

    const group = new THREE.Group();

    materials.forEach((item, i) => {
        const mesh = new THREE.Mesh(sphereGeo, item.mat);
        mesh.position.x = (i - materials.length / 2 + 0.5) * 1.5;
        group.add(mesh);
    });

    return group;
}
```

### 光源类型

```js
// 1. 环境光 — 基础亮度，让暗面不完全黑
const ambient = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambient);

// 2. 平行光 — 模拟太阳，平行光线，有方向
const directional = new THREE.DirectionalLight(0xffffff, 1);
directional.position.set(5, 10, 5);
directional.castShadow = true;  // 投射阴影
directional.shadow.mapSize.width = 1024;
directional.shadow.mapSize.height = 1024;
scene.add(directional);

// 3. 点光源 — 灯泡，向四面八方发光
const point = new THREE.PointLight(0xff0000, 1, 10); // 颜色, 强度, 距离
point.position.set(2, 2, 2);
scene.add(point);

// 4. 聚光灯 — 手电筒，锥形光束
const spot = new THREE.SpotLight(0xffffff, 2, 20, Math.PI/6, 0.3, 0.5);
spot.position.set(0, 5, 0);
spot.castShadow = true;
scene.add(spot);

// 5. 半球光 — 天空色+地面色，模拟户外环境
const hemi = new THREE.HemisphereLight(0x87ceeb, 0x362907, 0.8);
scene.add(hemi);
```

| 光源 | 特点 | 性能 | 阴影支持 |
|------|------|------|---------|
| AmbientLight | 均匀照亮 | 最低 | ❌ |
| DirectionalLight | 平行光（太阳） | 低 | ✅ |
| PointLight | 向四周发光（灯泡） | 中 | ✅ |
| SpotLight | 锥形光（手电筒） | 高 | ✅ |
| HemisphereLight | 天空+地面色 | 低 | ❌ |

---

## 6. 纹理与贴图

### 基本纹理

```js
import * as THREE from 'three';

// 创建纹理加载器
const loader = new THREE.TextureLoader();

// 加载纹理
const texture = loader.load(
    '/textures/wood.jpg',          // 图片路径
    () => console.log('加载完成'),  // 成功回调
    (progress) => {                // 进度回调
        console.log(`${(progress.loaded / progress.total * 100)}%`);
    },
    (err) => console.error('加载失败', err)  // 错误回调
);

// 应用到材质
const material = new THREE.MeshStandardMaterial({
    map: texture,                 // 颜色贴图（最基础）
    roughness: 0.5,
    metalness: 0.1,
});

// 纹理属性
texture.wrapS = THREE.RepeatWrapping;  // 水平重复
texture.wrapT = THREE.RepeatWrapping;  // 垂直重复
texture.repeat.set(2, 2);             // 重复 2x2
texture.offset.set(0.5, 0);           // 偏移
texture.rotation = Math.PI / 4;       // 旋转 45°
```

### 实战：PBR 材质全通道

```js
const loader = new THREE.TextureLoader();

// 同时加载多张贴图
const textures = {
    map:      loader.load('/textures/brick/color.jpg'),     // 颜色贴图
    normalMap: loader.load('/textures/brick/normal.jpg'),   // 法线贴图（凹凸细节）
    roughnessMap: loader.load('/textures/brick/roughness.jpg'), // 粗糙度
    aoMap:      loader.load('/textures/brick/ao.jpg'),      // 环境光遮蔽
    displacementMap: loader.load('/textures/brick/displacement.jpg'), // 置换贴图
};

const sphereGeo = new THREE.SphereGeometry(1, 64, 64);
const sphereMat = new THREE.MeshStandardMaterial({
    ...textures,
    roughness: 0.8,
    metalness: 0.1,
});
const sphere = new THREE.Mesh(sphereGeo, sphereMat);
scene.add(sphere);
```

### 6 面不同纹理的立方体

```js
const materials = [
    new THREE.MeshStandardMaterial({ map: loader.load('/textures/cube/right.jpg') }),
    new THREE.MeshStandardMaterial({ map: loader.load('/textures/cube/left.jpg') }),
    new THREE.MeshStandardMaterial({ map: loader.load('/textures/cube/top.jpg') }),
    new THREE.MeshStandardMaterial({ map: loader.load('/textures/cube/bottom.jpg') }),
    new THREE.MeshStandardMaterial({ map: loader.load('/textures/cube/front.jpg') }),
    new THREE.MeshStandardMaterial({ map: loader.load('/textures/cube/back.jpg') }),
];

const cube = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), materials);
scene.add(cube);
```

### 用 Canvas 动态生成纹理

```js
function createLabelTexture(text) {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 128;

    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#2d3436';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 36px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, canvas.width / 2, canvas.height / 2);

    const texture = new THREE.CanvasTexture(canvas);
    return new THREE.MeshStandardMaterial({ map: texture });
}

const labelPlane = new THREE.Mesh(
    new THREE.PlaneGeometry(1, 0.5),
    createLabelTexture('Three.js')
);
scene.add(labelPlane);
```

---

## 7. 动画与渲染循环

### 基础动画：绕轴旋转

```js
function animate() {
    requestAnimationFrame(animate);

    // 绕 Y 轴旋转
    cube.rotation.y += 0.01;

    // 上下摆动
    cube.position.y = Math.sin(Date.now() * 0.003) * 0.5;

    renderer.render(scene, camera);
}
animate();
```

### 使用 GSAP 实现流畅补间动画

```bash
npm install gsap
```

```js
import gsap from 'gsap';

// 移动到指定位置
gsap.to(cube.position, {
    x: 3,
    y: 2,
    duration: 1.5,
    ease: 'power2.out',
});

// 旋转
gsap.to(cube.rotation, {
    y: Math.PI * 2,   // 转一圈
    duration: 2,
    ease: 'elastic.out(1, 0.5)',
});

// 缩放弹入
gsap.from(cube.scale, {
    x: 0, y: 0, z: 0,
    duration: 1,
    ease: 'back.out(1.7)',
});

// 链式动画
gsap.timeline()
    .to(cube.position, { x: 3, duration: 1 })
    .to(cube.position, { y: 2, duration: 0.5 })
    .to(cube.rotation, { y: Math.PI, duration: 1 });
```

### 实战：物体沿路径运动

```js
import * as THREE from 'three';

// 创建贝塞尔曲线路径
const curve = new THREE.CubicBezierCurve3(
    new THREE.Vector3(-3, 0, 0),   // 起点
    new THREE.Vector3(-1, 3, 2),   // 控制点1
    new THREE.Vector3(1, -3, -2),  // 控制点2
    new THREE.Vector3(3, 0, 0),    // 终点
);

// 可视化路径
const points = curve.getPoints(50);  // 50 个采样点
const pathLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints(points),
    new THREE.LineBasicMaterial({ color: 0xffff00 })
);
scene.add(pathLine);

// 让小球沿路径运动
const ballGeo = new THREE.SphereGeometry(0.2, 16, 16);
const ballMat = new THREE.MeshStandardMaterial({ color: 0xff0000 });
const ball = new THREE.Mesh(ballGeo, ballMat);
scene.add(ball);

function animate() {
    requestAnimationFrame(animate);

    // t 在 0-1 之间循环
    const t = (Math.sin(Date.now() * 0.001) + 1) / 2;
    const point = curve.getPointAt(t);
    ball.position.copy(point);

    renderer.render(scene, camera);
}
animate();
```

---

## 8. 交互控制

### OrbitControls：轨道控制器

```js
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const controls = new OrbitControls(camera, renderer.domElement);

// 配置
controls.enableDamping = true;       // 惯性阻尼（更平滑）
controls.dampingFactor = 0.05;
controls.minDistance = 2;           // 最小缩放距离
controls.maxDistance = 20;          // 最大缩放距离
controls.maxPolarAngle = Math.PI / 2; // 限制只能看到地平线以下
controls.target.set(0, 0, 0);       // 围绕哪个点旋转
controls.update();

function animate() {
    controls.update();  // 必须调用
    renderer.render(scene, camera);
}
```

### Raycaster：射线拾取

```js
import * as THREE from 'three';

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

// 假设有多个可点击的物体
const clickableObjects = [cube1, cube2, cube3];

window.addEventListener('click', (event) => {
    // 将屏幕坐标转为归一化设备坐标 (-1 到 1)
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    // 发射射线
    raycaster.setFromCamera(mouse, camera);

    // 检测碰撞
    const intersects = raycaster.intersectObjects(clickableObjects);

    if (intersects.length > 0) {
        const hitObject = intersects[0].object;

        // 高亮选中物体
        hitObject.material.emissive = new THREE.Color(0x333333);
        console.log('点击了:', hitObject.name || '未命名物体');

        // 取消其他物体的高亮
        clickableObjects.forEach(obj => {
            if (obj !== hitObject) {
                obj.material.emissive = new THREE.Color(0x000000);
            }
        });
    }
});
```

### 实战：3D 商品查看器

```js
// 完整的商品 3D 查看器
class ProductViewer {
    constructor(container, modelUrl) {
        this.container = container;
        this.modelUrl = modelUrl;
        this.init();
    }

    init() {
        // 场景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf0f0f0);

        // 相机
        this.camera = new THREE.PerspectiveCamera(
            45, this.container.clientWidth / this.container.clientHeight, 0.1, 100
        );
        this.camera.position.set(5, 3, 8);

        // 渲染器
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // 限制像素比
        this.container.appendChild(this.renderer.domElement);

        // 轨道控制
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.autoRotate = true;      // 自动旋转
        this.controls.autoRotateSpeed = 1.0;
        this.controls.enableZoom = true;
        this.controls.minPolarAngle = 0.3;    // 限制不翻到底部
        this.controls.maxPolarAngle = Math.PI / 2 + 0.3;

        // 光照
        this.scene.add(new THREE.AmbientLight(0xffffff, 0.6));
        const light1 = new THREE.DirectionalLight(0xffffff, 1);
        light1.position.set(5, 5, 5);
        this.scene.add(light1);

        const light2 = new THREE.DirectionalLight(0xffffff, 0.5);
        light2.position.set(-5, -2, -3);
        this.scene.add(light2);

        // 地面
        const floor = new THREE.Mesh(
            new THREE.PlaneGeometry(10, 10),
            new THREE.MeshStandardMaterial({ color: 0xeeeeee, roughness: 0.8 })
        );
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = -2;
        floor.receiveShadow = true;
        this.scene.add(floor);

        // 加载模型（用 Box 演示，实际替换为 GLTF 模型）
        this.loadModel();

        // 渲染
        this.animate();

        // 响应式
        window.addEventListener('resize', () => this.onResize());
    }

    loadModel() {
        // 这里用 Box 替代，实际用 GLTFLoader
        const geo = new THREE.BoxGeometry(2, 2, 2, 1, 1, 1);
        const mat = new THREE.MeshStandardMaterial({
            color: 0x3498db,
            roughness: 0.2,
            metalness: 0.3,
        });
        this.model = new THREE.Mesh(geo, mat);
        this.model.castShadow = true;
        this.scene.add(this.model);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    onResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }

    // 公开方法
    autoRotate(enable) { this.controls.autoRotate = enable; }
    resetView() {
        this.camera.position.set(5, 3, 8);
        this.controls.target.set(0, 0, 0);
        this.controls.update();
    }
    setBackground(color) { this.scene.background = new THREE.Color(color); }
}
```

---

## 9. 加载 3D 模型

### GLTF/GLB 模型加载（最常用格式）

```bash
npm install three
```

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

// 1. 创建加载器
const loader = new GLTFLoader();

// 2. (可选) 配置 Draco 解压缩器（减小模型体积）
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/v1/decoders/');
loader.setDRACOLoader(dracoLoader);

// 3. 加载模型
loader.load(
    '/models/product.glb',
    (gltf) => {
        const model = gltf.scene;

        // 遍历所有子物体，设置阴影
        model.traverse((child) => {
            if (child.isMesh) {
                child.castShadow = true;
                child.receiveShadow = true;
            }
        });

        scene.add(model);

        // 获取动画（如果有）
        if (gltf.animations.length > 0) {
            const mixer = new THREE.AnimationMixer(model);
            const action = mixer.clipAction(gltf.animations[0]);
            action.play();
        }
    },
    (progress) => {
        const pct = (progress.loaded / progress.total * 100).toFixed(0);
        console.log(`加载中: ${pct}%`);
    },
    (error) => console.error('模型加载失败:', error)
);
```

### 带加载进度条的完整示例

```html
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2c3e50);

const camera = new THREE.PerspectiveCamera(45, innerWidth/innerHeight, 0.1, 50);
camera.position.set(5, 3, 8);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);

new OrbitControls(camera, renderer.domElement);

// 光照
scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const light = new THREE.DirectionalLight(0xffffff, 1.2);
light.position.set(5, 5, 5);
scene.add(light);

// 加载模型（带进度）
const loader = new GLTFLoader();
const progressBar = document.getElementById('progress');

loader.load(
    '/models/scene.glb',
    (gltf) => {
        scene.add(gltf.scene);
        document.getElementById('loading').style.display = 'none';
    },
    (xhr) => {
        const pct = Math.round(xhr.loaded / xhr.total * 100);
        progressBar.style.width = pct + '%';
        progressBar.textContent = pct + '%';
    },
    (err) => {
        console.error('加载失败', err);
        document.getElementById('loading').textContent = '模型加载失败';
    }
);

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();
</script>
```

### FBX / OBJ / Collada 等格式

```js
// FBX (npm install three/examples/jsm/loaders/FBXLoader.js)
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';
new FBXLoader().load('/model.fbx', (fbx) => scene.add(fbx));

// OBJ + MTL
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { MTLLoader } from 'three/addons/loaders/MTLLoader.js';
new MTLLoader().load('/model.mtl', (materials) => {
    materials.preload();
    new OBJLoader().setMaterials(materials).load('/model.obj', (obj) => scene.add(obj));
});

// 加载器汇总
// GLTFLoader/DRACOLoader: 推荐格式（glTF/GLB）
// FBXLoader: Autodesk FBX
// OBJLoader/MTLLoader: OBJ
// ColladaLoader: .dae
// STLLoader: 3D 打印 STL
// SVGLoader: SVG 转 3D
```

---

## 10. 粒子系统

### BufferGeometry 自定义粒子

```js
// 创建 10000 个随机分布的粒子
const particleCount = 10000;
const positions = new Float32Array(particleCount * 3);
const colors = new Float32Array(particleCount * 3);
const sizes = new Float32Array(particleCount);

const color = new THREE.Color();

for (let i = 0; i < particleCount; i++) {
    // 球形随机分布
    const radius = 5;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const r = radius * Math.cbrt(Math.random()); // 立方根让分布更均匀

    positions[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = r * Math.cos(phi);

    // 渐变颜色（内紫外蓝）
    color.setHSL(0.7 + (r / radius) * 0.2, 0.8, 0.6);
    colors[i * 3]     = color.r;
    colors[i * 3 + 1] = color.g;
    colors[i * 3 + 2] = color.b;

    // 随机大小
    sizes[i] = Math.random() * 0.1 + 0.02;
}

const particleGeo = new THREE.BufferGeometry();
particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
particleGeo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

// 圆形粒子纹理
const spriteTexture = (() => {
    const canvas = document.createElement('canvas');
    canvas.width = 32;
    canvas.height = 32;
    const ctx = canvas.getContext('2d');
    ctx.beginPath();
    ctx.arc(16, 16, 14, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();
    return new THREE.CanvasTexture(canvas);
})();

const particleMat = new THREE.PointsMaterial({
    size: 0.1,
    map: spriteTexture,
    vertexColors: true,       // 使用顶点颜色
    blending: THREE.AdditiveBlending, // 叠加混合（发光效果）
    depthWrite: false,
    transparent: true,
});

const particles = new THREE.Points(particleGeo, particleMat);
scene.add(particles);

// 动画：旋转所有粒子
function animate() {
    requestAnimationFrame(animate);
    particles.rotation.y += 0.002;
    particles.rotation.x += 0.001;
    renderer.render(scene, camera);
}
```

### 实战：背景星空

```js
function createStarField(count = 1000) {
    const positions = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
        // 球形分布，半径随机
        const r = 20 + Math.random() * 30;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);

        positions[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
        positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
        positions[i * 3 + 2] = r * Math.cos(phi);
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const mat = new THREE.PointsMaterial({
        size: 0.15,
        color: 0xffffff,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
    });

    const stars = new THREE.Points(geo, mat);
    stars.name = 'stars';
    scene.add(stars);
    return stars;
}
```

---

## 11. 后期处理

```bash
npm install three
```

```js
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { RGBShiftShader } from 'three/addons/shaders/RGBShiftShader.js';

// 创建后期处理管线
const composer = new EffectComposer(renderer);

// 1. 基础渲染通道（必需）
const renderPass = new RenderPass(scene, camera);
composer.addPass(renderPass);

// 2. 泛光效果（Bloom）
const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    1.5,    // 强度
    0.4,    // 半径
    0.85    // 阈值（亮度超过此值才发光）
);
composer.addPass(bloomPass);

// 3. RGB 偏移效果（故障艺术风格）
const rgbShiftPass = new ShaderPass(RGBShiftShader);
rgbShiftPass.uniforms['amount'].value = 0.003;
composer.addPass(rgbShiftPass);

// 渲染循环中用 composer 替代 renderer
function animate() {
    requestAnimationFrame(animate);
    composer.render();  // 而不是 renderer.render()
}
```

### 常用后期效果

```js
// 景深效果
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
const bokehPass = new BokehPass(scene, camera, {
    focus: 5, aperture: 0.02, maxblur: 0.01
});
composer.addPass(bokehPass);

// 胶片颗粒
import { FilmPass } from 'three/addons/postprocessing/FilmPass.js';
const filmPass = new FilmPass(0.35, 0.5, 2048, false);
composer.addPass(filmPass);

// 画面暗角
import { AfterimagePass } from 'three/addons/postprocessing/AfterimagePass.js';
const afterPass = new AfterimagePass(0.95);
composer.addPass(afterPass);
```

---

## 12. 性能优化

### 优化清单

| 优化方向 | 具体措施 | 效果 |
|---------|---------|------|
| **几何体** | 减少分段数（SphereGeometry 的 32→16） | 顶点数减半 |
| | 合并静态几何体 (`BufferGeometryUtils.mergeGeometries`) | 减少 draw call |
| **材质** | 复用材质（不要每个物体 new 一个相同材质） | 减少 GPU 切换 |
| **纹理** | 使用压缩纹理（KTX2/Basis） | 显存减 70% |
| | 合理设置纹理大小（不要用 4096×4096 做小图标） | 显存直接减少 |
| **渲染** | `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))` | 4K 屏不渲染 4K |
| | 离屏物体用 Frustum Culling（默认开启） | 不渲染看不见的 |
| **阴影** | 降低 shadow.mapSize（1024 足够，不需要 4096） | 阴影计算量大幅减少 |
| | 只对必要的灯光开 castShadow | 每个阴影光源都是一个渲染 |
| **实例化** | 大量相同物体用 `InstancedMesh` | 1个 draw call 渲染万个 |
| **LOD** | 远处用低模，近处用高模 (`THREE.LOD`) | 动态平衡画质与性能 |

### InstancedMesh（实例化渲染）

```js
// 场景：10000 棵树，传统方式需要 10000 个 Mesh → 10000 个 draw call
// InstancedMesh：1 个 draw call 渲染 10000 棵

const count = 10000;
const treeGeo = new THREE.ConeGeometry(0.2, 1, 8);
const treeMat = new THREE.MeshStandardMaterial({ color: 0x2ecc71 });

const instancedMesh = new THREE.InstancedMesh(treeGeo, treeMat, count);
instancedMesh.castShadow = true;

// 设置每个实例的位置、旋转、缩放
const dummy = new THREE.Object3D();
const color = new THREE.Color();

for (let i = 0; i < count; i++) {
    // 随机位置
    dummy.position.x = (Math.random() - 0.5) * 100;
    dummy.position.z = (Math.random() - 0.5) * 100;
    dummy.position.y = 0;

    // 随机缩放
    const scale = 0.5 + Math.random() * 1.5;
    dummy.scale.set(scale, scale, scale);

    dummy.updateMatrix();
    instancedMesh.setMatrixAt(i, dummy.matrix);

    // 随机颜色变化
    color.setHSL(0.25 + Math.random() * 0.1, 0.7, 0.3 + Math.random() * 0.2);
    instancedMesh.setColorAt(i, color);
}

instancedMesh.instanceMatrix.needsUpdate = true;
instancedMesh.instanceColor.needsUpdate = true;

scene.add(instancedMesh);
```

### 性能监控

```js
import Stats from 'three/addons/libs/stats.module.js';

const stats = new Stats();
stats.showPanel(0); // 0: fps, 1: ms, 2: mb
document.body.appendChild(stats.dom);

function animate() {
    stats.begin();
    // 渲染代码...
    stats.end();
    requestAnimationFrame(animate);
}
```

---

## 13. 实战场景

### 场景 1：3D 数据可视化仪表盘

```js
// 使用 Three.js 做 3D 柱状图/饼图/地图
// 常见搭配：ECharts GL（内置 Three.js）/ Deck.gl

function createBarChart(data, scene) {
    /**
     * data: [{ label: 'Q1', value: 85 }, { label: 'Q2', value: 92 }, ...]
     */
    const group = new THREE.Group();
    const barWidth = 0.6;
    const spacing = 1.5;
    const maxHeight = 5;

    data.forEach((item, i) => {
        const height = (item.value / 100) * maxHeight;
        const geo = new THREE.BoxGeometry(barWidth, height, barWidth);
        const mat = new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.6 - i * 0.08, 0.8, 0.5),
            roughness: 0.3,
            metalness: 0.2,
        });

        const bar = new THREE.Mesh(geo, mat);
        bar.position.x = (i - data.length / 2 + 0.5) * spacing;
        bar.position.y = height / 2;
        bar.castShadow = true;

        group.add(bar);
    });

    scene.add(group);
    return group;
}
```

### 场景 2：产品 360° 旋转展示

```js
// 基于第 8 章 ProductViewer 类扩展
// 添加颜色/材质切换、截图下载功能

class ProductShowcase360 extends ProductViewer {
    setColor(hex) {
        if (this.model) {
            this.model.traverse(child => {
                if (child.isMesh && child.material.color) {
                    child.material.color.set(hex);
                }
            });
        }
    }

    setWireframe(enable) {
        if (this.model) {
            this.model.traverse(child => {
                if (child.isMesh) {
                    child.material.wireframe = enable;
                }
            });
        }
    }

    takeScreenshot() {
        this.renderer.render(this.scene, this.camera);
        const dataURL = this.renderer.domElement.toDataURL('image/png');
        const link = document.createElement('a');
        link.download = 'product-screenshot.png';
        link.href = dataURL;
        link.click();
    }
}

// 使用
const viewer = new ProductShowcase360(
    document.getElementById('viewer'),
    '/models/product.glb'
);

document.getElementById('btn-red').onclick = () => viewer.setColor('#e74c3c');
document.getElementById('btn-screenshot').onclick = () => viewer.takeScreenshot();
```

### 场景 3：VR 全景看房

```js
// 用球形贴图实现 360° 全景
function createPanorama(imageUrl, scene) {
    const geo = new THREE.SphereGeometry(50, 64, 64);
    const texture = new THREE.TextureLoader().load(imageUrl);
    const mat = new THREE.MeshBasicMaterial({
        map: texture,
        side: THREE.BackSide,  // 内表面可见
    });

    const sphere = new THREE.Mesh(geo, mat);
    sphere.name = 'panorama';
    scene.add(sphere);
    return sphere;
}

// 相机放在球中心，用户看到的就是全景
camera.position.set(0, 0, 0);

// 鼠标拖拽旋转视角
controls.enableZoom = false;
controls.rotateSpeed = -0.5;  // 负值反向：向左拖=向右看
```

### 场景 4：3D 地形可视化

```js
function createTerrain(width, depth, heightFn, scene) {
    const segments = 128;
    const geo = new THREE.PlaneGeometry(width, depth, segments, segments);
    geo.rotateX(-Math.PI / 2);  // 水平放置

    const positions = geo.attributes.position.array;

    for (let i = 0; i < positions.length; i += 3) {
        const x = positions[i];
        const z = positions[i + 2];
        positions[i + 1] = heightFn(x, z);
    }

    // 根据高度着色
    const colors = new Float32Array(positions.length);
    const color = new THREE.Color();

    for (let i = 0; i < positions.length; i += 3) {
        const height = positions[i + 1];
        const t = (height + 5) / 10; // 归一化
        color.setHSL(0.25 - t * 0.2, 0.8, 0.3 + t * 0.5);
        colors[i] = color.r;
        colors[i + 1] = color.g;
        colors[i + 2] = color.b;
    }

    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geo.computeVertexNormals();

    const mat = new THREE.MeshStandardMaterial({
        vertexColors: true,
        roughness: 0.8,
        flatShading: true,
        wireframe: false,
    });

    const terrain = new THREE.Mesh(geo, mat);
    scene.add(terrain);
    return terrain;
}

// 使用：随机山脉地形
createTerrain(20, 20, (x, z) => {
    return Math.sin(x * 0.8) * Math.cos(z * 0.8) * 3
         + Math.sin(x * 2.5 + z * 1.5) * 1.5;
}, scene);
```

---

## 14. 常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 物体不显示 | 相机没对准、没光源（BasicMaterial）、物体在相机后面 | 检查 camera.lookAt、加光源、检查 position |
| 物体全黑 | 用了需要光源的材质但没加灯光 | 加 `AmbientLight` 或换 `MeshBasicMaterial` |
| 纹理不显示 | 路径错误、CORS、图片未加载完 | 检查路径、用绝对路径或 base64、等 `load` 回调 |
| 画面锯齿严重 | 未开抗锯齿 | `WebGLRenderer({ antialias: true })` |
| 拖拽卡顿 | PixelRatio 过高（4K屏） | `setPixelRatio(Math.min(devicePixelRatio, 2))` |
| 模型加载失败 | 路径、CORS、格式不兼容 | 用 glTF 格式、检查 MIME type |
| 阴影缺失 | 未启用阴影 | renderer + light + mesh 三方都要设置 |
| FPS 低 | 几何体过多、draw call 多、阴影太多 | 减少分段、InstancedMesh、关不必要阴影 |
| 动画抖动 | 没用 DeltaTime，帧率不稳 | `const delta = clock.getDelta()` 乘 DeltaTime |
| 透明物体渲染错误 | 渲染顺序问题 | `mesh.renderOrder = 1` + `material.depthWrite = false` |

---

## 速查卡片

### 最小模板

```js
// 场景 + 相机 + 渲染器
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, innerWidth/innerHeight, 0.1, 1000);
camera.position.z = 5;
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);

// 物体
const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(1, 1, 1),
    new THREE.MeshStandardMaterial({ color: 0x00ff88 })
);
scene.add(mesh);
scene.add(new THREE.AmbientLight(0xffffff, 0.5));
scene.add(new THREE.DirectionalLight(0xffffff, 1).position.set(5,5,5));

// 渲染
function animate() {
    requestAnimationFrame(animate);
    mesh.rotation.y += 0.01;
    renderer.render(scene, camera);
}
animate();
```

### 常用 API

```js
// 几何体
new THREE.BoxGeometry(w, h, d)
new THREE.SphereGeometry(r, 32, 16)
new THREE.PlaneGeometry(w, h)
new THREE.CylinderGeometry(rTop, rBottom, h, 32)

// 材质
new THREE.MeshStandardMaterial({ color, roughness, metalness, map })
new THREE.MeshBasicMaterial({ color, map })            // 不受光
new THREE.MeshPhongMaterial({ color, shininess })     // 高光

// 位置/旋转/缩放
mesh.position.set(x, y, z)
mesh.rotation.set(rx, ry, rz)
mesh.scale.set(sx, sy, sz)
mesh.lookAt(target)

// 光照
new THREE.AmbientLight(color, intensity)
new THREE.DirectionalLight(color, intensity)

// 相机
camera.position.set(x, y, z)
camera.lookAt(x, y, z)
```

---

---

## 15. 配置属性速查

### 15.1 WebGLRenderer 渲染器配置

```js
const renderer = new THREE.WebGLRenderer({
    // ===== 画质 =====
    antialias: true,              // 抗锯齿（性能开销中等，推荐开启）
    alpha: false,                  // 背景透明（true=canvas背景可见HTML元素）
    premultipliedAlpha: true,     // 预乘 Alpha（配合 alpha:true）

    // ===== 色彩 =====
    outputColorSpace: THREE.SRGBColorSpace, // 色彩空间（sRGB=标准，Linear-sRGB=线性）
    toneMapping: THREE.ACESFilmicToneMapping, // 色调映射（ACES=电影级，Reinhard=柔和，Cineon=影院）
    toneMappingExposure: 1.0,     // 曝光度（0.5=暗，2.0=亮）

    // ===== 性能 =====
    powerPreference: 'high-performance', // GPU 偏好（high-performance/low-power/default）
    preserveDrawingBuffer: false, // 保留绘制缓冲区（截图用，默认 false 省显存）
    stencil: false,               // 模板缓冲（阴影需要，默认自动开）
    depth: true,                   // 深度缓冲（3D 场景必须开）

    // ===== WebGL =====
    failIfMajorPerformanceCaveat: false, // 软件渲染时是否拒绝创建（生产建议 true）
});

// ===== 运行时设置 =====
renderer.setSize(window.innerWidth, window.innerHeight); // 尺寸
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // 像素比（限制2防4K屏卡顿）
renderer.setClearColor(0x000000, 1); // 背景色（RGBA）
renderer.setClearAlpha(0.5);         // 背景透明度

// ===== 阴影 =====
renderer.shadowMap.enabled = true;                    // 开启阴影
renderer.shadowMap.type = THREE.PCFSoftShadowMap;     // 阴影类型

// shadowMap.type 取值：
// THREE.BasicShadowMap     — 硬阴影（最快，最差）
// THREE.PCFShadowMap        — 软阴影（默认）
// THREE.PCFSoftShadowMap    — 更软的阴影（推荐）
// THREE.VSMShadowMap        — 方差阴影（接地面更柔和）

// ===== 输出编码 =====
renderer.outputColorSpace = THREE.SRGBColorSpace;     // 标准
// renderer.outputColorSpace = THREE.LinearSRGBColorSpace; // 线性
```

### 15.2 Scene 场景属性

```js
const scene = new THREE.Scene();

// 背景
scene.background = new THREE.Color(0x1a1a2e);         // 纯色
scene.background = new THREE.TextureLoader().load('sky.jpg'); // 贴图
scene.background = new THREE.CubeTextureLoader()       // 天空盒
    .setPath('/textures/skybox/')
    .load(['px.jpg','nx.jpg','py.jpg','ny.jpg','pz.jpg','nz.jpg']);

// 雾
scene.fog = new THREE.Fog(0xcccccc, 10, 50);          // 线性雾（颜色, 近, 远）
scene.fog = new THREE.FogExp2(0xcccccc, 0.01);        // 指数雾（颜色, 密度）

// 环境贴图（影响所有 PBR 材质的反射）
scene.environment = new THREE.CubeTextureLoader().load([...]);

// 覆盖材质（调试用，让所有物体变同一种材质）
scene.overrideMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000, wireframe: true });
```

### 15.3 PerspectiveCamera 相机属性

```js
const camera = new THREE.PerspectiveCamera(
    75,                                    // fov：视野角度（人眼约 60°，游戏常用 60-90）
    window.innerWidth / window.innerHeight,// aspect：宽高比（通常用容器宽/高）
    0.1,                                   // near：近裁面（小于此距离看不见）
    1000                                   // far：远裁面（大于此距离看不见）
);

// 运行时调整
camera.position.set(x, y, z);              // 位置
camera.lookAt(targetX, targetY, targetZ);  // 看向目标点
camera.aspect = w / h;                     // 宽高比（窗口大小改变时更新）
camera.updateProjectionMatrix();           // 修改参数后必须调用

// 适配移动端或不同屏幕
camera.fov = isMobile ? 90 : 60;           // 手机屏幕小，加大 FOV

// OrthographicCamera 正交相机参数
new THREE.OrthographicCamera(
    left, right,  // 左右范围
    top, bottom,  // 上下范围
    near, far     // 远近裁面
);
```

### 15.4 Material 材质属性速查表

```js
// ===== MeshStandardMaterial (PBR，最推荐) =====
new THREE.MeshStandardMaterial({
    color: 0xffffff,              // 基础颜色
    roughness: 0.5,               // 粗糙度 (0=镜面, 1=完全粗糙)
    metalness: 0.0,               // 金属感 (0=非金属, 1=纯金属)
    map: texture,                 // 颜色贴图
    normalMap: normalTexture,     // 法线贴图（凹凸细节，不增加顶点）
    roughnessMap: roughTexture,   // 粗糙度贴图（各区域不同粗糙度）
    metalnessMap: metalTexture,   // 金属度贴图
    aoMap: aoTexture,             // 环境光遮蔽贴图（让缝隙更暗）
    displacementMap: dispTexture, // 置换贴图（真正改变几何体顶点）
    displacementScale: 0.2,       // 置换强度
    emissive: 0x000000,           // 自发光颜色
    emissiveIntensity: 0,         // 自发光强度
    emissiveMap: emitTexture,     // 自发光贴图
    alphaMap: alphaTexture,       // 透明度贴图
    transparent: false,           // 是否透明
    opacity: 1.0,                 // 不透明度 (0=全透明, 1=不透明)
    side: THREE.FrontSide,        // 渲染面（FrontSide/BackSide/DoubleSide）
    wireframe: false,             // 线框模式
    flatShading: false,           // 平面着色（低多边形风格）
    depthTest: true,              // 深度测试
    depthWrite: true,             // 深度写入（透明物体通常关）
    dithering: false,             // 颜色抖动（减少色带，性能微小影响）
});

// ===== 材质对比 =====
// MeshBasicMaterial — 不受光照，纯色/贴图
new THREE.MeshBasicMaterial({ color, map, wireframe, transparent, opacity, side, alphaMap });

// MeshPhongMaterial — 镜面高光反射（比 Standard 便宜，画质差些）
new THREE.MeshPhongMaterial({
    color, map, specular: 0x111111, // 高光颜色
    shininess: 30,                   // 高光度 (0-高, 默认30)
    emissive, emissiveIntensity,
    transparent, opacity, side, wireframe,
});

// MeshLambertMaterial — 漫反射，无高光（最便宜的需要光的材质）
new THREE.MeshLambertMaterial({ color, map, emissive, transparent, opacity, side });

// MeshToonMaterial — 卡通风格
new THREE.MeshToonMaterial({ color, map, gradientMap }); // gradientMap 定义色阶

// MeshNormalMaterial — 法线着色（调试用）
new THREE.MeshNormalMaterial({ flatShading, wireframe, side });

// MeshMatcapMaterial — 烘焙光照（不依赖光源，性能极好）
new THREE.MeshMatcapMaterial({ matcap: matcapTexture, flatShading });

// 公共属性
// .color         颜色
// .map           颜色贴图
// .wireframe     线框模式
// .transparent   透明度开关
// .opacity       透明度 (0-1)
// .side          渲染面 (FrontSide/BackSide/DoubleSide)
// .depthTest     深度测试（几乎永远开）
// .depthWrite    深度写入（透明物体关）
// .visible       是否可见
// .flatShading   平面着色
```

### 15.5 纹理属性

```js
const texture = new THREE.TextureLoader().load('path.jpg');

// 重复/偏移/旋转
texture.wrapS = THREE.RepeatWrapping;    // 水平重复模式
texture.wrapT = THREE.RepeatWrapping;    // 垂直重复模式
// 可选值：RepeatWrapping（重复）/ ClampToEdgeWrapping（拉伸边缘）/ MirroredRepeatWrapping（镜像重复）
texture.repeat.set(2, 2);               // 重复次数（需配合 RepeatWrapping）
texture.offset.set(0.5, 0);             // 偏移量（0-1）
texture.rotation = Math.PI / 4;         // 旋转（弧度，绕中心）
texture.center.set(0.5, 0.5);           // 旋转中心点（默认 0,0）

// 颜色空间（影响颜色准确度）
texture.colorSpace = THREE.SRGBColorSpace;      // 颜色贴图（大多数图片是这个）
texture.colorSpace = THREE.LinearSRGBColorSpace; // 数据贴图（法线/粗糙度/金属度）

// 过滤方式
texture.magFilter = THREE.LinearFilter;  // 放大过滤（Linear=平滑, Nearest=像素风）
texture.minFilter = THREE.LinearMipmapLinearFilter; // 缩小过滤（带 Mipmap 的最平滑）

// Mipmap（自动生成不同大小的纹理版本，远处用低分辨率，近处用高分辨率）
texture.generateMipmaps = true;          // 自动生成（默认开）

// 纹理格式（影响内存和画质）
// RGBFormat  /  RGBAFormat  /  RedFormat
texture.format = THREE.RGBAFormat;
texture.type = THREE.UnsignedByteType;   // 每通道 8bit

// 各向异性过滤（斜着看纹理时更清晰，性能开销小，推荐开）
texture.anisotropy = renderer.capabilities.getMaxAnisotropy(); // 最大支持值

// 纹理更新（运行时修改纹理内容后需调用）
texture.needsUpdate = true;
```

### 15.6 Geometry 几何体属性

```js
const geo = new THREE.BoxGeometry(1, 1, 1);

// 可通过属性访问底层数据
geo.attributes.position    // 顶点位置 BufferAttribute
geo.attributes.normal      // 法线方向 BufferAttribute
geo.attributes.uv          // UV 坐标 BufferAttribute
geo.index                  // 索引（面由哪几个顶点组成）

// 计算（修改顶点后需调用）
geo.computeVertexNormals(); // 重新计算法线（修改顶点位置后必须调）
geo.computeBoundingBox();   // 重新计算包围盒
geo.computeBoundingSphere();// 重新计算包围球

// 修改顶点示例：球体变鱼眼效果
const positions = geo.attributes.position;
for (let i = 0; i < positions.count; i++) {
    const x = positions.getX(i);
    const y = positions.getY(i);
    const z = positions.getZ(i);
    const d = Math.sqrt(x*x + y*y + z*z);
    positions.setXYZ(i, x/d, y/d, z/d); // 归一化到球面
}
positions.needsUpdate = true;
geo.computeVertexNormals();
```

### 15.7 Object3D 通用属性（Mesh/Group/Light/Camera 的父类）

```js
// 所有 3D 物体都有这些属性

// ===== 变换 =====
object.position.set(x, y, z);    // 位置
object.position.x = 5;
object.rotation.set(rx, ry, rz); // 旋转（弧度，不是角度！）
object.rotation.order = 'YXZ';   // 旋转顺序（默认 'XYZ'）
object.scale.set(sx, sy, sz);    // 缩放

// ===== 可见性 =====
object.visible = true;            // 是否渲染
object.castShadow = true;         // 投射阴影
object.receiveShadow = true;      // 接收阴影

// ===== 渲染 =====
object.renderOrder = 0;           // 渲染顺序（值越大越后渲染，透明物体用）
object.frustumCulled = true;      // 视锥体剔除（看不到的不渲染，性能优化）
object.matrixAutoUpdate = true;   // 自动更新变换矩阵

// ===== 父子关系 =====
object.add(child);                // 添加子物体（子物体相对父物体变换）
object.remove(child);             // 移除子物体
object.parent                     // 父物体引用
object.children                   // 子物体数组
object.attach(child);             // 添加子物体但保持世界坐标不变

// ===== 工具方法 =====
object.lookAt(x, y, z);                      // 看向目标点
object.lookAt(new THREE.Vector3(x, y, z));   // 向量形式
object.getWorldPosition(targetVector);       // 获取世界坐标
object.getWorldQuaternion(targetQuaternion); // 获取世界旋转
object.traverse(callback);                   // 遍历所有子物体（递归）
object.updateMatrix();                       // 手动更新矩阵
object.updateMatrixWorld();                  // 手动更新世界矩阵

// ===== 命名与查找 =====
object.name = 'myCube';            // 名称
scene.getObjectByName('myCube');   // 按名称查找（遍历所有后代）
scene.getObjectById(id);           // 按 ID 查找
```

### 15.8 Light 光源属性

```js
// ===== 公共属性 =====
const light = new THREE.DirectionalLight(color, intensity);
light.color.set(0xffffff);           // 颜色
light.intensity = 1.5;               // 强度
light.visible = true;                // 开关

// ===== DirectionalLight 平行光（太阳）=====
new THREE.DirectionalLight(0xffffff, 1);
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 1024;   // 阴影贴图分辨率
directionalLight.shadow.mapSize.height = 1024;
directionalLight.shadow.camera.near = 0.5;      // 阴影相机的近裁面
directionalLight.shadow.camera.far = 50;        // 阴影相机的远裁面
directionalLight.shadow.camera.left = -10;      // 阴影相机的范围
directionalLight.shadow.camera.right = 10;
directionalLight.shadow.camera.top = 10;
directionalLight.shadow.camera.bottom = -10;
directionalLight.shadow.bias = -0.0005;         // 阴影偏移（消除阴影条纹）
directionalLight.shadow.normalBias = 0.02;      // 法线偏移

// ===== PointLight 点光源（灯泡）=====
new THREE.PointLight(0xff0000, 1, 10, 1);     // 颜色, 强度, 距离, 衰减
pointLight.decay = 2;                // 衰减系数（2=物理正确平方反比）

// ===== SpotLight 聚光灯（手电筒）=====
new THREE.SpotLight(0xffffff, 2, 20, Math.PI/6, 0.3, 1);
// 颜色, 强度, 距离, 角度, 半影衰减, 衰减
spotLight.angle = Math.PI / 6;       // 光束角度
spotLight.penumbra = 0.3;            // 边缘柔和度 (0=硬边, 1=最软)
spotLight.target.position.set(x,y,z);// 照射目标点
scene.add(spotLight.target);         // target 也要加入场景

// ===== HemisphereLight 半球光（户外环境）=====
new THREE.HemisphereLight(skyColor, groundColor, intensity);
// skyColor：天空色（照上方）
// groundColor：地面色（照下方）

// ===== 光照助手（开发调试用）=====
scene.add(new THREE.DirectionalLightHelper(directionalLight, 1)); // 平行光可视化
scene.add(new THREE.PointLightHelper(pointLight, 0.5));           // 点光源可视化
scene.add(new THREE.SpotLightHelper(spotLight));                  // 聚光灯可视化
scene.add(new THREE.CameraHelper(directionalLight.shadow.camera)); // 阴影相机范围
```

### 15.9 Controls 控制器属性

```js
// OrbitControls 轨道控制器
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const controls = new OrbitControls(camera, renderer.domElement);

// ===== 交互开关 =====
controls.enableDamping = true;        // 惯性阻尼
controls.dampingFactor = 0.05;        // 阻尼系数（越小惯性越大）
controls.enableRotate = true;         // 允许旋转
controls.enableZoom = true;           // 允许缩放
controls.enablePan = true;            // 允许平移
controls.autoRotate = true;           // 自动旋转
controls.autoRotateSpeed = 1.0;       // 自动旋转速度

// ===== 旋转限制 =====
controls.minAzimuthAngle = -Infinity; // 水平最小角度
controls.maxAzimuthAngle = Infinity;  // 水平最大角度
controls.minPolarAngle = 0;           // 垂直最小角度（0=正上方）
controls.maxPolarAngle = Math.PI;     // 垂直最大角度（PI=正下方）

// ===== 缩放限制 =====
controls.minDistance = 1;             // 最小缩放距离
controls.maxDistance = 50;            // 最大缩放距离
controls.zoomSpeed = 1.0;             // 缩放速度

// ===== 平移/旋转速度 =====
controls.rotateSpeed = 1.0;           // 旋转灵敏度
controls.panSpeed = 1.0;              // 平移灵敏度

// ===== 键盘控制 =====
controls.keyPanSpeed = 7.0;           // 键盘平移速度
controls.keys = {
    LEFT: 'ArrowLeft', RIGHT: 'ArrowRight',
    UP: 'ArrowUp', BOTTOM: 'ArrowDown',
};

// ===== 其他 =====
controls.target.set(0, 0, 0);         // 旋转中心
controls.update();                     // 修改参数后调用
controls.saveState();                  // 保存当前状态
controls.reset();                      // 恢复到上次保存的状态
controls.dispose();                    // 销毁控制器（移除事件监听）
```

### 15.10 Raycaster 射线检测属性

```js
const raycaster = new THREE.Raycaster();

// ===== 配置 =====
raycaster.far = Infinity;               // 检测最大距离
raycaster.near = 0;                     // 检测最小距离

// ===== 检测方法 =====
raycaster.setFromCamera(mouse, camera); // 从相机发出一条经过鼠标位置的射线
raycaster.intersectObjects(objects);    // 检测是否与物体列表相交（无序）
raycaster.intersectObjects(objects, true); // true=递归检测子物体
raycaster.intersectObject(object);      // 检测单个物体

// ===== 返回结果 [ { object, point, distance, face, uv, ... } ] =====
const intersects = raycaster.intersectObjects(meshes);
if (intersects.length > 0) {
    const hit = intersects[0];
    console.log('点击物体:', hit.object.name);
    console.log('碰撞点坐标:', hit.point);       // Vector3 世界坐标
    console.log('碰撞距离:', hit.distance);       // 从相机到碰撞点
    console.log('碰撞的面索引:', hit.faceIndex);   // 三角形面的索引
    console.log('UV 坐标:', hit.uv);              // 贴图坐标
}
```

### 15.11 动画与时钟

```js
// Clock 时钟（获取精确时间差）
const clock = new THREE.Clock();

function animate() {
    const delta = clock.getDelta();       // 上一次调用到现在的秒数
    const elapsed = clock.getElapsedTime(); // 始终启动以来的总秒数

    // 恒速旋转（不受帧率影响）
    cube.rotation.y += delta * Math.PI / 2; // 每秒转半圈（与帧率无关）

    // 振荡运动
    cube.position.y = Math.sin(elapsed * 2) * 0.5;

    renderer.render(scene, camera);
    requestAnimationFrame(animate);
}

// AnimationMixer（播放 glTF/FBX 等模型的骨骼动画）
import { AnimationMixer } from 'three';

const mixer = new AnimationMixer(gltf.scene);
const action = mixer.clipAction(gltf.animations[0]); // 取第一个动画片段

// 播放控制
action.play();                          // 播放
action.stop();                          // 停止
action.paused = false;                  // 暂停/恢复
action.timeScale = 1.5;                 // 播放速度（1.5倍速）
action.loop = THREE.LoopRepeat;         // 循环模式
// LoopOnce（一次）/ LoopRepeat（循环）/ LoopPingPong（往返）

action.setDuration(2);                  // 设置持续时间（秒）
action.crossFadeTo(otherAction, 0.5);   // 渐变切换到另一个动画（0.5秒过渡）
action.weight = 1;                      // 动画权重（0-1，混合动画用）

// 渲染循环中更新
function animate() {
    const delta = clock.getDelta();
    mixer.update(delta);                // 更新动画
    renderer.render(scene, camera);
}
```

### 15.12 辅助调试工具

```js
// ===== 轴辅助线 =====
scene.add(new THREE.AxesHelper(5));     // RGB = XYZ，长度 5

// ===== 地面网格 =====
scene.add(new THREE.GridHelper(10, 10)); // 大小10×10，10个格子

// ===== 包围盒 =====
const box = new THREE.BoxHelper(mesh, 0xff0000);
box.update();                           // 更新包围盒
scene.add(box);

// ===== 法线可视化 =====
scene.add(new THREE.VertexNormalsHelper(mesh, 0.2, 0x00ff00));

// ===== 骨骼辅助 =====
scene.add(new THREE.SkeletonHelper(skinnedMesh));

// ===== 阴影相机范围 =====
scene.add(new THREE.CameraHelper(directionalLight.shadow.camera));

// ===== 点光源范围球 =====
scene.add(new THREE.PointLightHelper(pointLight, 0.5));

// ===== 性能监控（FPS/MS/MB）=====
import Stats from 'three/addons/libs/stats.module.js';
const stats = new Stats();
stats.showPanel(0);                     // 0:FPS, 1:每帧毫秒, 2:内存
document.body.appendChild(stats.dom);
// 渲染循环中：stats.begin() ... stats.end()

// ===== 渲染信息（draw calls、三角形、点数）=====
console.log(renderer.info.render);       // { calls, triangles, points, ... }
```

### 15.13 加载器属性

```js
// ===== TextureLoader 纹理加载器 =====
const texLoader = new THREE.TextureLoader();
texLoader.setCrossOrigin('anonymous');  // 跨域
texLoader.setPath('/textures/');        // 基础路径

// ===== GLTFLoader =====
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const gltfLoader = new GLTFLoader();
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/v1/decoders/');
dracoLoader.setDecoderConfig({ type: 'js' });  // js 或 wasm
gltfLoader.setDRACOLoader(dracoLoader);

// ===== CubeTextureLoader 天空盒加载器 =====
const cubeLoader = new THREE.CubeTextureLoader();
cubeLoader.setPath('/textures/skybox/');
const skybox = cubeLoader.load(['px.jpg','nx.jpg','py.jpg','ny.jpg','pz.jpg','nz.jpg']);

// ===== AudioListener / AudioLoader 音频 =====
const listener = new THREE.AudioListener();
camera.add(listener);
new THREE.AudioLoader().load('bgm.mp3', (buffer) => {
    const sound = new THREE.Audio(listener);
    sound.setBuffer(buffer);
    sound.setVolume(0.5);
    sound.setLoop(true);
    sound.play();
});

// ===== LoadingManager 统一管理加载进度 =====
import { LoadingManager } from 'three';
const manager = new LoadingManager();

manager.onStart = (url, itemsLoaded, itemsTotal) => {
    console.log(`开始加载: ${url}`);
};
manager.onProgress = (url, itemsLoaded, itemsTotal) => {
    const pct = Math.round(itemsLoaded / itemsTotal * 100);
    console.log(`加载进度: ${pct}%`);
};
manager.onLoad = () => console.log('全部加载完成！');
manager.onError = (url) => console.error(`加载失败: ${url}`);

// 所有加载器共享同一个 manager
const texLoader = new THREE.TextureLoader(manager);
const gltfLoader = new GLTFLoader(manager);
```

### 15.14 数学工具速查

```js
// ===== Vector3 三维向量 =====
const v = new THREE.Vector3(1, 2, 3);
v.set(4, 5, 6);
v.x = 7;
v.length();                             // 向量长度
v.normalize();                          // 归一化（长度变为1）
v.distanceTo(other);                    // 到另一个点的距离
v.add(other).multiplyScalar(2);         // 链式调用
v.clone();                              // 深拷贝
v.copy(other);                          // 复制值
v.dot(other);                           // 点积（判断方向）
v.cross(other);                         // 叉积（求法线）

// ===== Euler 欧拉角 =====
const euler = new THREE.Euler(x, y, z, 'YXZ');
// 旋转顺序默认 'XYZ'，常用 'YXZ'（Yaw-Pitch-Roll）

// ===== Quaternion 四元数 =====
const quat = new THREE.Quaternion();
object.quaternion.copy(quat);

// ===== Color 颜色 =====
const color = new THREE.Color();
color.set(0xff0000);                    // 十六进制
color.set('#ff0000');                    // CSS 字符串
color.set('rgb(255, 0, 0)');            // CSS RGB
color.setHSL(0, 1, 0.5);                // HSL（色相0-1, 饱和度, 明度）
color.setScalar(0.5);                   // 灰度（0=黑, 1=白）

// ===== MathUtils 工具 =====
THREE.MathUtils.radToDeg(rad);          // 弧度→角度
THREE.MathUtils.degToRad(deg);          // 角度→弧度
THREE.MathUtils.clamp(value, min, max); // 限制范围
THREE.MathUtils.lerp(a, b, t);          // 线性插值
THREE.MathUtils.randFloat(min, max);     // 随机浮点
THREE.MathUtils.randFloatSpread(range); // 随机浮点（散布）
THREE.MathUtils.randInt(min, max);       // 随机整数
THREE.MathUtils.smoothstep(edge0, edge1, x); // 平滑过渡
```

---

> **Three.js 最核心的公式：Scene + Camera + Renderer = 3D 世界。每个物体 = Geometry（形状）+ Material（材质）= Mesh（网格）。理解了这 5 个概念，就掌握了 Three.js 的骨架。**
