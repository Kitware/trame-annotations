<script setup lang="ts">
import { ref, computed, watchEffect, defineProps, toRefs } from "vue";
import { Quadtree, Rectangle } from "@timohausmann/quadtree-ts";
import type { BoxAnnotationAugmented } from "./annotations.js";
import AnnotationsPopup from "./AnnotationPopup.vue";
import { useDevicePixelRatio, useResizeObserver } from "./utils.js";

const props = defineProps<{
  boxAnnotations: BoxAnnotationAugmented[];
  imageSize: { width: number; height: number };
  lineWidth: number;
  lineOpacity: number;
  popupContainer: Element | undefined | null;
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

const dpi = useDevicePixelRatio();

const rect = useResizeObserver(visibleCanvas);

const displayScale = computed(() => {
  if (!rect.value) return 1;
  return props.imageSize.width / rect.value.width;
});

const lineWidthInDisplay = computed(
  () => lineWidth.value * dpi.pixelRatio.value * displayScale.value,
);

// Draw visible annotations
watchEffect(() => {
  if (!visibleCanvas.value || !visibleCtx.value) return;

  const canvas = visibleCanvas.value;
  const ctx = visibleCtx.value;

  canvas.width = props.imageSize.width;
  canvas.height = props.imageSize.height;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.globalCompositeOperation = "lighter";
  ctx.lineWidth = lineWidthInDisplay.value;
  const alpha = lineOpacity.value;

  props.boxAnnotations.forEach(({ color, bbox }) => {
    ctx.strokeStyle = `rgba(${[...color, alpha].join(",")})`;
    ctx.strokeRect(bbox[0], bbox[1], bbox[2], bbox[3]);
  });
});

// Draw picking annotations
let annotationsTree: Quadtree<Rectangle<number>> | undefined = undefined;

watchEffect(() => {
  if (!pickingCanvas.value || !pickingCtx.value) return;

  const canvas = pickingCanvas.value;
  const ctx = pickingCtx.value;

  canvas.width = props.imageSize.width;
  canvas.height = props.imageSize.height;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  annotationsTree = new Quadtree({
    width: canvas.width,
    height: canvas.height,
    maxLevels: 8,
    maxObjects: 10,
  });

  props.boxAnnotations.forEach((annotation, i) => {
    const treeNode = new Rectangle({
      x: annotation.bbox[0],
      y: annotation.bbox[1],
      width: annotation.bbox[2],
      height: annotation.bbox[3],
      data: i,
    });
    annotationsTree!.insert(treeNode);
    ctx.fillStyle = "rgb(255, 0, 0)";
    ctx.fillRect(
      annotation.bbox[0],
      annotation.bbox[1],
      annotation.bbox[2],
      annotation.bbox[3],
    );
  });
});

function displayToPixel(
  x: number,
  y: number,
  canvas: HTMLCanvasElement,
): [number, number] {
  const { left, width, top, height } = canvas.getBoundingClientRect();

  return [
    (canvas.width * (x - left)) / width,
    (canvas.height * (y - top)) / height,
  ];
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
</script>

<template>
  <canvas
    ref="visibleCanvas"
    style="width: 100%; position: absolute; left: 0; top: 0"
  />
  <canvas
    ref="pickingCanvas"
    style="opacity: 0; width: 100%; position: absolute; left: 0; top: 0"
    @mouseenter="mouseInComponent = true"
    @mouseleave="mouseInComponent = false"
    @mousemove="mouseMoveEvent = $event"
  />
  <AnnotationsPopup
    :popup-annotations="popupAnnotations"
    :popup-position="mousePos"
    :relative-parent="pickingCanvas"
    :container="popupContainer"
  />
</template>
