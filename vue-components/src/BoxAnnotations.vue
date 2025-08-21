<script setup lang="ts">
import {
  ref,
  computed,
  watchEffect,
  watch,
  defineProps,
  toRefs,
  onMounted,
  onBeforeUnmount,
} from "vue";
import { Quadtree, Rectangle } from "@timohausmann/quadtree-ts";
import type { BoxAnnotationAugmented } from "./annotations.js";
import AnnotationsPopup from "./AnnotationPopup.vue";
import { useDevicePixelRatio, type Rect } from "./utils.js";

const props = defineProps<{
  boxAnnotations: BoxAnnotationAugmented[];
  imageSize: { width: number; height: number };
  lineWidth: number;
  lineOpacity: number;
  popupContainer: Element | undefined | null;
  groupByModel: boolean;
}>();
const { boxAnnotations, lineWidth, lineOpacity } = toRefs(props);

const visibleCanvas = ref<HTMLCanvasElement>();
const visibleCtx = computed(() =>
  visibleCanvas.value?.getContext("2d", { alpha: true }),
);
const pickingCanvas = ref<HTMLCanvasElement>();
const pickingCtx = computed(() =>
  pickingCanvas.value?.getContext("2d", { willReadFrequently: true }),
);

const rect = ref<Rect>({ width: 1, height: 1, top: 0, left: 0 });
let resizeObserver: ResizeObserver | null = null;

// Compute scaling factor from image size to canvas size.
const imageToCanvasScale = computed(() => {
  if (!rect.value) return 1;

  const widthRatio = rect.value.width / props.imageSize.width;
  const heightRatio = rect.value.height / props.imageSize.height;
  if (widthRatio > heightRatio) {
    return heightRatio;
  } else {
    return widthRatio;
  }
});

const canvasDims = computed(() => {
  return {
    width: Math.floor(props.imageSize.width * imageToCanvasScale.value),
    height: Math.floor(props.imageSize.height * imageToCanvasScale.value),
  };
});

const dpi = useDevicePixelRatio();
const lineWidthInDisplay = computed(
  () => lineWidth.value * dpi.pixelRatio.value,
);

// Draw visible annotations
watch(
  [
    visibleCanvas,
    visibleCtx,
    canvasDims,
    lineWidthInDisplay,
    lineOpacity,
    imageToCanvasScale,
    () => props.boxAnnotations,
  ],
  () => {
    if (!visibleCanvas.value || !visibleCtx.value) return;
    // setTimeout avoids "error: ResizeObserver loop completed with undelivered notifications"
    setTimeout(drawVisibleAnnotations, 0);
  },
);

function drawVisibleAnnotations() {
  if (!visibleCanvas.value || !visibleCtx.value) return;

  const canvas = visibleCanvas.value;
  const ctx = visibleCtx.value;

  const dims = canvasDims.value;

  canvas.width = dims.width;
  canvas.height = dims.height;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.globalCompositeOperation = "lighter";
  ctx.lineWidth = lineWidthInDisplay.value;
  const alpha = lineOpacity.value;

  props.boxAnnotations.forEach(({ color, bbox }) => {
    ctx.strokeStyle = `rgba(${[...color, alpha].join(",")})`;
    ctx.strokeRect(
      bbox[0] * imageToCanvasScale.value,
      bbox[1] * imageToCanvasScale.value,
      bbox[2] * imageToCanvasScale.value,
      bbox[3] * imageToCanvasScale.value,
    );
  });
}

// Draw picking annotations
let annotationsTree: Quadtree<Rectangle<number>> | undefined = undefined;

watchEffect(() => {
  if (!pickingCanvas.value || !pickingCtx.value || !rect.value) return;

  const canvas = pickingCanvas.value;
  const ctx = pickingCtx.value;

  canvas.width = canvasDims.value.width;
  canvas.height = canvasDims.value.height;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  annotationsTree = new Quadtree({
    width: canvas.width,
    height: canvas.height,
    maxLevels: 8,
    maxObjects: 10,
  });

  props.boxAnnotations.forEach((annotation, i) => {
    const [x, y, width, height] = annotation.bbox.map(
      (coord) => coord * imageToCanvasScale.value,
    );
    const treeNode = new Rectangle({
      x,
      y,
      width,
      height,
      data: i,
    });
    annotationsTree!.insert(treeNode);
    ctx.fillStyle = "rgb(255, 0, 0)";
    ctx.fillRect(x, y, width, height);
  });
});

