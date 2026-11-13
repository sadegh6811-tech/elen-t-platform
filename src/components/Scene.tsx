import { useEffect, useMemo, useRef } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Stars } from "@react-three/drei";
import * as THREE from "three";

type PointerRef = React.MutableRefObject<{ x: number; y: number; moved: number }>;

function usePointer(): PointerRef {
  const pointer = useRef({ x: 0, y: 0, moved: 0 });
  useEffect(() => {
    const update = (clientX: number, clientY: number) => {
      pointer.current.x = (clientX / window.innerWidth) * 2 - 1;
      pointer.current.y = -((clientY / window.innerHeight) * 2 - 1);
      pointer.current.moved = performance.now();
    };
    const onMouse = (e: MouseEvent) => update(e.clientX, e.clientY);
    const onTouch = (e: TouchEvent) => {
      const t = e.touches[0];
      if (t) update(t.clientX, t.clientY);
    };
    window.addEventListener("mousemove", onMouse, { passive: true });
    window.addEventListener("touchmove", onTouch, { passive: true });
    window.addEventListener("touchstart", onTouch, { passive: true });
    return () => {
      window.removeEventListener("mousemove", onMouse);
      window.removeEventListener("touchmove", onTouch);
      window.removeEventListener("touchstart", onTouch);
    };
  }, []);
  return pointer;
}

function FrameDriver({ fps, pointer, reducedMotion }: { fps: number; pointer: PointerRef; reducedMotion: boolean }) {
  const invalidate = useThree((s) => s.invalidate);
  useEffect(() => {
    let raf = 0;
    let last = 0;
    const interval = 1000 / fps;
    const loop = (t: number) => {
      raf = requestAnimationFrame(loop);
      if (document.hidden) return;
      if (reducedMotion && t - pointer.current.moved > 1500) return;
      if (t - last >= interval) {
        last = t - ((t - last) % interval);
        invalidate();
      }
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [fps, invalidate, pointer, reducedMotion]);
  return null;
}

function ParticleShell({ count, radius }: { count: number; radius: number }) {
  const ref = useRef<THREE.Points>(null);
  const { positions, colors } = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const cyan = new THREE.Color("#22d3ee");
    const purple = new THREE.Color("#a855f7");
    const blue = new THREE.Color("#3b82f6");
    const golden = Math.PI * (3 - Math.sqrt(5));
    const tmp = new THREE.Color();
    for (let i = 0; i < count; i++) {
      const y = 1 - (i / (count - 1)) * 2;
      const r = Math.sqrt(1 - y * y);
      const theta = golden * i;
      const jitter = radius * (1 + (Math.random() - 0.5) * 0.08);
      positions[i * 3] = Math.cos(theta) * r * jitter;
      positions[i * 3 + 1] = y * jitter;
      positions[i * 3 + 2] = Math.sin(theta) * r * jitter;
      const mix = (y + 1) / 2;
      tmp.copy(cyan).lerp(purple, mix);
      if (Math.random() > 0.85) tmp.lerp(blue, 0.6);
      colors[i * 3] = tmp.r;
      colors[i * 3 + 1] = tmp.g;
      colors[i * 3 + 2] = tmp.b;
    }
    return { positions, colors };
  }, [count, radius]);

  useFrame((_, delta) => {
    if (!ref.current) return;
    ref.current.rotation.y -= delta * 0.05;
    ref.current.rotation.z += delta * 0.02;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-color" args={[colors, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.035} vertexColors transparent opacity={0.85} depthWrite={false} blending={THREE.AdditiveBlending} sizeAttenuation />
    </points>
  );
}

function OrbitRing({ radius, color, tilt, speed }: { radius: number; color: string; tilt: [number, number, number]; speed: number; }) {
  const ref = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => {
    if (ref.current) ref.current.rotation.z += delta * speed;
  });
  return (
    <group rotation={tilt}>
      <mesh ref={ref}>
        <torusGeometry args={[radius, 0.006, 6, 160]} />
        <meshBasicMaterial color={color} transparent opacity={0.55} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
    </group>
  );
}

