<script setup lang="ts">
import {
  ref,
  watchEffect,
  computed,
  onMounted,
  unref,
  type MaybeRef,
} from "vue";

import { Quadtree, Rectangle } from "@timohausmann/quadtree-ts";
import { useDevicePixelRatio, useResizeObserver } from "./utils.js";

type Color = readonly [number, number, number];

const CATEGORY_COLORS: Color[] = [
  [255, 0, 0],
  [0, 255, 0],
  [0, 0, 255],
  [255, 255, 0],
  [255, 0, 255],
  [0, 255, 255],
];

const LINE_OPACITY = 0.9;
const LINE_WIDTH = 2; // in pixels

type Box = [number, number, number, number];

type Classification = {
  category_id: number;
  id?: number;
  label?: string; // fallback if category_id has no match
};

type BoxAnnotation = Classification & {
  bbox: Box;
};

type Annotation = Classification | BoxAnnotation;

type ClassificationWithColor = Classification & {
  color: Color;
};

type BoxAnnotationWithColor = BoxAnnotation & {
  color: Color;
};

type AnnotationWithColor = ClassificationWithColor | BoxAnnotationWithColor;

type Category = {
  name: string;
};

const TOOLTIP_OFFSET = [8, 8];
const TOOLTIP_PADDING = 16; // fudge to keep tooltip from clipping/overflowing. In pixels

let annotationsTree: Quadtree<Rectangle<number>> | undefined = undefined;

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

const props = defineProps<{
  identifier: MaybeRef<string>;
  src: MaybeRef<string>;
  annotations?: MaybeRef<Annotation[]> | null;
  categories?: MaybeRef<Record<PropertyKey, Category>> | null;
  containerSelector?: MaybeRef<string> | null;
  lineWidth?: MaybeRef<number> | null;
  lineOpacity?: MaybeRef<number> | null;
  selected?: MaybeRef<boolean>;
}>();

// withDefaults, toRefs, and handle null | Refs
const annotations = computed(() => unref(props.annotations) ?? []);
const categories = computed(() => unref(props.categories) ?? {});
const containerSelector = computed(() => unref(props.containerSelector) ?? "");
const lineOpacity = computed(() => unref(props.lineOpacity) ?? LINE_OPACITY);
const lineWidth = computed(() => unref(props.lineWidth) ?? LINE_WIDTH);

const visibleCanvas = ref<HTMLCanvasElement>();
const visibleCtx = computed(() =>
  visibleCanvas.value?.getContext("2d", { alpha: true }),
);
const pickingCanvas = ref<HTMLCanvasElement>();
const pickingCtx = computed(() =>
  pickingCanvas.value?.getContext("2d", { willReadFrequently: true }),
);
const labelContainer = ref<HTMLUListElement>();

const imageSize = ref({ width: 0, height: 0 });
const img = ref<HTMLImageElement>();
const onImageLoad = () => {
  imageSize.value = {
    width: img.value?.naturalWidth ?? 0,
    height: img.value?.naturalHeight ?? 0,
  };
};

const annotationsWithColor = computed(() => {
  return annotations.value.map((annotation) => {
    const mutex = annotation.category_id ?? 0;
    const color = CATEGORY_COLORS[mutex % CATEGORY_COLORS.length];
    return { ...annotation, color };
  });
});

const annotationsByType = computed(() =>
  annotationsWithColor.value.reduce(
    (acc, annotation) => {
      if ("bbox" in annotation) {
        acc.boxAnnotations.push(annotation);
      } else {
        acc.classifications.push(annotation);
      }
      return acc;
    },
    {
      boxAnnotations: [] as BoxAnnotationWithColor[],
      classifications: [] as ClassificationWithColor[],
    },
  ),
);

const boxAnnotations = computed(() => annotationsByType.value.boxAnnotations);
const classifications = computed(() => annotationsByType.value.classifications);

const dpi = useDevicePixelRatio();

const { width } = useResizeObserver(visibleCanvas);

const displayScale = computed(() => {
  if (!visibleCanvas.value) return 1;
  return imageSize.value.width / width.value;
});

