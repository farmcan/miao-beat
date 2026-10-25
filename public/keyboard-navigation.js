// Keep the full keyboard reachable without relying on a drag gesture.
const mounted = new WeakMap();

export function mountKeyboardNavigation(root = document) {
  const scroller = root.querySelector('.melody-scroll');
  const keys = root.querySelector('#melodyKeys');
  const navigation = root.querySelector('#keyboardNavigation');
  const lower = root.querySelector('#keyboardLower');
  const higher = root.querySelector('#keyboardHigher');
  if (!scroller || !keys || !navigation || !lower || !higher) return null;
  if (mounted.has(scroller)) return mounted.get(scroller);

  const win = scroller.ownerDocument.defaultView;
  const reducedMotion = win.matchMedia?.('(prefers-reduced-motion: reduce)');
  let frame = 0;
  const maximum = () => Math.max(0, scroller.scrollWidth - scroller.clientWidth);
  function update() {
    frame = 0;
    const max = maximum();
    const overflowing = scroller.clientWidth > 0 && !keys.hidden && max > 1;
    navigation.hidden = !overflowing;
    lower.disabled = !overflowing || scroller.scrollLeft <= 1;
    higher.disabled = !overflowing || scroller.scrollLeft >= max - 1;
  }
  function schedule() {
    if (!frame) frame = win.requestAnimationFrame(update);
  }
  function move(direction) {
    const left = Math.max(0, Math.min(maximum(), scroller.scrollLeft + direction * Math.max(1, Math.round(scroller.clientWidth * .9))));
    scroller.scrollTo({left, behavior: reducedMotion?.matches ? 'auto' : 'smooth'});
    schedule();
  }
  const goLower = () => move(-1);
  const goHigher = () => move(1);
  lower.addEventListener('click', goLower);
  higher.addEventListener('click', goHigher);
  scroller.addEventListener('scroll', schedule, {passive: true});
  win.addEventListener('resize', schedule);
  const resizeObserver = win.ResizeObserver ? new win.ResizeObserver(schedule) : null;
  resizeObserver?.observe(scroller);
  resizeObserver?.observe(keys);
  const mutationObserver = new win.MutationObserver(schedule);
  mutationObserver.observe(keys, {childList: true, attributes: true, attributeFilter: ['hidden']});
  const surface = root.querySelector('#playingSurface');
  if (surface) mutationObserver.observe(surface, {attributes: true, attributeFilter: ['data-instrument']});

  const controller = {update: schedule, destroy() {
    if (frame) win.cancelAnimationFrame(frame);
    lower.removeEventListener('click', goLower);
    higher.removeEventListener('click', goHigher);
    scroller.removeEventListener('scroll', schedule);
    win.removeEventListener('resize', schedule);
    resizeObserver?.disconnect();
    mutationObserver.disconnect();
    navigation.hidden = true;
    mounted.delete(scroller);
  }};
  mounted.set(scroller, controller);
  update();
  return controller;
}
