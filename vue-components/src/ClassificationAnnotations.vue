<script setup lang="ts">
import { ref, computed } from "vue";
import { type ClassificationAugmented } from "./annotations.js";
import AnnotationsPopup from "./AnnotationPopup.vue";

const DOT_SPACING = 6;
const DOT_SIZE = 14;

const props = defineProps<{
  classifications: ClassificationAugmented[];
  popupContainer: Element | undefined | null;
}>();
const showClasses = ref(false);
const classesDot = ref<HTMLDivElement>();

const popupPosition = computed(() => {
  // need showClasses in here to trigger computation after layout changes
  if (!classesDot.value || !showClasses.value) return { x: 0, y: 0 };
  const { left, top, width, height } = classesDot.value.getBoundingClientRect();
  return { x: left + width / 2, y: top + height - 4 };
});

const classColors = computed(() => {
  if (!props.classifications.length) return [];
  return props.classifications
    .map(({ color }) => `rgb(${color.join(",")})`)
    .reverse();
});

const popupAnnotations = computed(() => {
  if (showClasses.value) return props.classifications;
  return [];
});
</script>

<template>
  <div
    ref="classesDot"
    style="position: relative; margin: 0"
    :style="{
      height: `${classColors.length * DOT_SPACING + DOT_SIZE}px`,
      width: `${DOT_SIZE}px`,
    }"
    @mouseenter="showClasses = true"
    @mouseleave="showClasses = false"
  >
    <span
      v-for="(color, i) in classColors"
      :key="i"
      :style="{
        top: `${classColors.length * DOT_SPACING - i * DOT_SPACING}px`,
        position: 'absolute',
        backgroundColor: color,
        width: `${DOT_SIZE}px`,
        height: `${DOT_SIZE}px`,
        borderRadius: '50%',
        boxShadow: '0 1px 1px rgba(0, 0, 0, 0.5)',
      }"
    ></span>

    <AnnotationsPopup
      :popup-annotations="popupAnnotations"
      :popup-position="popupPosition"
      :relative-parent="classesDot"
      :container="popupContainer"
    />
  </div>
</template>
