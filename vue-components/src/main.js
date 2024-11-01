import ImageDetection from "./ImageDetection.vue";

const components = {
  ImageDetection,
};

export function install(Vue) {
  Object.entries(components).forEach(([name, component]) => {
    Vue.component(name, component);
  });
}
