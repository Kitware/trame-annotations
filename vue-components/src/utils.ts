import {
  ref,
  type Ref,
  getCurrentScope,
  onScopeDispose,
  watchEffect,
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

export function useResizeObserver(element: Ref<HTMLElement | undefined>) {
  const width = ref(0);
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
      for (const entry of entries) {
        width.value = entry.contentRect.width;
      }
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
    width.value = currentElement.clientWidth;
  });

  tryOnScopeDispose(cleanup);

  return {
    width,
  };
}
