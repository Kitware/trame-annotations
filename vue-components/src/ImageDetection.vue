<script setup lang="ts">
import { ref, watchEffect, computed, unref, type MaybeRef } from "vue";

import { Quadtree, Rectangle } from "@timohausmann/quadtree-ts";
import {
  useDevicePixelRatio,
  useResizeObserver,
  useSelector,
  useTooltipPositioning,
} from "./utils.js";

type Color = readonly [number, number, number];

const CATEGORY_COLORS: Color[] = [
  [255, 0, 0], // Red
  [0, 255, 0], // Green
  [0, 0, 255], // Blue
  [255, 165, 0], // Orange
  [0, 255, 255], // Cyan
  [255, 255, 0], // Yellow
  [255, 0, 255], // Magenta
  [255, 69, 0], // Orange Red
  [255, 20, 147], // Deep Pink
  [255, 215, 0], // Gold
];

const LINE_OPACITY = 0.9;
const LINE_WIDTH = 2; // in pixels

type Box = [number, number, number, number];

type Classification = {
  category_id: number;
  id?: number;
  label?: string; // fallback if category_id has no match
  score?: number;
};

type BoxAnnotation = Classification & {
  bbox: Box;
};

type Annotation = Classification | BoxAnnotation;

type AnnotationAugmentations = {
  color: Color;
  name: string;
};

type ClassificationAugmented = Classification & AnnotationAugmentations;

type BoxAnnotationAugmented = BoxAnnotation & AnnotationAugmentations;

type AnnotationAugmented = ClassificationAugmented | BoxAnnotationAugmented;

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
const labelContainer = ref<HTMLUListElement>();

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

function mouseEnter() {
  const id = unref(props.identifier);
  if (id != undefined) {
    emit("hover", { id });
  }
  mouseInComponent.value = true;
}

function mouseLeave() {
  emit("hover", { id: "" });
  mouseInComponent.value = false;
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

const hoveredBoxAnnotations = ref<AnnotationAugmented[]>([]);

const mousePos = ref({ x: 0, y: 0 });

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

  const pixelRectangle = new Rectangle({
    x: pixelX,
    y: pixelY,
    width: 2,
    height: 2,
  });

  const hits = annotationsTree
    .retrieve(pixelRectangle)
    .filter((rect) => doRectanglesOverlap(rect, pixelRectangle))
    .map((hit) => hit.data)
    .filter((annoIndex) => annoIndex != undefined)
    .map((annoIndex) => boxAnnotations.value[annoIndex]);

  hoveredBoxAnnotations.value = hits;

  mousePos.value = {
    x: e.clientX,
    y: e.clientY,
  };
}

const classesHovered = ref(false);

const popupAnnotations = computed(() => {
  if (!mouseInComponent.value) return [];
  if (classesHovered.value) return classifications.value;
  return hoveredBoxAnnotations.value;
});

const classesDot = ref<HTMLDivElement>();

const popupPosition = computed(() => {
  if (classesHovered.value && classesDot.value) {
    const { left, top, width, height } =
      classesDot.value.getBoundingClientRect();
    return { x: left + width / 2, y: top + height / 2 };
  }
  return mousePos.value;
});

const tooltipContainer = useSelector(containerSelector);

const tooltipPosition = useTooltipPositioning(
  labelContainer,
  popupPosition,
  pickingCanvas,
  tooltipContainer,
);

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
    @mouseenter="mouseEnter"
    @mousemove="mouseMove"
    @mouseleave="mouseLeave"
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
    <ul
      ref="labelContainer"
      :style="{
        position: 'absolute',
        visibility: popupAnnotations.length ? 'visible' : 'hidden',
        left: `${tooltipPosition.left}px`,
        top: `${tooltipPosition.top}px`,
        zIndex: 10,
        padding: '0.4rem',
        whiteSpace: 'pre',
        fontSize: 'small',
        borderRadius: '0.2rem',
        borderColor: 'rgba(127, 127, 127, 0.75)',
        borderStyle: 'solid',
        borderWidth: 'thin',
        backgroundColor: 'white',
        listStyleType: 'none',
        pointerEvents: 'none',
        margin: 0,
      }"
    >
      <li
        v-for="annotation in popupAnnotations"
        :key="annotation.id"
        :style="{ display: 'flex', alignItems: 'center' }"
      >
        <span
          :style="{
            backgroundColor: `rgb(${annotation.color.join(',')})`,
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            display: 'inline-block',
            marginRight: '0.4rem',
          }"
        ></span>
        <span>{{ annotation.name }}</span>
      </li>
    </ul>
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
        @mouseenter="classesHovered = true"
        @mouseleave="classesHovered = false"
      ></span>
    </div>
  </div>
</template>
