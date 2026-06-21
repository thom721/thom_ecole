<template>
  <Teleport to="body">
    <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0">
      <div v-if="show" class="modal-root">

        <!-- Backdrop -->
        <Transition name="backdrop-fade">
          <div
            v-if="show"
            class="modal-backdrop"
            @click="$emit('close')"
          />
        </Transition>

        <!-- Dialog -->
        <div class="modal-stage" role="dialog" aria-modal="true">
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 scale-95 translate-y-2"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95">
            <div
              v-if="show"
              class="modal-panel"
              :class="maxWidthClass"
            >

              <!-- Accent bar top -->
              <div class="modal-accent-bar" />

              <!-- Header -->
              <div class="flex items-center justify-between px-5 py-4 border-b border-white/[0.07]">
                <div class="modal-header-inner">
                  <!-- Icon slot or default -->
                  <div v-if="$slots.icon" class="modal-icon-wrap">
                    <slot name="icon" />
                  </div>
                  <div class="modal-title-block">
                    <slot name="title" />
                    <p v-if="$slots.subtitle" class="modal-subtitle">
                      <slot name="subtitle" />
                    </p>
                  </div>
                </div>

                <!-- Close -->
                <button
                  type="button"
                  class="modal-close-btn"
                  @click="$emit('close')"
                  aria-label="Fermer"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                    <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
                  </svg>
                </button>
              </div>

              <!-- Divider -->
              <div class="modal-divider" />

              <!-- Content -->
              <div class="modal-body">
                <slot name="content" />
              </div>

              <!-- Footer -->
              <template v-if="$slots.footer">
                <div class="modal-divider" />
                <div class="modal-footer">
                  <slot name="footer" />
                </div>
              </template>

            </div>
          </Transition>
        </div>

      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  show:     { type: Boolean, default: false },
  maxWidth: { type: String,  default: '2xl' },
});

defineEmits(['close']);

const maxWidthClass = computed(() => ({
  sm:  'mw-sm',
  md:  'mw-md',
  lg:  'mw-lg',
  xl:  'mw-xl',
  '2xl': 'mw-2xl',
  '3xl': 'mw-3xl',
  '4xl': 'mw-4xl',
}[props.maxWidth] ?? 'mw-2xl'));

// Lock body scroll when open
const lockScroll = () => document.body.style.overflow = 'hidden';
const unlockScroll = () => document.body.style.overflow = '';

// Close on Escape
const onKeyDown = (e) => { if (e.key === 'Escape' && props.show) emit('close'); };

import { getCurrentInstance } from 'vue';
const { emit } = getCurrentInstance();

onMounted(() => window.addEventListener('keydown', onKeyDown));
onUnmounted(() => { window.removeEventListener('keydown', onKeyDown); unlockScroll(); });

import { watch } from 'vue';
watch(() => props.show, (v) => v ? lockScroll() : unlockScroll(), { immediate: true });
</script>

<style scoped>
/* ── Root & backdrop ─────────────────────────────────────────────── */
.modal-root {
  position: fixed;
  inset: 0;
  z-index: 100;
  overflow-y: auto;
  font-family: 'Instrument Sans', 'DM Sans', 'Segoe UI', sans-serif;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(5, 8, 15, 0.72);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.modal-stage {
  position: relative;
  display: flex;
  min-height: 100%;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  pointer-events: none;
}

/* ── Panel ───────────────────────────────────────────────────────── */
.modal-panel {
  position: relative;
  pointer-events: all;
  width: 100%;
  background: #13171f;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 16px;
  box-shadow:
    0 0 0 1px rgba(255,255,255,0.04),
    0 32px 64px -12px rgba(0,0,0,0.6),
    0 0 80px -20px rgba(99, 133, 255, 0.08);
  overflow: hidden;
}

/* Accent bar — slim gradient stripe at top */
.modal-accent-bar {
  height: 2px;
  background: linear-gradient(90deg,
    transparent 0%,
    #4a7cff 20%,
    #6b9fff 50%,
    #4a7cff 80%,
    transparent 100%
  );
  opacity: 0.7;
}

/* ── Max widths ──────────────────────────────────────────────────── */
.mw-sm  { max-width: 24rem; }
.mw-md  { max-width: 28rem; }
.mw-lg  { max-width: 32rem; }
.mw-xl  { max-width: 36rem; }
.mw-2xl { max-width: 42rem; }
.mw-3xl { max-width: 52rem; }

/* ── Header ──────────────────────────────────────────────────────── */
.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem 1.125rem;
}

.modal-header-inner {
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
}

