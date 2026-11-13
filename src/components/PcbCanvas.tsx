import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export const PcbCanvas: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    // Concurrency check for low-end hardware
    const concurrency = typeof navigator !== 'undefined' ? navigator.hardwareConcurrency || 4 : 4;
    const partsCount = concurrency < 4 ? 8 : 14;

    // Reduced motion preference check
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Dimensions
    const width = container.clientWidth || 600;
    const height = container.clientHeight || 400;

    // Scene
    const scene = new THREE.Scene();

    // Camera
    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 100);
    camera.position.set(0, 3, 6);
    camera.lookAt(0, 0, 0);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(width, height);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    container.appendChild(renderer.domElement);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    // Moving Cyan PointLight
    const movingCyanLight = new THREE.PointLight(0x00d4d4, 3, 8);
    movingCyanLight.position.set(0, 0.4, 0);
    scene.add(movingCyanLight);

    // Light 2 (Orange Accent)
    const orangePointLight = new THREE.PointLight(0xff8c42, 2.2, 10);
    orangePointLight.position.set(3, 2, -2);
    scene.add(orangePointLight);

    // Light 3 (Soft white fill)
    const softWhiteLight = new THREE.PointLight(0xe2e8f0, 1.2, 8);
    softWhiteLight.position.set(-2, 3, 2);
    scene.add(softWhiteLight);

    // Main Group for interactive rotation
    const pcbGroup = new THREE.Group();
    scene.add(pcbGroup);

    // Abstract PCB Board: BoxGeometry(4, 0.1, 3)
    const boardGeo = new THREE.BoxGeometry(4, 0.1, 3);
    const boardMat = new THREE.MeshPhysicalMaterial({
      color: 0x0c121e,
      roughness: 0.28,
      metalness: 0.25,
      clearcoat: 0.9,
      clearcoatRoughness: 0.15
    });
    const boardMesh = new THREE.Mesh(boardGeo, boardMat);
    pcbGroup.add(boardMesh);

    // Add copper trace patterns on the PCB surface
    const traceMatCyan = new THREE.MeshBasicMaterial({ color: 0x00d4d4, transparent: true, opacity: 0.4 });
    const traceMatOrange = new THREE.MeshBasicMaterial({ color: 0xff8c42, transparent: true, opacity: 0.35 });

    const traceGeos: THREE.Mesh[] = [];
    const tracesConfig = [
      { x: -1.2, z: -0.6, w: 1.2, h: 0.04, mat: traceMatCyan },
      { x: 0.8, z: 0.5, w: 1.5, h: 0.04, mat: traceMatOrange },
      { x: -0.5, z: 0.8, w: 0.04, h: 0.9, mat: traceMatCyan },
      { x: 1.2, z: -0.4, w: 0.04, h: 1.2, mat: traceMatCyan }
    ];

    tracesConfig.forEach((tr) => {
      const plane = new THREE.Mesh(new THREE.PlaneGeometry(tr.w, tr.h), tr.mat);
      plane.rotation.x = -Math.PI / 2;
      plane.position.set(tr.x, 0.052, tr.z);
      pcbGroup.add(plane);
      traceGeos.push(plane);
    });

    // Parts definitions on PCB (12-15 parts or 8 on lower concurrency)
    const chipGeo = new THREE.BoxGeometry(0.65, 0.12, 0.65);
    const mcuMat = new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.3, metalness: 0.8 });
    
    // Main MCU chip in the middle-left
    const mainMcu = new THREE.Mesh(chipGeo, mcuMat);
    mainMcu.position.set(-0.9, 0.11, -0.3);
    pcbGroup.add(mainMcu);

    // Colorful accent materials
    const cyanPartMat = new THREE.MeshStandardMaterial({ color: 0x00d4d4, roughness: 0.2, metalness: 0.5 });
    const orangePartMat = new THREE.MeshStandardMaterial({ color: 0xff8c42, roughness: 0.3, metalness: 0.4 });
    const grayPartMat = new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.5, metalness: 0.6 });
    const darkGrayMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4, metalness: 0.7 });

    const partsMeshList: THREE.Mesh[] = [];

    // Predefined component positions on 4x3 surface
    const componentSpecs = [
      { type: 'box', size: [0.7, 0.25, 0.4], pos: [1.1, 0.17, -0.8], mat: orangePartMat }, // Relay
      { type: 'cyl', size: [0.18, 0.18, 0.4], pos: [0.4, 0.25, -0.9], mat: cyanPartMat }, // Cap
      { type: 'cyl', size: [0.16, 0.16, 0.35], pos: [0.1, 0.22, -0.9], mat: grayPartMat }, // Cap
      { type: 'box', size: [0.35, 0.08, 0.25], pos: [-1.4, 0.09, 0.6], mat: orangePartMat }, // LDO
      { type: 'box', size: [0.4, 0.08, 0.25], pos: [-0.9, 0.09, 0.8], mat: cyanPartMat }, // IC
      { type: 'box', size: [0.5, 0.22, 0.35], pos: [1.2, 0.16, 0.2], mat: darkGrayMat }, // Transformer
      { type: 'box', size: [0.3, 0.08, 0.3], pos: [0.6, 0.09, 0.9], mat: grayPartMat }, // Sensor
      { type: 'cyl', size: [0.12, 0.12, 0.3], pos: [1.4, 0.2, 0.8], mat: cyanPartMat }, // Cap
      { type: 'box', size: [0.25, 0.06, 0.15], pos: [-0.2, 0.08, -0.2], mat: orangePartMat }, // Resistor pack
      { type: 'box', size: [0.25, 0.06, 0.15], pos: [-0.2, 0.08, 0.1], mat: cyanPartMat },
      { type: 'box', size: [0.4, 0.1, 0.2], pos: [-1.4, 0.1, -1.0], mat: darkGrayMat },
      { type: 'box', size: [0.2, 0.06, 0.2], pos: [0.5, 0.08, -0.2], mat: grayPartMat },
      { type: 'cyl', size: [0.14, 0.14, 0.28], pos: [-0.5, 0.19, -0.9], mat: orangePartMat },
      { type: 'box', size: [0.3, 0.08, 0.18], pos: [0.9, 0.09, -0.2], mat: cyanPartMat }
    ];

    const activeSpecs = componentSpecs.slice(0, partsCount);

    activeSpecs.forEach((spec) => {
      let mesh: THREE.Mesh;
      if (spec.type === 'cyl') {
        const [rt, rb, h] = spec.size;
        const geo = new THREE.CylinderGeometry(rt, rb, h, 16);
        mesh = new THREE.Mesh(geo, spec.mat);
      } else {
        const [w, h, d] = spec.size;
        const geo = new THREE.BoxGeometry(w, h, d);
        mesh = new THREE.Mesh(geo, spec.mat);
      }
      mesh.position.set(spec.pos[0], spec.pos[1], spec.pos[2]);
      pcbGroup.add(mesh);
      partsMeshList.push(mesh);
    });

    // Slight initial tilt so it looks perspective-rich
    pcbGroup.rotation.x = 0.25;

    // Interaction handlers
    let targetRotationY = 0;
    let targetRotationX = 0.25;
    let isInteracting = false;
    let startX = 0;
    let startY = 0;

    const handlePointerDown = (e: PointerEvent) => {
      isInteracting = true;
      startX = e.clientX;
      startY = e.clientY;
    };

    const handlePointerMove = (e: PointerEvent) => {
      if (!isInteracting) {
        // subtle hover parallax
        const rect = container.getBoundingClientRect();
        const normX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        const normY = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
        targetRotationY = normX * 0.4;
        targetRotationX = 0.25 - normY * 0.15;
      } else {
        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;
        targetRotationY += deltaX * 0.006;
        targetRotationX = Math.max(0.05, Math.min(0.65, targetRotationX + deltaY * 0.004));
        startX = e.clientX;
        startY = e.clientY;
      }
    };

    const handlePointerUp = () => {
      isInteracting = false;
    };

    container.addEventListener('pointerdown', handlePointerDown);
    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', handlePointerUp);

    // Animation loop
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      if (prefersReducedMotion) {
        renderer.render(scene, camera);
        return;
      }

      animationFrameId = requestAnimationFrame(animate);

      const elapsedTime = clock.getElapsedTime();

      // Gentle continuous rotation in Y (0.003 rad/frame) + smooth lerp to target
      if (!isInteracting) {
        pcbGroup.rotation.y += 0.003;
      } else {
        pcbGroup.rotation.y += (targetRotationY - pcbGroup.rotation.y) * 0.1;
      }
      pcbGroup.rotation.x += (targetRotationX - pcbGroup.rotation.x) * 0.05;

      // Cyan PointLight moves gently across the surface
      movingCyanLight.position.x = Math.sin(elapsedTime * 0.9) * 1.6;
      movingCyanLight.position.z = Math.cos(elapsedTime * 0.7) * 1.1;
      movingCyanLight.position.y = 0.35 + Math.sin(elapsedTime * 1.5) * 0.1;

      renderer.render(scene, camera);
    };

    // If reduced motion is requested, just render one frame without looping
    if (prefersReducedMotion) {
      renderer.render(scene, camera);
    } else {
      animate();
    }

    // ResizeObserver
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const newW = entry.contentRect.width;
        const newH = entry.contentRect.height;
        if (newW > 0 && newH > 0) {
          camera.aspect = newW / newH;
          camera.updateProjectionMatrix();
          renderer.setSize(newW, newH);
          if (prefersReducedMotion) {
            renderer.render(scene, camera);
          }
        }
      }
    });
    resizeObserver.observe(container);

    // Cleanup
    return () => {
      cancelAnimationFrame(animationFrameId);
      resizeObserver.disconnect();
      container.removeEventListener('pointerdown', handlePointerDown);
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerUp);

      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }

      // Dispose Geometries and Materials
      boardGeo.dispose();
      boardMat.dispose();
      chipGeo.dispose();
      mcuMat.dispose();
      cyanPartMat.dispose();
      orangePartMat.dispose();
      grayPartMat.dispose();
      darkGrayMat.dispose();
      traceMatCyan.dispose();
      traceMatOrange.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={mountRef}
      className="w-full h-full min-h-[300px] sm:min-h-[420px] relative touch-none cursor-grab active:cursor-grabbing"
      aria-label="3D Interactive PCB"
    />
  );
};
