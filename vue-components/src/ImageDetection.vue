<script setup lang="ts">
import { ref, computed, unref, type MaybeRef } from "vue";
import { useSelector } from "./utils.js";
import {
  CATEGORY_COLORS,
  MISSING_CATEGORY,
  type Annotation,
  type BoxAnnotationAugmented,
  type ClassificationAugmented,
} from "./annotations.js";
import BoxAnnotations from "./BoxAnnotations.vue";
import ClassificationAnnotations from "./ClassificationAnnotations.vue";

const LINE_OPACITY = 0.9;
const LINE_WIDTH = 2; // in pixels

type Category = {
  name: string;
};

type TrameProp<T> = MaybeRef<T | null>;

const props = defineProps<{
  identifier?: TrameProp<string>;
  src: TrameProp<string>;
  annotations?: TrameProp<Annotation[]>;
  categories?: TrameProp<Record<number, Category>>;
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
      const color =
        category_id != undefined
          ? CATEGORY_COLORS[category_id % CATEGORY_COLORS.length]
          : MISSING_CATEGORY;

      const category =
        categories.value[category_id]?.name ?? label ?? "Unknown";
      const scoreStr = score != undefined ? ` ${Math.round(score * 100)}%` : "";
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

type HoverEvent = {
  id: string;
};

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

const tooltipContainer = useSelector(containerSelector);

const borderSize = computed(() => (props.selected ? "4" : "0"));

const src = computed(() => unref(props.src) ?? undefined);
</script>

<template>
  <div
    style="position: relative"
    @mouseenter="mouseEnter"
    @mouseleave="mouseLeave"
  >
    <img
      ref="img"
      :src="src"
      :style="{ outlineWidth: borderSize + 'px' }"
      style="width: 100%; outline-style: dotted; outline-color: red"
      @load="onImageLoad"
    />
    <BoxAnnotations
      :box-annotations="boxAnnotations"
      :image-size="imageSize"
      :line-width="lineWidth"
      :line-opacity="lineOpacity"
      :popup-container="tooltipContainer"
    />
    <ClassificationAnnotations
      style="position: absolute; top: 0.4rem; left: 0.4rem; margin: 0"
      :classifications="classifications"
      :popup-container="tooltipContainer"
    />
  </div>
</template>