.modal-icon-wrap {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: rgba(74, 124, 255, 0.1);
  border: 1px solid rgba(74, 124, 255, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7aaeff;
  font-size: 15px;
  margin-top: 1px;
}

.modal-title-block {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Title is provided via slot — these are the default styles
   that will cascade into the slot content */
.modal-title-block :deep(h2),
.modal-title-block :deep(h3),
.modal-title-block :deep(span),
.modal-title-block :deep(p:first-child) {
  font-size: 15px;
  font-weight: 600;
  color: #e2e8f5;
  letter-spacing: -0.01em;
  line-height: 1.35;
  margin: 0;
}

.modal-subtitle {
  font-size: 12px;
  color: #5c6880;
  margin: 0;
  line-height: 1.45;
}

/* ── Close button ────────────────────────────────────────────────── */
.modal-close-btn {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: 7px;
  background: transparent;
  border: 1px solid transparent;
  color: #4a5568;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
  margin-top: 2px;
}
.modal-close-btn:hover {
  background: rgba(255,255,255,0.05);
  border-color: rgba(255,255,255,0.08);
  color: #9aa5bb;
}
.modal-close-btn:active {
  background: rgba(255,255,255,0.08);
}

/* ── Divider ─────────────────────────────────────────────────────── */
.modal-divider {
  height: 1px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(255,255,255,0.055) 15%,
    rgba(255,255,255,0.055) 85%,
    transparent 100%
  );
}

/* ── Body ────────────────────────────────────────────────────────── */
.modal-body {
  padding: 1.5rem;
  color: #8a95a8;
  font-size: 13.5px;
  line-height: 1.6;
}

/* Propagate nice defaults into slotted content */
.modal-body :deep(p) { color: #8a95a8; font-size: 13.5px; }
.modal-body :deep(strong) { color: #c8d2e0; font-weight: 600; }
.modal-body :deep(a) { color: #7aaeff; text-decoration: underline; text-underline-offset: 2px; }
.modal-body :deep(label) { color: #6b7a90; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; }

/* Input/select defaults inside modal */
.modal-body :deep(input),
.modal-body :deep(select),
.modal-body :deep(textarea) {
  width: 100%;
  background: #0d1017;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  padding: 8px 12px;
  color: #dde4f0;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  font-family: inherit;
}
.modal-body :deep(input:focus),
.modal-body :deep(select:focus),
.modal-body :deep(textarea:focus) {
  border-color: rgba(74, 124, 255, 0.5);
  box-shadow: 0 0 0 3px rgba(74, 124, 255, 0.1);
}
.modal-body :deep(input::placeholder),
.modal-body :deep(textarea::placeholder) {
  color: #34404f;
}

/* ── Footer ──────────────────────────────────────────────────────── */
.modal-footer {
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.625rem;
}

/* Button defaults inside footer */
.modal-footer :deep(button) {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
  font-family: inherit;
}

/* Primary action */
.modal-footer :deep(button[data-variant="primary"]),
.modal-footer :deep(.btn-primary) {
  background: linear-gradient(135deg, #3a6ee8, #5585f5);
  color: #fff;
  border-color: rgba(255,255,255,0.1);
  box-shadow: 0 2px 12px rgba(58, 110, 232, 0.3);
}
.modal-footer :deep(button[data-variant="primary"]:hover),
.modal-footer :deep(.btn-primary:hover) {
  background: linear-gradient(135deg, #4478f0, #6691f7);
  box-shadow: 0 4px 16px rgba(58, 110, 232, 0.4);
  transform: translateY(-1px);
}

/* Secondary / cancel */
.modal-footer :deep(button[data-variant="secondary"]),
.modal-footer :deep(.btn-secondary) {
  background: rgba(255,255,255,0.04);
  color: #7a8699;
  border-color: rgba(255,255,255,0.07);
}
.modal-footer :deep(button[data-variant="secondary"]:hover),
.modal-footer :deep(.btn-secondary:hover) {
  background: rgba(255,255,255,0.07);
  color: #aab5c8;
  border-color: rgba(255,255,255,0.11);
}

/* Danger */
.modal-footer :deep(button[data-variant="danger"]),
.modal-footer :deep(.btn-danger) {
  background: rgba(220, 60, 60, 0.1);
  color: #e57373;
  border-color: rgba(220, 60, 60, 0.2);
}
.modal-footer :deep(button[data-variant="danger"]:hover),
.modal-footer :deep(.btn-danger:hover) {
  background: rgba(220, 60, 60, 0.18);
  color: #ef9a9a;
  border-color: rgba(220, 60, 60, 0.3);
}

/* ── Transitions ─────────────────────────────────────────────────── */

/* Fade for root + backdrop */
.modal-fade-enter-active,
.modal-fade-leave-active,
.backdrop-fade-enter-active,
.backdrop-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to,
.backdrop-fade-enter-from,
.backdrop-fade-leave-to { opacity: 0; }

/* Slide + scale for the panel */
.modal-slide-enter-active {
  transition: opacity 0.22s ease, transform 0.22s cubic-bezier(0.22, 1, 0.36, 1);
}
.modal-slide-leave-active {
  transition: opacity 0.18s ease, transform 0.18s cubic-bezier(0.55, 0, 1, 0.45);
}
.modal-slide-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.975);
}
.modal-slide-leave-to {
  opacity: 0;
  transform: translateY(6px) scale(0.985);
}
</style>