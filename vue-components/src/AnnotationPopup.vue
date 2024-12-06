<script setup lang="ts">
import { ref, toRefs } from "vue";
import { useTooltipPositioning } from "./utils.js";
import type { ClassificationAugmented } from "./annotations.js";

const props = defineProps<{
  popupAnnotations: ClassificationAugmented[];
  popupPosition: { x: number; y: number };
  relativeParent: Element | undefined;
  container: Element | undefined | null;
}>();
const { popupAnnotations, popupPosition, relativeParent, container } =
  toRefs(props);

const labelContainer = ref<HTMLElement>();

const tooltipPosition = useTooltipPositioning(
  labelContainer,
  popupPosition,
  relativeParent,
  container,
);
</script>

<template>
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
</template>
