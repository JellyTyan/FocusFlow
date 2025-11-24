import { createApp } from 'vue';
import { createPinia } from 'pinia';
import './style.css';
import App from './App.vue';
import router from './router';

const app = createApp(App);
const pinia = createPinia();

type LazyElement = HTMLElement & {
  __lazyObserver?: IntersectionObserver;
  __lazyAnimated?: boolean;
};

app.directive('lazy-show', {
  mounted(el: LazyElement) {
    if (el.__lazyAnimated) return;

    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.45s ease, transform 0.45s ease';

    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting && !el.__lazyAnimated) {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
            el.__lazyAnimated = true;
            observer.disconnect();
          }
        });
      },
      { threshold: 0.15 }
    );

    observer.observe(el);
    el.__lazyObserver = observer;
  },
  unmounted(el: LazyElement) {
    el.__lazyObserver?.disconnect();
  },
});

app.use(pinia);
app.use(router);
app.mount('#app');