function displayToPixel(
  x: number,
  y: number,
  canvas: HTMLCanvasElement,
): [number, number] {
  const { left, width, top, height } = canvas.getBoundingClientRect();

  const ratio_w = width / height / (canvas.width / canvas.height);
  const ratio_h = 1 / ratio_w;

  let frac: [number, number];

  if (ratio_w > 1) {
    frac = [
      ((x - left) / width) * ratio_w - 0.5 * ratio_w + 0.5,
      (y - top) / height,
    ];
  } else {
    frac = [
      (x - left) / width,
      ((y - top) / height) * ratio_h - 0.5 * ratio_h + 0.5,
    ];
  }

  return [canvas.width * frac[0], canvas.height * frac[1]];
}

const mouseMoveEvent = ref<MouseEvent>();

const mousePos = computed(() => {
  if (!mouseMoveEvent.value) {
    return { x: 0, y: 0 };
  }
  return {
    x: mouseMoveEvent.value.clientX,
    y: mouseMoveEvent.value.clientY,
  };
});

function doRectanglesOverlap(
  recA: Rectangle<unknown>,
  recB: Rectangle<unknown>,
): boolean {
  const noHOverlap =
    recB.x >= recA.x + recA.width || recA.x >= recB.x + recB.width;

  if (noHOverlap) {
    return false;
  }

  const noVOverlap =
    recB.y >= recA.y + recA.height || recA.y >= recB.y + recB.height;

  return !noVOverlap;
}

const hoveredBoxAnnotations = computed(() => {
  if (
    !pickingCanvas.value ||
    pickingCanvas.value.width === 0 ||
    !annotationsTree ||
    !boxAnnotations.value ||
    !pickingCtx.value
  ) {
    return [];
  }

  const { x, y } = mousePos.value;
  const [canvasX, canvasY] = displayToPixel(x, y, pickingCanvas.value);

  const pixelRectangle = new Rectangle({
    x: canvasX,
    y: canvasY,
    width: 2,
    height: 2,
  });

  return annotationsTree
    .retrieve(pixelRectangle)
    .filter((rect) => doRectanglesOverlap(rect, pixelRectangle))
    .map((hit) => hit.data)
    .filter((annoIndex) => annoIndex != undefined)
    .map((annoIndex) => boxAnnotations.value[annoIndex]);
});

const mouseInComponent = ref(false);

const popupAnnotations = computed(() => {
  if (!mouseInComponent.value) return [];
  return hoveredBoxAnnotations.value;
});

onMounted(() => {
  function onResize(entries: ResizeObserverEntry[]) {
    const entry = entries[entries.length - 1];
    const { width, height, top, left } = entry.target.getBoundingClientRect();
    rect.value = { width, height, top, left };
  }

  resizeObserver = new ResizeObserver(onResize);

  if (visibleCanvas.value) {
    resizeObserver.observe(visibleCanvas.value);
  }
});

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
});

function onMouseMove(event: MouseEvent) {
  mouseInComponent.value = true;
  mouseMoveEvent.value = event;
}
</script>

<template>
  <canvas
    ref="visibleCanvas"
    style="
      width: 100%;
      position: absolute;
      left: 0;
      top: 0;
      height: 100%;
      object-fit: contain;
    "
  />
  <canvas
    ref="pickingCanvas"
    style="
      opacity: 0;
      width: 100%;
      position: absolute;
      left: 0;
      top: 0;
      height: 100%;
      object-fit: contain;
    "
    @mouseleave="mouseInComponent = false"
    @mousemove="onMouseMove"
  />
  <AnnotationsPopup
    :popup-annotations="popupAnnotations"
    :popup-position="mousePos"
    :relative-parent="pickingCanvas"
    :container="popupContainer"
    :group-by-model="groupByModel"
  />
</template>
