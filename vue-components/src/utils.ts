// Modified from vueuse
import { ref } from "vue";
import { getCurrentScope, onScopeDispose } from "vue";

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
 *
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
