'use client'; // ← این خط برای Next.js حیاتی است

import { Canvas, useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

const PAIRS = 34;

function Helix() {
  const group = useRef<THREE.Group>(null!);
  const nodes = useMemo(() => {
    const arr: { a: THREE.Vector3; b: THREE.Vector3; i: number }[] = [];
    for (let i = 0; i < PAIRS; i++) {
      const t = i * 0.42;
      const y = (i - PAIRS / 2) * 0.24;
      arr.push({
        a: new THREE.Vector3(Math.cos(t) * 1.3, y, Math.sin(t) * 1.3),
        b: new THREE.Vector3(Math.cos(t + Math.PI) * 1.3, y, Math.sin(t + Math.PI) * 1.3),
        i,
      });
    }
    return arr;
  }, []);

  useFrame((state, dt) => {
    const g = group.current;
    if (!g) return;
    g.rotation.y += dt * 0.35;
    const { x, y } = state.pointer;
    g.rotation.x = THREE.MathUtils.lerp(g.rotation.x, -y * 0.4, 0.05);
    g.rotation.z = THREE.MathUtils.lerp(g.rotation.z, 0.35 + x * 0.3, 0.05);
    g.position.x = THREE.MathUtils.lerp(g.position.x, x * 0.4, 0.05);
    g.children.forEach((c, idx) => {
      const s = 1 + Math.sin(state.clock.elapsedTime * 2 + idx * 0.3) * 0.15;
      if ((c as any).userData.pulse) c.scale.setScalar(s);
    });
  });

  return (
    <group ref={group} rotation={[0, 0, 0.35]}>
      {nodes.map(({ a, b, i }) => {
        const mid = a.clone().add(b).multiplyScalar(0.5);
        const len = a.distanceTo(b);
        const dir = b.clone().sub(a).normalize();
        const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
        return (
          <group key={i}>
            <mesh position={a} userData={{ pulse: true }}>
              <sphereGeometry args={[0.1, 16, 16]} />
              <meshStandardMaterial color="#22d3ee" emissive="#06b6d4" emissiveIntensity={2} />
            </mesh>
            <mesh position={b} userData={{ pulse: true }}>
              <sphereGeometry args={[0.1, 16, 16]} />
              <meshStandardMaterial color="#4ade80" emissive="#22c55e" emissiveIntensity={2} />
            </mesh>
            <mesh position={mid} quaternion={q}>
              <cylinderGeometry args={[0.018, 0.018, len, 6]} />
              <meshStandardMaterial color="#2dd4bf" emissive="#14b8a6" emissiveIntensity={0.8} transparent opacity={0.55} />
            </mesh>
          </group>
        );
      })}
    </group>
  );
}

function Particles() {
  const ref = useRef<THREE.Points>(null!);
  const positions = useMemo(() => {
    const p = new Float32Array(600 * 3);
    for (let i = 0; i < p.length; i++) p[i] = (Math.random() - 0.5) * 14;
    return p;
  }, []);
  useFrame((_, dt) => { if (ref.current) ref.current.rotation.y -= dt * 0.03; });
  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.03} color="#38bdf8" transparent opacity={0.7} />
    </points>
  );
}

export default function DNAScene() {
  return (
    <Canvas camera={{ position: [0, 0, 8], fov: 50 }} dpr={[1, 2]} gl={{ alpha: true, antialias: true }}>
      <ambientLight intensity={0.4} />
      <pointLight position={[5, 5, 5]} intensity={40} color="#38bdf8" />
      <pointLight position={[-5, -3, 2]} intensity={30} color="#4ade80" />
      <Helix />
      <Particles />
    </Canvas>
  );
}
