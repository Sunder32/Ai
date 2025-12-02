/* eslint-disable react/no-unknown-property */
import React, { useEffect, useRef, useState } from 'react';
import { Canvas, extend, useFrame } from '@react-three/fiber';
import { Environment, Lightformer } from '@react-three/drei';
import {
  BallCollider,
  CuboidCollider,
  Physics,
  RigidBody,
  useRopeJoint,
  useSphericalJoint,
  RigidBodyProps
} from '@react-three/rapier';
import { MeshLineGeometry, MeshLineMaterial } from 'meshline';
import * as THREE from 'three';
import { FaUser, FaTimes } from 'react-icons/fa';

extend({ MeshLineGeometry, MeshLineMaterial });

interface LanyardTooltipProps {
  buttonText?: string;
  buttonClassName?: string;
}

export default function LanyardTooltip({
  buttonText = 'Профиль',
  buttonClassName = ''
}: LanyardTooltipProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      {/* Кнопка-триггер */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`group relative px-4 py-2 rounded-xl font-semibold text-white transition-all duration-300 hover:scale-105 ${buttonClassName}`}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl transition-opacity group-hover:opacity-90"></div>
        <div className="relative flex items-center gap-2">
          {React.createElement(FaUser as any, { className: "text-lg" })}
          <span>{buttonText}</span>
        </div>
      </button>

      {/* Выпадающая подсказка */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Оверлей с размытием */}
          <div
            className="absolute inset-0 backdrop-blur-md bg-black/50"
            onClick={() => setIsOpen(false)}
          />

          {/* Контейнер карточки */}
          <div className="relative z-10 backdrop-blur-xl bg-white/5 rounded-3xl border border-white/10 p-8 max-w-4xl w-full mx-4 shadow-2xl">
            {/* Кнопка закрытия */}
            <button
              onClick={() => setIsOpen(false)}
              className="absolute top-4 right-4 p-2 rounded-xl bg-white/5 border border-white/10 text-white/80 hover:text-white hover:bg-white/10 transition-all duration-300"
            >
              {React.createElement(FaTimes as any, { className: "text-xl" })}
            </button>

            {/* Заголовок */}
            <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 mb-6 text-center">
              Интерактивная визитная карточка
            </h2>

            {/* 3D Canvas */}
            <div className="relative w-full h-[500px] rounded-2xl overflow-hidden border border-white/10">
              <Canvas
                camera={{ position: [0, 0, 30], fov: 20 }}
                dpr={[1, 2]}
                gl={{ alpha: true }}
                onCreated={({ gl }) => gl.setClearColor(new THREE.Color(0x000000), 0)}
              >
                <ambientLight intensity={Math.PI} />
                <Physics gravity={[0, -40, 0]} timeStep={1 / 60}>
                  <Band />
                </Physics>
                <Environment blur={0.75}>
                  <Lightformer
                    intensity={2}
                    color="white"
                    position={[0, -1, 5]}
                    rotation={[0, 0, Math.PI / 3]}
                    scale={[100, 0.1, 1]}
                  />
                  <Lightformer
                    intensity={3}
                    color="white"
                    position={[-1, -1, 1]}
                    rotation={[0, 0, Math.PI / 3]}
                    scale={[100, 0.1, 1]}
                  />
                  <Lightformer
                    intensity={3}
                    color="white"
                    position={[1, 1, 1]}
                    rotation={[0, 0, Math.PI / 3]}
                    scale={[100, 0.1, 1]}
                  />
                  <Lightformer
                    intensity={10}
                    color="white"
                    position={[-10, 0, 14]}
                    rotation={[0, Math.PI / 2, Math.PI / 3]}
                    scale={[100, 10, 1]}
                  />
                </Environment>
              </Canvas>

              {/* Подсказка */}
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 backdrop-blur-xl bg-white/10 border border-white/20 rounded-xl px-4 py-2">
                <p className="text-white/90 text-sm font-medium">
                  Перетащите карточку мышью
                </p>
              </div>
            </div>

            {/* Дополнительная информация */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="backdrop-blur-xl bg-white/5 rounded-xl border border-white/10 p-4 text-center">
                <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-1">
                  Физика
                </div>
                <p className="text-white/70 text-sm">
                  Реалистичная симуляция
                </p>
              </div>
              <div className="backdrop-blur-xl bg-white/5 rounded-xl border border-white/10 p-4 text-center">
                <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-1">
                  Интерактив
                </div>
                <p className="text-white/70 text-sm">
                  Перетаскивание мышью
                </p>
              </div>
              <div className="backdrop-blur-xl bg-white/5 rounded-xl border border-white/10 p-4 text-center">
                <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-blue-400 mb-1">
                  3D Графика
                </div>
                <p className="text-white/70 text-sm">
                  WebGL визуализация
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

interface BandProps {
  maxSpeed?: number;
  minSpeed?: number;
}

function Band({ maxSpeed = 50, minSpeed = 0 }: BandProps) {
  const band = useRef<any>(null);
  const fixed = useRef<any>(null);
  const j1 = useRef<any>(null);
  const j2 = useRef<any>(null);
  const j3 = useRef<any>(null);
  const card = useRef<any>(null);

  const vec = new THREE.Vector3();
  const ang = new THREE.Vector3();
  const rot = new THREE.Vector3();
  const dir = new THREE.Vector3();

  const segmentProps: any = {
    type: 'dynamic' as RigidBodyProps['type'],
    canSleep: true,
    colliders: false,
    angularDamping: 4,
    linearDamping: 4
  };

  // Заглушка для демонстрации (если нет GLB файла)
  const nodes = {
    card: { geometry: new THREE.BoxGeometry(1.6, 2.25, 0.02) },
    clip: { geometry: new THREE.BoxGeometry(0.1, 0.5, 0.1) },
    clamp: { geometry: new THREE.BoxGeometry(0.1, 0.3, 0.1) }
  };

  const materials = {
    base: { map: null },
    metal: new THREE.MeshStandardMaterial({ color: '#888', metalness: 0.9, roughness: 0.3 })
  };

  // Не загружаем внешние файлы - используем только встроенные геометрии
  // const gltf = useGLTF(cardGLB, true) as any;
  // const texture = useTexture(lanyard);
  // if (gltf?.nodes) Object.assign(nodes, gltf.nodes);
  // if (gltf?.materials) Object.assign(materials, gltf.materials);

  // Создаем пустую текстуру для шнурка
  const texture = new THREE.Texture();

  const [curve] = useState(
    () =>
      new THREE.CatmullRomCurve3([
        new THREE.Vector3(),
        new THREE.Vector3(),
        new THREE.Vector3(),
        new THREE.Vector3()
      ])
  );
  const [dragged, drag] = useState<false | THREE.Vector3>(false);
  const [hovered, hover] = useState(false);

  useRopeJoint(fixed, j1, [[0, 0, 0], [0, 0, 0], 1]);
  useRopeJoint(j1, j2, [[0, 0, 0], [0, 0, 0], 1]);
  useRopeJoint(j2, j3, [[0, 0, 0], [0, 0, 0], 1]);
  useSphericalJoint(j3, card, [
    [0, 0, 0],
    [0, 1.45, 0]
  ]);

  useEffect(() => {
    if (hovered) {
      document.body.style.cursor = dragged ? 'grabbing' : 'grab';
      return () => {
        document.body.style.cursor = 'auto';
      };
    }
  }, [hovered, dragged]);

  useFrame((state, delta) => {
    if (dragged && typeof dragged !== 'boolean') {
      vec.set(state.pointer.x, state.pointer.y, 0.5).unproject(state.camera);
      dir.copy(vec).sub(state.camera.position).normalize();
      vec.add(dir.multiplyScalar(state.camera.position.length()));
      [card, j1, j2, j3, fixed].forEach(ref => ref.current?.wakeUp());
      card.current?.setNextKinematicTranslation({
        x: vec.x - dragged.x,
        y: vec.y - dragged.y,
        z: vec.z - dragged.z
      });
    }
    if (fixed.current && band.current) {
      [j1, j2].forEach(ref => {
        if (!ref.current.lerped)
          ref.current.lerped = new THREE.Vector3().copy(ref.current.translation());
        const clampedDistance = Math.max(
          0.1,
          Math.min(1, ref.current.lerped.distanceTo(ref.current.translation()))
        );
        ref.current.lerped.lerp(
          ref.current.translation(),
          delta * (minSpeed + clampedDistance * (maxSpeed - minSpeed))
        );
      });
      curve.points[0].copy(j3.current.translation());
      curve.points[1].copy(j2.current.lerped);
      curve.points[2].copy(j1.current.lerped);
      curve.points[3].copy(fixed.current.translation());
      
      const points = curve.getPoints(32);
      const geometry = new MeshLineGeometry();
      geometry.setPoints(points);
      band.current.geometry = geometry;
      
      ang.copy(card.current.angvel());
      rot.copy(card.current.rotation());
      card.current.setAngvel({ x: ang.x, y: ang.y - rot.y * 0.25, z: ang.z });
    }
  });

  curve.curveType = 'chordal';
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  
  const lineGeometry = new MeshLineGeometry();
  const lineMaterial = new MeshLineMaterial({
    color: 'white',
    resolution: new THREE.Vector2(1000, 1000),
    useMap: 0,
    repeat: new THREE.Vector2(-4, 1),
    lineWidth: 1
  } as any);

  return (
    <>
      <group position={[0, 4, 0]}>
        <RigidBody ref={fixed} {...segmentProps} type={'fixed' as RigidBodyProps['type']} />
        <RigidBody position={[0.5, 0, 0]} ref={j1} {...segmentProps}>
          <BallCollider args={[0.1]} />
        </RigidBody>
        <RigidBody position={[1, 0, 0]} ref={j2} {...segmentProps}>
          <BallCollider args={[0.1]} />
        </RigidBody>
        <RigidBody position={[1.5, 0, 0]} ref={j3} {...segmentProps}>
          <BallCollider args={[0.1]} />
        </RigidBody>
        <RigidBody
          position={[2, 0, 0]}
          ref={card}
          {...segmentProps}
          type={
            dragged
              ? ('kinematicPosition' as RigidBodyProps['type'])
              : ('dynamic' as RigidBodyProps['type'])
          }
        >
          <CuboidCollider args={[0.8, 1.125, 0.01]} />
          <group
            scale={2.25}
            position={[0, -1.2, -0.05]}
            onPointerOver={() => hover(true)}
            onPointerOut={() => hover(false)}
            onPointerUp={(e: any) => {
              e.target.releasePointerCapture(e.pointerId);
              drag(false);
            }}
            onPointerDown={(e: any) => {
              e.target.setPointerCapture(e.pointerId);
              drag(
                new THREE.Vector3()
                  .copy(e.point)
                  .sub(vec.copy(card.current.translation()))
              );
            }}
          >
            <mesh geometry={nodes.card.geometry}>
              <meshPhysicalMaterial
                map={materials.base.map}
                clearcoat={1}
                clearcoatRoughness={0.15}
                roughness={0.9}
                metalness={0.8}
                color="#3B82F6"
              />
            </mesh>
            <mesh
              geometry={nodes.clip.geometry}
              material={materials.metal}
              material-roughness={0.3}
            />
            <mesh geometry={nodes.clamp.geometry} material={materials.metal} />
          </group>
        </RigidBody>
      </group>
      <mesh ref={band} geometry={lineGeometry} material={lineMaterial} />
    </>
  );
}