const lineWidthInDisplay = computed(
  () => lineWidth.value * dpi.pixelRatio.value * displayScale.value,
);

// draw visible annotations
watchEffect(() => {
  if (!visibleCanvas.value || !visibleCtx.value) {
    return;
  }
  const canvas = visibleCanvas.value;
  const ctx = visibleCtx.value;

  canvas.width = imageSize.value.width;
  canvas.height = imageSize.value.height;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.globalCompositeOperation = "lighter"; // additive blend mode
  ctx.lineWidth = lineWidthInDisplay.value;
  const alpha = lineOpacity.value;
  boxAnnotations.value.forEach(({ color, bbox }) => {
    ctx.strokeStyle = `rgba(${[...color, alpha].join(",")})`;
    ctx.strokeRect(bbox[0], bbox[1], bbox[2], bbox[3]);
  });
});

// draw picking annotations
watchEffect(() => {
  if (!pickingCtx.value || !pickingCanvas.value) {
    return;
  }
  const canvas = pickingCanvas.value;
  const ctx = pickingCtx.value;

  canvas.width = imageSize.value.width;
  canvas.height = imageSize.value.height;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  annotationsTree = new Quadtree({
    width: canvas.width,
    height: canvas.height,
    maxLevels: 8,
    maxObjects: 10,
  });

  boxAnnotations.value.forEach((annotation, i) => {
    const treeNode = new Rectangle({
      x: annotation.bbox[0],
      y: annotation.bbox[1],
      width: annotation.bbox[2],
      height: annotation.bbox[3],
      data: i,
    });
    annotationsTree?.insert(treeNode);
    ctx.fillStyle = `rgb(255, 0, 0)`;
    ctx.fillRect(
      annotation.bbox[0],
      annotation.bbox[1],
      annotation.bbox[2],
      annotation.bbox[3],
    );
  });
});

interface HoverEvent {
  id: string;
}

type Events = {
  hover: [HoverEvent];
};

const emit = defineEmits<Events>();

function hideLabel() {
  if (labelContainer.value) labelContainer.value.style.visibility = "hidden";
}

onMounted(hideLabel);

function mouseEnter() {
  emit("hover", { id: unref(props.identifier) });
}
function mouseLeave() {
  emit("hover", { id: "" });
  hideLabel();
}

function displayToPixel(
  x: number,
  y: number,
  canvas: HTMLCanvasElement,
): [number, number] {
  const canvasBounds = canvas.getBoundingClientRect();

  const pixelX = (canvas.width * (x - canvasBounds.left)) / canvasBounds.width;
  const pixelY = (canvas.height * (y - canvasBounds.top)) / canvasBounds.height;

  return [pixelX, pixelY];
}

const mounted = ref(false);
onMounted(() => {
  mounted.value = true;
});
const container = computed(() => {
  if (!mounted.value || !containerSelector.value) return null;
  return document.querySelector(containerSelector.value);
});

const makeAnnotationLabel = (annotation: AnnotationWithColor) => {
  const { category_id, label, color } = annotation;
  const name = categories.value[category_id]?.name ?? label ?? "Unknown";

  const category = document.createElement("li");
  const dot = document.createElement("span");
  dot.style.backgroundColor = `rgb(${color.join(",")})`;
  dot.style.width = "10px";
  dot.style.height = "10px";
  dot.style.borderRadius = "50%";
  dot.style.display = "inline-block";
  dot.style.marginRight = "0.4rem";
  category.appendChild(dot);
  const text = document.createElement("span");
  text.textContent = name;
  category.appendChild(text);
  return category;
};

