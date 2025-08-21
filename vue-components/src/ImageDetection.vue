<script setup lang="ts">
import {
  ref,
  computed,
  unref,
  type MaybeRef,
  onMounted,
  onBeforeUnmount,
} from "vue";
import { useSelector } from "./utils";
import {
  CATEGORY_COLORS,
  MODEL_COLORS,
  MISSING_CATEGORY,
  type Annotation,
  type BoxAnnotationAugmented,
  type ClassificationAugmented,
} from "./annotations";
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
  annotations?: TrameProp<Annotation[] | { [model_id: number]: Annotation[] }>;
  categories?: TrameProp<Record<number, Category>>;
  models?: TrameProp<Record<number, Category>>;
  containerSelector?: TrameProp<string>;
  lineWidth?: TrameProp<number>;
  lineOpacity?: TrameProp<number>;
  selected?: TrameProp<boolean>;
  scoreThreshold?: TrameProp<number>;
  colorBy: TrameProp<"category" | "model">;
}>();

// withDefaults, toRefs, and handle null | Refs
const annotations = computed(() => {
  const annotations = unref(props.annotations);

  if (!annotations) {
    return [];
  }

  if (Array.isArray(annotations)) {
    return annotations;
  }

  const flatAnnotations: Annotation[] = Object.entries(annotations)
    .map(([model_id, model_annotations]) => {
      return [model_id, unref(model_annotations)] as [string, Annotation[]];
    })
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    .filter(([model_id, model_annotations]) => {
      return model_annotations != undefined;
    })
    .map(([model_id, model_annotations]) => {
      return model_annotations.map((ann: Annotation) => ({
        ...ann,
        model_id: parseInt(model_id),
      }));
    })
    .flat();

  return flatAnnotations;
});
const categories = computed(() => unref(props.categories) ?? {});
const models = computed(() => unref(props.models) ?? {});
const containerSelector = computed(() => unref(props.containerSelector) ?? "");
const lineOpacity = computed(() => unref(props.lineOpacity) ?? LINE_OPACITY);
const lineWidth = computed(() => unref(props.lineWidth) ?? LINE_WIDTH);
const scoreThreshold = computed(() => unref(props.scoreThreshold) ?? 0);
const colorBy = computed(() => unref(props.colorBy) ?? "category");

const imageSize = ref({ width: 0, height: 0 });
const img = ref<HTMLImageElement>();
const ready = ref<boolean>(true);
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
      const { category_id, model_id, label, score } = annotation;

      let color = MISSING_CATEGORY;

      if (colorBy.value === "category" && category_id != undefined) {
        color = CATEGORY_COLORS[category_id % CATEGORY_COLORS.length];
      } else if (colorBy.value === "model" && model_id != undefined) {
        color = MODEL_COLORS[model_id % MODEL_COLORS.length];
      }

      const category =
        categories.value[category_id]?.name ?? label ?? "Unknown";
      const scoreStr = score != undefined ? ` ${Math.round(score * 100)}%` : "";
      const name = `${category}${scoreStr}`;

      const modelName =
        models.value[model_id!]?.name ?? `Unknown model (${model_id})`;
      return { ...annotation, color, name, modelName };
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

function mouseEnter() {
  const id = unref(props.identifier);
  if (id != undefined) {
    emit("hover", { id });
  }
}

function mouseLeave() {
  emit("hover", { id: "" });
}

const tooltipContainer = useSelector(containerSelector);

const borderSize = computed(() => (props.selected ? "4" : "0"));

const src = computed(() => unref(props.src) ?? undefined);

function onContainerTransitionStart(ev: Event) {
  ready.value = false;
  ev.target?.addEventListener("transitionend", onContainerTransitionEnd);
}

function onContainerTransitionEnd(ev: Event) {
  ready.value = true;
  ev.target?.removeEventListener("transitionend", onContainerTransitionEnd);
}

onMounted(() => {
  // If the container is being animated we shouldn't display the annotations or the underlying canvas
  // will not be sized correctly.
  tooltipContainer.value?.addEventListener(
    "transitionstart",
    onContainerTransitionStart,
  );
});

onBeforeUnmount(() => {
  tooltipContainer.value?.removeEventListener(
    "transitionstart",
    onContainerTransitionStart,
  );
  tooltipContainer.value?.removeEventListener(
    "transitionend",
    onContainerTransitionEnd,
  );
});
</script>

<template>
  <div
    style="position: relative; width: 100%; height: 100%"
    @mouseenter="mouseEnter"
    @mouseleave="mouseLeave"
  >
    <img
      ref="img"
      :src="src"
      :style="{ outlineWidth: borderSize + 'px' }"
      style="
        width: 100%;
        height: 100%;
        object-fit: contain;
        outline-style: dotted;
        outline-color: red;
      "
      @load="onImageLoad"
    />
    <BoxAnnotations
      v-if="ready && boxAnnotations.length > 0"
      :box-annotations="boxAnnotations"
      :image-size="imageSize"
      :line-width="lineWidth"
      :line-opacity="lineOpacity"
      :popup-container="tooltipContainer"
      :group-by-model="colorBy === 'model'"
    />
    <ClassificationAnnotations
      v-if="ready && classifications.length > 0"
      style="position: absolute; top: 0.4rem; left: 0.4rem; margin: 0"
      :classifications="classifications"
      :popup-container="tooltipContainer"
      :group-by-model="colorBy === 'model'"
    />
  </div>
</template>
