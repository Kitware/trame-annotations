<script setup lang="ts">
import { ref, computed } from "vue";
import { type ClassificationAugmented } from "./annotations.js";
import AnnotationsPopup from "./AnnotationPopup.vue";

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
  return { x: left + width / 2, y: top + height / 2 };
});

const firstClassColor = computed(() => {
  if (!props.classifications.length) return "transparent";
  return `rgb(${props.classifications[0].color.join(",")})`;
});

const popupAnnotations = computed(() => {
  if (showClasses.value) return props.classifications;
  return [];
});
</script>

<template>
  <div ref="classesDot" style="position: relative; margin: 0">
    <span
      :style="{
        backgroundColor: firstClassColor,
        width: '14px',
        height: '14px',
        borderRadius: '50%',
        display: 'inline-block',
      }"
      @mouseenter="showClasses = true"
      @mouseleave="showClasses = false"
    ></span>

    <AnnotationsPopup
      :popup-annotations="popupAnnotations"
      :popup-position="popupPosition"
      :relative-parent="classesDot"
      :container="popupContainer"
    />
  </div>
</template>
