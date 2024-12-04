<script setup lang="ts">
import { ref, watchEffect, computed, unref, type MaybeRef } from "vue";

import { Quadtree, Rectangle } from "@timohausmann/quadtree-ts";
import {
  useDevicePixelRatio,
  useResizeObserver,
  useSelector,
} from "./utils.js";
import {
  CATEGORY_COLORS,
  type Annotation,
  type BoxAnnotationAugmented,
  type ClassificationAugmented,
} from "./annotations.js";
import AnnotationsPopup from "./AnnotationPopup.vue";

const LINE_OPACITY = 0.9;
const LINE_WIDTH = 2; // in pixels

type Category = {
  name: string;
};

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

type TrameProp<T> = MaybeRef<T | null>;

const props = defineProps<{
  identifier?: TrameProp<string>;
  src: TrameProp<string>;
  annotations?: TrameProp<Annotation[]>;
  categories?: TrameProp<Record<PropertyKey, Category>>;
  containerSelector?: TrameProp<string>;
  lineWidth?: TrameProp<number>;
  lineOpacity?: TrameProp<number>;
  selected?: TrameProp<boolean>;
  scoreThreshold?: TrameProp<number>;
}>();

// withDefaults, toRefs, and handle null | Refs
const annotations = computed(() => unref(props.annotations) ?? []);
const categories = computed(() => unref(props.categories) ?? {});
const containerSelector = computed(() => unref(props.containerSelector) ?? "");
const lineOpacity = computed(() => unref(props.lineOpacity) ?? LINE_OPACITY);
const lineWidth = computed(() => unref(props.lineWidth) ?? LINE_WIDTH);
const scoreThreshold = computed(() => unref(props.scoreThreshold) ?? 0);

const visibleCanvas = ref<HTMLCanvasElement>();
const visibleCtx = computed(() =>
  visibleCanvas.value?.getContext("2d", { alpha: true }),
);
const pickingCanvas = ref<HTMLCanvasElement>();
const pickingCtx = computed(() =>
  pickingCanvas.value?.getContext("2d", { willReadFrequently: true }),
);

const imageSize = ref({ width: 0, height: 0 });
const img = ref<HTMLImageElement>();
const onImageLoad = () => {
  imageSize.value = {
    width: img.value?.naturalWidth ?? 0,
    height: img.value?.naturalHeight ?? 0,
  };
};

const annotationsAugmented = computed(() => {
  return annotations.value
    .filter(({ score }) => score == undefined || score >= scoreThreshold.value)
    .map((annotation) => {
      const { category_id, label, score } = annotation;
      const mutex = category_id ?? 0;
      const color = CATEGORY_COLORS[mutex % CATEGORY_COLORS.length];

      const category =
        categories.value[category_id]?.name ?? label ?? "Unknown";
      const scoreStr = score != undefined ? ` ${score.toFixed(2)}` : "";
      const name = `${category}${scoreStr}`;
      return { ...annotation, color, name };
    });
});

const annotationsByType = computed(() =>
  annotationsAugmented.value.reduce(
    (acc, annotation) => {
      if ("bbox" in annotation) {
        acc.boxAnnotations.push(annotation);
      } else {
        acc.classifications.push(annotation);
      }
      return acc;
    },
    {
      boxAnnotations: [] as BoxAnnotationAugmented[],
      classifications: [] as ClassificationAugmented[],
    },
  ),
);

const boxAnnotations = computed(() => annotationsByType.value.boxAnnotations);
const classifications = computed(() => annotationsByType.value.classifications);

const dpi = useDevicePixelRatio();

const rect = useResizeObserver(visibleCanvas);

const displayScale = computed(() => {
  if (!visibleCanvas.value) return 1;
  return imageSize.value.width / rect.value.width;
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

const mouseInComponent = ref(false);

watchEffect(() => {
  if (!mouseInComponent.value) {
    // leaving
    emit("hover", { id: "" });
    return;
  }

  // entered
  const id = unref(props.identifier) ?? "";
  emit("hover", { id });
});

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

const hoveredBoxAnnotations = computed(() => {
  if (
    !pickingCanvas.value ||
    pickingCanvas.value.width === 0 ||
    !annotationsTree ||
    !categories.value ||
    !props.annotations ||
    !pickingCtx.value
  ) {
    return [];
  }

  const { x, y } = mousePos.value;
  const [pixelX, pixelY] = displayToPixel(x, y, pickingCanvas.value);

  const pixelRectangle = new Rectangle({
    x: pixelX,
    y: pixelY,
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

const showClasses = ref(false);

const popupAnnotations = computed(() => {
  if (!mouseInComponent.value) return [];
  if (showClasses.value) return classifications.value;
  return hoveredBoxAnnotations.value;
});

const classesDot = ref<HTMLDivElement>();

const popupPosition = computed(() => {
  if (showClasses.value && classesDot.value) {
    const { left, top, width, height } =
      classesDot.value.getBoundingClientRect();
    return { x: left + width / 2, y: top + height / 2 };
  }
  return mousePos.value;
});

const tooltipContainer = useSelector(containerSelector);

const firstClassColor = computed(() => {
  if (!classifications.value.length) return "transparent";
  return `rgb(${classifications.value[0].color.join(",")})`;
});

const borderSize = computed(() => (props.selected ? "4" : "0"));

const src = computed(() => unref(props.src) ?? undefined);
</script>

<template>
  <div
    style="position: relative"
    @mouseenter="mouseInComponent = true"
    @mouseleave="mouseInComponent = false"
    @mousemove="mouseMoveEvent = $event"
  >
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
    />
    <div
      v-if="classifications.length"
      ref="classesDot"
      style="position: absolute; top: 0.4rem; left: 0.4rem; margin: 0"
    >
      <span
        :style="{
          backgroundColor: firstClassColor,
          width: '14px',
          height: '14px',
          borderRadius: '50%',
          display: 'inline-block',
          marginRight: '0.4rem',
        }"
        @mouseenter="showClasses = true"
        @mouseleave="showClasses = false"
      ></span>
    </div>
    <AnnotationsPopup
      :popup-annotations="popupAnnotations"
      :popup-position="popupPosition"
      :relative-parent="pickingCanvas"
      :container="tooltipContainer"
    />
  </div>
</template>
