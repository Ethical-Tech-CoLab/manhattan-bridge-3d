import { useCallback, useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import type { Confidence, PartMetadata, PartsDocument, ViewMode, ViewerConfig } from './model';
import { MATERIAL_APPEARANCE, PROVENANCE_STYLE, VIEW_PRESETS } from './model';

/**
 * BridgeViewer renders any source-governed GLB whose part nodes carry metadata in glTF `extras`.
 * Nothing in this file is Manhattan Bridge specific: the model, its metadata and the camera framing
 * all come from model.config.json.
 *
 * This drives three.js directly rather than through a React reconciler. The viewer needs only four
 * things from the 3D layer - load, orbit, pick, recolour - and a direct implementation keeps the
 * canvas lifecycle explicit and debuggable, with React owning only the surrounding UI.
 */

export interface BridgeViewerProps {
  config: ViewerConfig;
  doc: PartsDocument;
  selectedId: string | null;
  hiddenSystems: Set<string>;
  hiddenParts: Set<string>;
  confidenceOverlay: boolean;
  materialMode: boolean;
  provenanceOutlines: boolean;
  hiddenProvenance: Set<string>;
  /** Bumped by the shell whenever the surrounding layout changes, e.g. a panel collapses. */
  layoutToken: number;
  viewMode: ViewMode;
  /** Reports metres-per-pixel of the active camera so the shell can draw a scale bar. */
  onScaleChange: (metresPerPixel: number) => void;
  onSelect: (partId: string | null) => void;
  focusToken: number;
}

interface RenderablePart {
  id: string;
  root: THREE.Object3D;
  renderables: Array<THREE.Mesh | THREE.LineSegments>;
  outlines: THREE.LineSegments[];
}

interface Viewer {
  renderer: THREE.WebGLRenderer;
  scene: THREE.Scene;
  camera: THREE.PerspectiveCamera;
  orthoCamera: THREE.OrthographicCamera;
  activeCamera: THREE.Camera;
  controls: OrbitControls;
  raycaster: THREE.Raycaster;
  parts: RenderablePart[];
  selectionHelper: THREE.Box3Helper | null;
  /** Reconcile the drawing buffer with the element, and render one frame immediately. */
  resize: () => void;
  dispose: () => void;
}

const PRESENTATION_FOG = new THREE.FogExp2(new THREE.Color('#93a8bd'), 0.000055);

const SELECTION_COLOR = new THREE.Color('#ffffff');
const SELECTION_BOX_COLOR = new THREE.Color('#ffd166');

function collectParts(root: THREE.Object3D): RenderablePart[] {
  const parts: RenderablePart[] = [];
  root.traverse((object) => {
    const partId = (object.userData as Partial<PartMetadata>)?.part_id;
    if (!partId) return;
    const renderables: Array<THREE.Mesh | THREE.LineSegments> = [];
    object.traverse((child) => {
      const isRenderable =
        (child as THREE.Mesh).isMesh === true || (child as THREE.LineSegments).isLineSegments === true;
      if (!isRenderable) return;
      const renderable = child as THREE.Mesh | THREE.LineSegments;
      // The exporter deduplicates materials by style, so clone before recolouring per part.
      const material = renderable.material as THREE.Material | THREE.Material[];
      renderable.material = Array.isArray(material)
        ? material.map((m) => m.clone())
        : material.clone();
      const cloned = renderable.material as THREE.MeshStandardMaterial;
      renderable.userData.baseColor = cloned.color.clone();
      renderable.userData.baseOpacity = cloned.opacity;
      renderable.userData.baseRoughness = cloned.roughness ?? 1;
      renderable.userData.baseMetalness = cloned.metalness ?? 0;
      renderables.push(renderable);
    });
    if (renderables.length > 0) parts.push({ id: partId, root: object, renderables, outlines: [] });
  });
  return parts;
}

/** Model bounding box corners converted from the authoring Z-up frame to the glTF Y-up frame. */
function framingBox(doc: PartsDocument): { center: THREE.Vector3; corners: THREE.Vector3[] } | null {
  const bbox = doc.measures.model_bbox_prototype_m as { min: number[]; max: number[] } | undefined;
  if (!bbox) return null;
  const corners: THREE.Vector3[] = [];
  for (const x of [bbox.min[0], bbox.max[0]]) {
    for (const y of [bbox.min[1], bbox.max[1]]) {
      for (const z of [bbox.min[2], bbox.max[2]]) {
        corners.push(new THREE.Vector3(x, z, -y));
      }
    }
  }
  const center = new THREE.Vector3(
    (bbox.min[0] + bbox.max[0]) / 2,
    (bbox.min[2] + bbox.max[2]) / 2,
    -(bbox.min[1] + bbox.max[1]) / 2,
  );
  return { center, corners };
}

/** Exact fit of an axis-aligned box: every corner must sit inside both frustum planes. */
function frameCamera(viewer: Viewer, config: ViewerConfig, doc: PartsDocument): void {
  const frame = framingBox(doc);
  const { camera, controls } = viewer;
  if (!frame) {
    camera.position.set(...config.camera.position);
    controls.target.set(...config.camera.target);
    controls.update();
    return;
  }
  const vFov = (camera.fov * Math.PI) / 180;
  const tanV = Math.tan(vFov / 2);
  const tanH = tanV * camera.aspect;

  const direction = new THREE.Vector3(...config.camera.position).normalize();
  const right = new THREE.Vector3().crossVectors(direction, new THREE.Vector3(0, 1, 0)).normalize();
  const up = new THREE.Vector3().crossVectors(right, direction).normalize();

  let distance = 0;
  const offset = new THREE.Vector3();
  for (const corner of frame.corners) {
    offset.copy(corner).sub(frame.center);
    const depth = offset.dot(direction);
    distance = Math.max(
      distance,
      Math.abs(offset.dot(right)) / tanH + depth,
      Math.abs(offset.dot(up)) / tanV + depth,
    );
  }
  distance *= config.framePadding ?? 1.2;

  camera.position.copy(frame.center).addScaledVector(direction, distance);
  camera.updateProjectionMatrix();
  controls.target.copy(frame.center);
  controls.update();
}

/**
 * Attach a provenance outline to every mesh: solid for documented, dashed for inferred, dotted for
 * assumed (SRC-018 section 5.5).
 *
 * The outlines are built once after load and then only toggled, because EdgesGeometry is expensive
 * and the provenance of a part never changes at runtime. Line primitives are skipped: a truss web
 * drawn as wires is already unmistakably schematic, and outlining a line with a line would just
 * thicken it.
 */
function buildProvenanceOutlines(viewer: Viewer, doc: PartsDocument): void {
  const metadataById = new Map(doc.parts.map((part) => [part.part_id, part]));

  viewer.parts.forEach((part) => {
    const meta = metadataById.get(part.id);
    if (!meta) return;
    const style = PROVENANCE_STYLE[meta.geometry_provenance];
    if (!style) return;

    part.renderables.forEach((renderable) => {
      if ((renderable as THREE.Mesh).isMesh !== true) return;
      const mesh = renderable as THREE.Mesh;
      const edges = new THREE.EdgesGeometry(mesh.geometry, 25);
      const material = style.dash
        ? new THREE.LineDashedMaterial({
            color: new THREE.Color(style.color),
            dashSize: style.dash[0],
            gapSize: style.dash[1],
            transparent: true,
            opacity: 0.95,
          })
        : new THREE.LineBasicMaterial({
            color: new THREE.Color(style.color),
            transparent: true,
            opacity: 0.85,
          });
      const outline = new THREE.LineSegments(edges, material);
      // Required for LineDashedMaterial; without it every dashed line renders solid.
      outline.computeLineDistances();
      outline.userData.isProvenanceOutline = true;
      outline.renderOrder = 2;
      mesh.add(outline);
      part.outlines.push(outline);
    });
  });
}

export default function BridgeViewer(props: BridgeViewerProps) {
  const {
    config,
    doc,
    selectedId,
    hiddenSystems,
    hiddenParts,
    confidenceOverlay,
    materialMode,
    provenanceOutlines,
    hiddenProvenance,
    layoutToken,
    viewMode,
    onScaleChange,
    onSelect,
  } = props;
  const hostRef = useRef<HTMLDivElement | null>(null);
  const viewerRef = useRef<Viewer | null>(null);
  const onSelectRef = useRef(onSelect);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const environmentRef = useRef<THREE.Group | null>(null);

  onSelectRef.current = onSelect;
  const onScaleChangeRef = useRef(onScaleChange);
  onScaleChangeRef.current = onScaleChange;

  // ------------------------------------------------------------------ lifecycle
  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(config.background);

    const camera = new THREE.PerspectiveCamera(
      config.camera.fov,
      1,
      config.camera.near,
      config.camera.far,
    );
    camera.position.set(...config.camera.position);

    // A true orthographic camera, not a long-lens perspective. Engineering views have to be
    // measurable off the screen, and only a parallel projection makes a scale bar honest
    // everywhere in the frame rather than just at the target distance.
    const orthoCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, -60000, 60000);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    host.appendChild(renderer.domElement);
    const canvas = renderer.domElement;

    // ---------------------------------------------------------------- presentation layer
    //
    // Everything between here and the controls is lighting and scene furniture. Per
    // CONFIDENCE-MODEL.md section 7 it may change how a surface is lit, shaded or coloured, and may
    // not move a vertex. GRT-078 asserts that boundary against the exported mesh.
    const environment = new THREE.Group();
    environment.name = 'presentation_environment';
    environment.userData.presentationOnly = true;
    scene.add(environment);
    environmentRef.current = environment;

    // Sky. A large inverted sphere with a vertical gradient, which reads as atmosphere without
    // pretending to be a measured sky or a real time of day.
    const sky = new THREE.Mesh(
      new THREE.SphereGeometry(24000, 32, 16),
      new THREE.ShaderMaterial({
        side: THREE.BackSide,
        depthWrite: false,
        uniforms: {
          top: { value: new THREE.Color('#2b4568') },
          bottom: { value: new THREE.Color('#8fa4b8') },
        },
        vertexShader: `
          varying float vH;
          void main() {
            vec4 world = modelMatrix * vec4(position, 1.0);
            vH = normalize(world.xyz).y;
            gl_Position = projectionMatrix * viewMatrix * world;
          }`,
        fragmentShader: `
          uniform vec3 top; uniform vec3 bottom; varying float vH;
          void main() {
            gl_FragColor = vec4(mix(bottom, top, smoothstep(-0.05, 0.55, vH)), 1.0);
          }`,
      }),
    );
    sky.name = 'presentation_sky';
    environment.add(sky);

    // Water at the mean-high-water datum. This is the one piece of scene furniture that is
    // dimensionally honest: z = 0 in the authoring frame IS mean high water, a registered datum, so
    // the plane sits exactly where the datum says and the towers meet it correctly.
    //
    // Deliberately rough and barely metallic. A low-roughness, high-metalness plane behaves as a
    // mirror and throws a blown-out specular streak across the whole frame, which drowns the
    // structure -- the subject of the image -- in scene furniture.
    const water = new THREE.Mesh(
      new THREE.PlaneGeometry(30000, 30000),
      new THREE.MeshStandardMaterial({
        color: new THREE.Color('#33485a'),
        roughness: 0.88,
        metalness: 0.06,
        transparent: true,
        opacity: 0.95,
      }),
    );
    water.name = 'presentation_water_mhw';
    water.rotation.x = -Math.PI / 2;
    water.position.y = 0;
    environment.add(water);

    // Haze. A 2 km structure needs aerial perspective or the far end reads as near, and the
    // reference photography (SRC-018) shows exactly this over the East River.
    scene.fog = PRESENTATION_FOG;

    scene.add(new THREE.HemisphereLight(0xdce9f7, 0x2a3038, 1.0));
    scene.add(new THREE.AmbientLight(0xffffff, 0.32));
    const key = new THREE.DirectionalLight(0xfff3e2, 2.3);
    key.position.set(900, 1100, 700);
    scene.add(key);
    const fill = new THREE.DirectionalLight(0xcfe0f5, 0.85);
    fill.position.set(-800, 350, -700);
    scene.add(fill);
    // A dim upward light so the underside reads at all. The underside is what a person in DUMBO
    // actually sees, and with only overhead light it renders as a black slab.
    const bounce = new THREE.DirectionalLight(0x93a7b8, 0.5);
    bounce.position.set(0, -600, 200);
    scene.add(bounce);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.maxDistance = config.camera.far * 0.5;
    controls.target.set(...config.camera.target);

    const raycaster = new THREE.Raycaster();
    raycaster.params.Line = { threshold: config.lineRaycastThreshold };

    const viewer: Viewer = {
      renderer,
      scene,
      camera,
      orthoCamera,
      activeCamera: camera,
      controls,
      raycaster,
      parts: [],
      selectionHelper: null,
      resize: () => undefined,
      dispose: () => undefined,
    };
    viewerRef.current = viewer;

    const resize = () => {
      const rect = host.getBoundingClientRect();
      const width = Math.max(1, Math.floor(rect.width));
      const height = Math.max(1, Math.floor(rect.height));
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      // The orthographic frustum has no aspect of its own: it must be rebuilt from the current
      // half-height so that a metre is the same number of pixels horizontally and vertically.
      const halfH = (orthoCamera.top - orthoCamera.bottom) / 2 || 1;
      const halfW = halfH * (width / height);
      orthoCamera.left = -halfW;
      orthoCamera.right = halfW;
      orthoCamera.updateProjectionMatrix();
    };
    resize();
    const observer = new ResizeObserver(resize);
    observer.observe(host);

    // Also exposed so a layout change the browser does not report -- collapsing a side panel only
    // alters a CSS grid column, and neither ResizeObserver nor requestAnimationFrame can be relied
    // on to deliver promptly in every environment -- can force the reconciliation directly.
    viewer.resize = () => {
      resize();
      renderer.render(scene, viewer.activeCamera);
    };

    /**
     * Reconcile the drawing buffer with the element every frame.
     *
     * ResizeObserver alone proved unreliable here: collapsing a side panel changes a CSS grid
     * column, and the canvas element resized without the observer delivering a callback in time,
     * leaving a 760 px buffer stretched across a 1372 px element. Comparing the two directly each
     * frame costs a couple of property reads and cannot miss a resize whatever caused it.
     */
    const syncSize = () => {
      const width = Math.max(1, Math.floor(canvas.clientWidth));
      const height = Math.max(1, Math.floor(canvas.clientHeight));
      const ratio = renderer.getPixelRatio();
      if (canvas.width !== Math.floor(width * ratio) || canvas.height !== Math.floor(height * ratio)) {
        renderer.setSize(width, height, false);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        const halfH = (orthoCamera.top - orthoCamera.bottom) / 2 || 1;
        const halfW = halfH * (width / height);
        orthoCamera.left = -halfW;
        orthoCamera.right = halfW;
        orthoCamera.updateProjectionMatrix();
      }
    };

    let frameId = 0;
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      syncSize();
      controls.update();
      renderer.render(scene, viewer.activeCamera);
    };
    animate();

    let disposed = false;
    const loader = new GLTFLoader();
    loader
      .loadAsync(config.modelUrl)
      .then((gltf) => {
        if (disposed) return;
        scene.add(gltf.scene);
        viewer.parts = collectParts(gltf.scene);
        buildProvenanceOutlines(viewer, doc);
        resize();
        frameCamera(viewer, config, doc);
        setReady(true);
      })
      .catch((err: unknown) => {
        if (!disposed) setError(err instanceof Error ? err.message : String(err));
      });

    const pointer = new THREE.Vector2();
    let downAt: { x: number; y: number } | null = null;
    const onPointerDown = (event: PointerEvent) => {
      downAt = { x: event.clientX, y: event.clientY };
    };
    const onPointerUp = (event: PointerEvent) => {
      // Ignore drags: only a near-stationary press counts as a pick.
      if (!downAt || Math.hypot(event.clientX - downAt.x, event.clientY - downAt.y) > 4) return;
      downAt = null;
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, viewer.activeCamera);
      const visible = viewer.parts.filter((p) => p.root.visible);
      const hits = raycaster.intersectObjects(
        visible.flatMap((p) => p.renderables),
        false,
      );
      if (hits.length === 0) {
        onSelectRef.current(null);
        return;
      }
      let object: THREE.Object3D | null = hits[0].object;
      while (object && !(object.userData as Partial<PartMetadata>)?.part_id) {
        object = object.parent;
      }
      onSelectRef.current(object ? ((object.userData as PartMetadata).part_id as string) : null);
    };
    renderer.domElement.addEventListener('pointerdown', onPointerDown);
    renderer.domElement.addEventListener('pointerup', onPointerUp);

    viewer.dispose = () => {
      disposed = true;
      cancelAnimationFrame(frameId);
      observer.disconnect();
      renderer.domElement.removeEventListener('pointerdown', onPointerDown);
      renderer.domElement.removeEventListener('pointerup', onPointerUp);
      controls.dispose();
      renderer.dispose();
      if (renderer.domElement.parentElement === host) host.removeChild(renderer.domElement);
    };

    return () => {
      viewer.dispose();
      viewerRef.current = null;
    };
  }, [config, doc]);

  // ------------------------------------------------------- visibility + colours
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || !ready) return;
    const metadataById = new Map(doc.parts.map((part) => [part.part_id, part]));

    // The environment is presentation only, so it steps aside for the two governance views: the
    // confidence overlay and the schematic (materials-off) view both want a neutral field, not a
    // sky. Fog goes with it, because haze over a schematic reads as data loss.
    const env = environmentRef.current;
    if (env) env.visible = materialMode && !confidenceOverlay;
    viewer.scene.fog = env && env.visible ? PRESENTATION_FOG : null;

    viewer.parts.forEach((part) => {
      const meta = metadataById.get(part.id);

      // SRC-018 section 5.5 is explicit that the provenance filter must hide rather than fade:
      // "a faded outline is still a shape a reader will trace, and the honest experience of
      // switching both off on this project is an empty frame."
      const provenanceHidden = meta ? hiddenProvenance.has(meta.geometry_provenance) : false;
      part.root.visible = !(
        hiddenParts.has(part.id) ||
        (meta ? hiddenSystems.has(meta.system) : false) ||
        provenanceHidden
      );
      const isSelected = part.id === selectedId;
      const appearance =
        materialMode && meta ? MATERIAL_APPEARANCE[meta.material] ?? null : null;
      const provenance = meta ? PROVENANCE_STYLE[meta.geometry_provenance] : null;

      part.outlines.forEach((outline) => {
        outline.visible = provenanceOutlines;
      });

      part.renderables.forEach((renderable) => {
        const material = renderable.material as THREE.MeshStandardMaterial;
        const base = renderable.userData.baseColor as THREE.Color;
        const baseOpacity = renderable.userData.baseOpacity as number;
        const isLine = (renderable as THREE.LineSegments).isLineSegments === true;

        // Confidence overlay still wins: it is a governance view, and if the reader has asked to
        // see grades, an attractive stone finish must not overrule that.
        const overlay = confidenceOverlay && meta
          ? new THREE.Color(doc.confidence_colors[meta.confidence as Confidence])
          : appearance
            ? new THREE.Color(appearance.color)
            : base;
        material.color.copy(isSelected ? SELECTION_COLOR : overlay);

        if (appearance && !confidenceOverlay) {
          // Line primitives keep their schematic opacity: a wire-drawn truss web rendered opaque
          // would read as solid plate, which would be a stronger claim than the geometry supports.
          // Fill opacity is further reduced by provenance so that reasoned and judged geometry
          // recedes behind what is actually documented.
          const provenanceFill = provenanceOutlines && provenance ? provenance.fillOpacity : 1;
          material.opacity = isSelected
            ? Math.min(1, appearance.opacity * 2.5)
            : isLine
              ? baseOpacity
              : appearance.opacity * provenanceFill;
          if (!isLine) {
            material.roughness = appearance.roughness;
            material.metalness = appearance.metalness;
            material.flatShading = meta?.material === 'masonry' || meta?.material === 'concrete';
          }
        } else {
          material.opacity = isSelected ? Math.min(1, baseOpacity * 2.5) : baseOpacity;
          if (!isLine) {
            material.roughness = renderable.userData.baseRoughness as number;
            material.metalness = renderable.userData.baseMetalness as number;
            material.flatShading = false;
          }
        }
        material.transparent = material.opacity < 1;
        material.needsUpdate = true;
      });
    });
  }, [
    ready,
    doc,
    hiddenParts,
    hiddenSystems,
    selectedId,
    confidenceOverlay,
    materialMode,
    provenanceOutlines,
    hiddenProvenance,
  ]);

  // ------------------------------------------------------------ selection box
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || !ready) return;
    if (viewer.selectionHelper) {
      viewer.scene.remove(viewer.selectionHelper);
      viewer.selectionHelper.geometry.dispose();
      viewer.selectionHelper = null;
    }
    const part = viewer.parts.find((p) => p.id === selectedId);
    if (!part || !part.root.visible) return;
    const box = new THREE.Box3().setFromObject(part.root);
    if (box.isEmpty()) return;
    const helper = new THREE.Box3Helper(box, SELECTION_BOX_COLOR);
    viewer.scene.add(helper);
    viewer.selectionHelper = helper;
  }, [ready, selectedId, hiddenParts, hiddenSystems]);

  // ------------------------------------------------------------------- framing
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || !ready) return;
    const part = doc.parts.find((p) => p.part_id === selectedId);
    if (!part) {
      frameCamera(viewer, config, doc);
      return;
    }
    // Authoring frame is Z-up (GEOMETRY-CONTROL.md); the GLB root rotates it to Y-up.
    const [minX, minY, minZ] = part.bbox_prototype_m.min;
    const [maxX, maxY, maxZ] = part.bbox_prototype_m.max;
    viewer.controls.target.set((minX + maxX) / 2, (minZ + maxZ) / 2, -(minY + maxY) / 2);
    viewer.controls.update();
  }, [ready, props.focusToken, selectedId, config, doc]);

  // The shell changed the layout around us. Reconcile immediately rather than waiting for the
  // browser to notice, so the render fills the new box on the very next paint.
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || !ready) return;
    viewer.resize();
  }, [ready, layoutToken]);

  // ------------------------------------------------------------------ view mode
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || !ready) return;
    const preset = VIEW_PRESETS[viewMode];
    const { camera, orthoCamera, controls, renderer, scene } = viewer;
    const frame = framingBox(doc);
    const centre = frame ? frame.center : new THREE.Vector3();

    if (!preset.orthographic) {
      viewer.activeCamera = camera;
      controls.object = camera;
      frameCamera(viewer, config, doc);
    } else {
      // Size the frustum to the model's extent as seen from this direction, so switching views
      // always lands on something sensible rather than on an empty frame.
      const dir = new THREE.Vector3(...preset.direction).normalize();
      const up = new THREE.Vector3(...preset.up).normalize();
      const right = new THREE.Vector3().crossVectors(dir, up).normalize();

      let halfW = 1;
      let halfH = 1;
      if (frame) {
        const offset = new THREE.Vector3();
        for (const corner of frame.corners) {
          offset.copy(corner).sub(centre);
          halfW = Math.max(halfW, Math.abs(offset.dot(right)));
          halfH = Math.max(halfH, Math.abs(offset.dot(up)));
        }
      }
      const pad = config.framePadding ?? 1.05;
      halfW *= pad;
      halfH *= pad;

      const canvas = renderer.domElement;
      const aspect = Math.max(1e-6, canvas.clientWidth / Math.max(1, canvas.clientHeight));
      // Grow whichever axis is too small, never shrink one, or the model would be cropped.
      if (halfW / halfH > aspect) halfH = halfW / aspect;
      else halfW = halfH * aspect;

      orthoCamera.left = -halfW;
      orthoCamera.right = halfW;
      orthoCamera.top = halfH;
      orthoCamera.bottom = -halfH;
      orthoCamera.up.copy(up);
      orthoCamera.position.copy(centre).addScaledVector(dir, 8000);
      orthoCamera.lookAt(centre);
      orthoCamera.zoom = 1;
      orthoCamera.updateProjectionMatrix();

      viewer.activeCamera = orthoCamera;
      controls.object = orthoCamera;
      controls.target.copy(centre);
      controls.update();
      // Re-derive the horizontal half-width from the canvas as it actually is. The aspect read
      // above can be stale on the first switch after a layout change, which produced a frustum an
      // order of magnitude too wide and a scale bar to match.
      viewer.resize();
    }
    renderer.render(scene, viewer.activeCamera);
  }, [ready, viewMode, config, doc]);

  // ------------------------------------------------- scale reporting for the scale bar
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || !ready) return;
    const { controls, renderer } = viewer;

    const report = () => {
      const canvas = renderer.domElement;
      const height = Math.max(1, canvas.clientHeight);
      const active = viewer.activeCamera;
      let metresPerPixel: number;
      if ((active as THREE.OrthographicCamera).isOrthographicCamera) {
        const ortho = active as THREE.OrthographicCamera;
        metresPerPixel = (ortho.top - ortho.bottom) / ortho.zoom / height;
      } else {
        // Perspective scale is only true at the orbit target's depth, which is why the shell
        // labels it as approximate in this mode.
        const persp = active as THREE.PerspectiveCamera;
        const distance = persp.position.distanceTo(controls.target);
        metresPerPixel = (2 * distance * Math.tan((persp.fov * Math.PI) / 360)) / height;
      }
      onScaleChangeRef.current(metresPerPixel);
    };

    report();
    controls.addEventListener('change', report);
    return () => controls.removeEventListener('change', report);
  }, [ready, viewMode, layoutToken, doc]);

  const retry = useCallback(() => window.location.reload(), []);

  return (
    <div className="canvas-host" ref={hostRef}>
      {error && (
        <div className="canvas-error">
          <strong>Could not load {config.modelUrl}</strong>
          <span>{error}</span>
          <span>
            Run <code>python scripts/build_control_skeleton.py</code> from the repository root, then{' '}
            <button type="button" onClick={retry}>
              reload
            </button>
            .
          </span>
        </div>
      )}
    </div>
  );
}
