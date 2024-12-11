import {
  ref,
  type Ref,
  getCurrentScope,
  onScopeDispose,
  watchEffect,
  computed,
  type MaybeRef,
  onMounted,
  unref,
} from "vue";

/**
 * Call onScopeDispose() if it's inside an effect scope lifecycle, if not, do nothing
 *
 * @param fn
 */
export function tryOnScopeDispose(fn: () => void) {
  if (getCurrentScope()) {
    onScopeDispose(fn);
    return true;
  }
  return false;
}

/**
 * Reactively track `window.devicePixelRatio`.
 *  Modified from vueuse
 * @see https://github.com/vueuse/vueuse/blob/main/packages/core/useDevicePixelRatio/index.ts
 */
export function useDevicePixelRatio() {
  const pixelRatio = ref(1);

  if (window) {
    let media: MediaQueryList;

    function observe() {
      pixelRatio.value = window!.devicePixelRatio;
      cleanup();
      media = window!.matchMedia(`(resolution: ${pixelRatio.value}dppx)`);
      media.addEventListener("change", observe, { once: true });
    }

    function cleanup() {
      media?.removeEventListener("change", observe);
    }

    observe();
    tryOnScopeDispose(cleanup);
  }

  return { pixelRatio };
}

export type UseDevicePixelRatioReturn = ReturnType<typeof useDevicePixelRatio>;

type Rect = {
  width: number;
  height: number;
  top: number;
  left: number;
};

export function useResizeObserver(
  element: Ref<HTMLElement | undefined | null>,
) {
  const rect = ref<Rect>();
  let observer: ResizeObserver | null = null;
  let currentElement: HTMLElement | undefined;

  const cleanup = () => {
    if (observer) {
      observer.disconnect();
      observer = null;
    }
    currentElement = undefined;
  };

  const setupObserver = () => {
    observer = new ResizeObserver((entries) => {
      const entry = entries[entries.length - 1];
      const { width, height, top, left } = entry.target.getBoundingClientRect();
      rect.value = { width, height, top, left };
    });
  };

  watchEffect(() => {
    if (
      currentElement &&
      (!element.value || element.value !== currentElement)
    ) {
      cleanup();
    }

    if (!element.value) return;

    if (!observer) {
      setupObserver();
    }

    currentElement = element.value;
    observer?.observe(currentElement);
    const { width, height, top, left } = currentElement.getBoundingClientRect();
    rect.value = { width, height, top, left };
  });

  tryOnScopeDispose(cleanup);

  return rect;
}

type Position = {
  x: number;
  y: number;
};

type TooltipPosition = {
  left: number;
  top: number;
};

export function useTooltipPositioning(
  popup: Ref<HTMLElement | undefined | null>,
  position: Ref<Position>,
  parent: Ref<Element | undefined | null>,
  container: Ref<Element | undefined | null>,
  offset: number = 8,
  margin: number = 16,
) {
  const popupRect = useResizeObserver(popup);

  const tooltipPosition = computed<TooltipPosition>(() => {
    const pos = position.value;

    let left = pos.x + offset;
    let top = pos.y + offset;

    if (!popupRect.value || !parent.value) return { left, top };

    const rect = popupRect.value;

    const containerRect = container.value?.getBoundingClientRect() ?? {
      left: 0,
      top: 0,
      width: window.innerWidth,
      height: window.innerHeight,
    };

    const toolTipInContainer = {
      left: left - containerRect.left,
      top: top - containerRect.top,
      width: rect.width + margin,
      height: rect.height + margin,
    };

    // Adjust position to keep the tooltip within the container
    if (
      toolTipInContainer.left + toolTipInContainer.width >
      containerRect.width
    ) {
      left = pos.x - rect.width - offset;
    }
    if (left < containerRect.left) {
      left = containerRect.left;
    }

    if (
      toolTipInContainer.top + toolTipInContainer.height >
      containerRect.height
    ) {
      top = pos.y - rect.height - offset;
    }
    if (top < containerRect.top) {
      top = containerRect.top;
    }

    // put in parent coordinates for absolute positioning
    const parentRect = parent.value.getBoundingClientRect();
    left -= parentRect.left;
    top -= parentRect.top;

    return { left, top };
  });

  return tooltipPosition;
}

export const useSelector = (query: MaybeRef<string>) => {
  const mounted = ref(false);
  onMounted(() => {
    mounted.value = true;
  });

  const queryResult = computed(() => {
    const q = unref(query);
    if (!mounted.value || !q) return null;
    return document.querySelector(q);
  });

  return queryResult;
};
