<script setup lang="ts">
import { ref, toRefs, computed } from "vue";
import { useTooltipPositioning } from "./utils.js";
import type { ClassificationAugmented } from "./annotations.js";

const props = defineProps<{
  popupAnnotations: ClassificationAugmented[];
  popupPosition: { x: number; y: number };
  groupByModel: boolean;
  relativeParent: Element | undefined;
  container: Element | undefined | null;
}>();
const {
  popupAnnotations,
  popupPosition,
  relativeParent,
  container,
  groupByModel,
} = toRefs(props);

const groupedAnnotations = computed(() => {
  if (!groupByModel.value) {
    return undefined;
  }

  return popupAnnotations.value.reduce(
    (acc, curr) => {
      const { model_id } = curr;

      if (model_id == undefined) {
        return acc;
      }

      let modelAnnotations = acc[model_id];

      if (modelAnnotations == undefined) {
        modelAnnotations = {
          name: curr.modelName || "",
          annotations: [],
        };

        acc[model_id] = modelAnnotations;
      }

      modelAnnotations.annotations.push(curr);

      return acc;
    },
    {} as {
      [modelId: number]: {
        name: string;
        annotations: ClassificationAugmented[];
      };
    },
  );
});
const labelContainer = ref<HTMLElement>();

const tooltipPosition = useTooltipPositioning(
  labelContainer,
  popupPosition,
  relativeParent,
  container,
);
</script>

<template>
  <div
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
    <template v-if="groupedAnnotations">
      <ul
        v-for="(model, modelId) of groupedAnnotations"
        :key="modelId"
        style="list-style-type: none; padding: 0"
      >
        <li>
          <span style="font-weight: 500; font-style: italic">
            {{ model.name }}
          </span>
          <ul style="list-style-type: none; padding-left: 1rem">
            <li
              v-for="annotation in model.annotations"
              :key="annotation.id"
              :style="{ display: 'flex', alignItems: 'center' }"
            >
              <!-- colored dot -->
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
        </li>
      </ul>
    </template>
    <ul v-else style="list-style-type: none; padding: 0">
      <li
        v-for="annotation in popupAnnotations"
        :key="annotation.id"
        :style="{ display: 'flex', alignItems: 'center' }"
      >
        <!-- colored dot -->
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
  </div>
</template>