function AICore({ pointer, isMobile }: { pointer: PointerRef; isMobile: boolean }) {
  const root = useRef<THREE.Group>(null);
  const outer = useRef<THREE.LineSegments>(null);
  const inner = useRef<THREE.Mesh>(null);
  const nucleus = useRef<THREE.Mesh>(null);
  const halo = useRef<THREE.Mesh>(null);

  const outerEdges = useMemo(() => new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(1.6, 1)), []);
  const midEdges = useMemo(() => new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(1.15, 0)), []);

  useEffect(() => () => {
    outerEdges.dispose();
    midEdges.dispose();
  }, [outerEdges, midEdges]);

  useFrame((state, delta) => {
    const t = state.clock.elapsedTime;
    const d = Math.min(delta, 0.1);
    if (root.current) {
      const targetX = pointer.current.y * 0.45;
      const targetY = pointer.current.x * 0.6;
      root.current.rotation.x = THREE.MathUtils.damp(root.current.rotation.x, targetX, 2.5, d);
      root.current.rotation.y = THREE.MathUtils.damp(root.current.rotation.y, targetY, 2.5, d);
      root.current.position.y = Math.sin(t * 0.6) * 0.08;
    }
    if (outer.current) {
      outer.current.rotation.y += d * 0.12;
      outer.current.rotation.x += d * 0.05;
    }
    if (inner.current) {
      inner.current.rotation.y -= d * 0.25;
      inner.current.rotation.z += d * 0.1;
    }
    if (nucleus.current) {
      const s = 1 + Math.sin(t * 2.2) * 0.06;
      nucleus.current.scale.setScalar(s);
    }
    if (halo.current) {
      const m = halo.current.material as THREE.MeshBasicMaterial;
      m.opacity = 0.08 + Math.sin(t * 1.4) * 0.03;
    }
  });

  return (
    <group ref={root} position={isMobile ? [0, 0.4, 0] : [0, 0, 0]} scale={isMobile ? 0.8 : 1}>
      <lineSegments ref={outer} geometry={outerEdges}>
        <lineBasicMaterial color="#22d3ee" transparent opacity={0.7} blending={THREE.AdditiveBlending} />
      </lineSegments>
      <mesh ref={inner}>
        <icosahedronGeometry args={[1.15, 0]} />
        <meshBasicMaterial color="#6d28d9" transparent opacity={0.12} depthWrite={false} />
        <lineSegments geometry={midEdges}>
          <lineBasicMaterial color="#a855f7" transparent opacity={0.85} blending={THREE.AdditiveBlending} />
        </lineSegments>
      </mesh>
      <mesh ref={nucleus}>
        <sphereGeometry args={[0.32, 24, 24]} />
        <meshBasicMaterial color="#67e8f9" />
      </mesh>
      <mesh ref={halo}>
        <sphereGeometry args={[0.7, 24, 24]} />
        <meshBasicMaterial color="#22d3ee" transparent opacity={0.1} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
      <ParticleShell count={isMobile ? 900 : 2200} radius={2.3} />
      <OrbitRing radius={2.0} color="#22d3ee" tilt={[Math.PI / 2.3, 0, 0]} speed={0.3} />
      <OrbitRing radius={2.65} color="#a855f7" tilt={[Math.PI / 3, Math.PI / 5, 0]} speed={-0.2} />
      <OrbitRing radius={3.1} color="#3b82f6" tilt={[Math.PI / 1.8, -Math.PI / 6, 0]} speed={0.12} />
    </group>
  );
}

export interface SceneProps { fps?: number; className?: string; }

export default function Scene({ fps, className = "" }: SceneProps) {
  const pointer = usePointer();
  const { isMobile, reducedMotion } = useMemo(() => {
    if (typeof window === "undefined") return { isMobile: false, reducedMotion: false };
    return {
      isMobile: window.matchMedia("(max-width: 1023px)").matches || window.matchMedia("(pointer: coarse)").matches,
      reducedMotion: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    };
  }, []);
  const targetFps = fps ?? (isMobile ? 30 : 60);

  return (
    <div aria-hidden className={`pointer-events-none fixed inset-0 ${className}`} style={{ zIndex: -1, background: "radial-gradient(ellipse at 50% 40%, #0b1a3a 0%, #070b1f 45%, #02030a 100%)" }}>
      <Canvas frameloop="demand" dpr={[1, isMobile ? 1.5 : 2]} camera={{ position: [0, 0, 7], fov: 50, near: 0.1, far: 100 }} gl={{ antialias: !isMobile, alpha: true, powerPreference: "high-performance" }} style={{ pointerEvents: "none" }}>
        <fog attach="fog" args={["#02030a", 8, 18]} />
        <FrameDriver fps={targetFps} pointer={pointer} reducedMotion={reducedMotion} />
        <AICore pointer={pointer} isMobile={isMobile} />
        <Stars radius={40} depth={30} count={isMobile ? 800 : 2000} factor={3} saturation={0.6} fade speed={0.6} />
      </Canvas>
      <div className="cyber-grid absolute inset-0 opacity-60" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,rgba(2,3,10,0.85)_100%)]" />
    </div>
  );
}