function mouseMove(e: MouseEvent) {
  if (
    !pickingCanvas.value ||
    pickingCanvas.value.width === 0 ||
    !labelContainer.value ||
    !annotationsTree ||
    !categories.value ||
    !props.annotations
  ) {
    return;
  }
  const ctx = pickingCtx.value;
  if (!ctx) {
    return;
  }

  const [pixelX, pixelY] = displayToPixel(
    e.clientX,
    e.clientY,
    pickingCanvas.value,
  );
  const pixelValue = ctx.getImageData(pixelX, pixelY, 1, 1).data[0];
  const pickedSomething = pixelValue > 0;

  if (!pickedSomething) {
    labelContainer.value.style.visibility = "hidden";
    return;
  }

  labelContainer.value.style.visibility = "visible";

  const pixelRectangle = new Rectangle({
    x: pixelX,
    y: pixelY,
    width: 2,
    height: 2,
  });
  const hits = annotationsTree
    .retrieve(pixelRectangle)
    .filter((rect) => doRectanglesOverlap(rect, pixelRectangle))
    .filter((hit) => hit.data != undefined)
    .map((hit) => {
      const annotation = boxAnnotations.value[hit.data!];
      return annotation;
    })
    .map(makeAnnotationLabel);

  labelContainer.value.replaceChildren(...hits);

  // Position the tooltip
  const [x, y] = [e.offsetX, e.offsetY];
  let posX = x + TOOLTIP_OFFSET[0];
  let posY = y + TOOLTIP_OFFSET[1];

  const tooltipRect = labelContainer.value.getBoundingClientRect();
  const parentRect = pickingCanvas.value.getBoundingClientRect();
  const containerRect = container.value?.getBoundingClientRect() ?? {
    left: 0,
    top: 0,
    width: window.innerWidth,
    height: window.innerHeight,
  };

  const toolTipInContainer = {
    left: parentRect.left + posX - containerRect.left,
    top: parentRect.top + posY - containerRect.top,
    width: tooltipRect.width + TOOLTIP_PADDING,
    height: tooltipRect.height + TOOLTIP_PADDING,
  };

  // if text goes off the edge, move up and/or left
  if (
    toolTipInContainer.left + toolTipInContainer.width >
    containerRect.width
  ) {
    posX = x - tooltipRect.width - TOOLTIP_OFFSET[0];
  }
  if (
    toolTipInContainer.top + toolTipInContainer.height >
    containerRect.height
  ) {
    posY = y - tooltipRect.height - TOOLTIP_OFFSET[1];
  }

  labelContainer.value.style.left = `${posX}px`;
  labelContainer.value.style.top = `${posY}px`;
}

const classificationsContainer = ref<HTMLUListElement>();

watchEffect(() => {
  if (!classificationsContainer.value) return;
  if (!classifications.value.length) {
    classificationsContainer.value.style.visibility = "hidden";
    return;
  }
  classificationsContainer.value.style.visibility = "visible";
  classificationsContainer.value.replaceChildren(
    ...classifications.value.map(makeAnnotationLabel),
  );
});

const borderSize = computed(() => (props.selected ? "4" : "0"));

const src = computed(() => unref(props.src));
</script>

<template>
  <div style="position: relative">
    <img
      ref="img"
      :src="src"
      :style="{ outlineWidth: borderSize + 'px' }"
      style="width: 100%; outline-style: dotted; outline-color: red"
      @load="onImageLoad"
    />
    <canvas
      ref="visibleCanvas"
      style="width: 100%; position: absolute; left: 0; top: 0"
    />
    <canvas
      ref="pickingCanvas"
      style="opacity: 0; width: 100%; position: absolute; left: 0; top: 0"
      @mouseenter="mouseEnter"
      @mousemove="mouseMove"
      @mouseleave="mouseLeave"
    />
    <ul
      ref="labelContainer"
      style="
        position: absolute;
        z-index: 10;
        padding: 0.4rem;
        white-space: pre;
        font-size: small;
        border-radius: 0.2rem;
        border-color: rgba(127, 127, 127, 0.75);
        border-style: solid;
        border-width: thin;
        background-color: white;
        list-style-type: none;
      "
    />
    <ul
      ref="classificationsContainer"
      style="
        top: 0.4rem;
        left: 0.4rem;
        margin: 0;
        pointer-events: none;
        position: absolute;
        padding: 0.4rem;
        white-space: pre;
        font-size: small;
        border-radius: 0.2rem;
        border-color: rgba(127, 127, 127, 0.75);
        border-style: solid;
        border-width: thin;
        background-color: white;
        list-style-type: none;
      "
    />
  </div>
</template>
