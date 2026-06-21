<template>
  <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6 overflow-x-scroll">
    <table class="w-full min-w-[700px]">
      <thead>
        <tr class="border-b border-white/[0.07]">
          <th
            v-for="col in columns"
            :key="col.key"
            class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3 pr-4 last:pr-0"
          >
            {{ col.label }} 000
          </th>
          <th
            v-if="actions"
            class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3"
          />
        </tr>
      </thead>

      <tbody>
        <!-- ───── Skeleton pulse (loading state) ───── -->
        <template v-if="loading">
          <tr
            v-for="n in skeletonRows"
            :key="'sk-' + n"
            class="border-b border-white/[0.04]"
            :class="n % 2 === 0 ? 'bg-white/[0.01]' : ''"
          >
            <td
              v-for="col in allColumns"
              :key="col.key"
              class="py-3 pr-4"
            >
              <div
                class="h-3 rounded-full bg-white/[0.06] animate-pulse"
                :style="{ width: randomWidth() }"
              />
            </td>
          </tr>
        </template>

        <!-- ───── Real rows ───── -->
        <template v-else>
          <transition-group name="row-fade" tag="tbody">
            <tr
              v-for="(row, index) in rows"
              :key="row[rowKey] ?? index"
              class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors"
              :class="[
                index % 2 === 1 ? 'bg-white/[0.01]' : '',
                'row-transition',
              ]"
            >
              <!-- Data cells -->
              <td
                v-for="col in columns"
                :key="col.key"
                class="py-2 pr-4"
              >
                <!-- Custom slot per column -->
                <slot
                  v-if="$slots[`cell-${col.key}`]"
                  :name="`cell-${col.key}`"
                  :row="row"
                  :value="row[col.key]"
                  :index="index"
                />
 
                <span
                  v-else-if="col.badge"
                  class="text-[11px] px-2 py-0.5 rounded-md bg-white/[0.06] text-[#b0b5cc]"
                >
                  {{ row[col.key] }}
                </span>
 
                <span
                  v-else
                  :class="[
                    'text-[#b0b5cc]',
                    col.mono ? 'font-mono' : '',
                    col.semibold ? 'font-semibold' : '',
                    col.nowrap ? 'whitespace-nowrap' : '',
                    col.size ?? 'text-[13px]',
                  ]"
                >
                  {{ row[col.key] }}
                </span>
              </td>

              <!-- Actions cell -->
              <td v-if="actions" class="py-2">
                <div class="flex items-center justify-center gap-2">
                  <!-- Render each action -->
                  <template v-for="action in actions" :key="action.key">

                    <!-- Select action -->
                    <div
                      v-if="action.type === 'select'"
                      class="min-w-[100px] py-1.5 bg-[#1e2335] text-[#e8eaf0] rounded-lg text-[12px] font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0 whitespace-nowrap"
                    >
                      <select
                        v-model="localSelections[row[rowKey] ?? index]"
                        class="border-0 focus:border-0 active:border-0 bg-transparent text-sky-500 w-full outline-none px-2"
                        @change="action.onChange?.(row, localSelections[row[rowKey] ?? index])"
                      >
                        <option
                          v-if="action.placeholder"
                          value=""
                          disabled
                          selected
                        >{{ action.placeholder }}</option>
                        <option
                          v-for="opt in resolveOptions(action.options, row)"
                          :key="opt.value"
                          :value="opt.value"
                        >{{ opt.label }}</option>
                      </select>
                    </div>

                    <!-- Button action -->
                    <button
                      v-else-if="action.type === 'button'"
                      :disabled="action.loading?.(row, index) ?? false"
                      class="bg-[#1e2335] text-[#b0b5cc] rounded shadow-sm hover:text-sky-500 hover:border-sky-200 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed p-1.5"
                      @click="action.onClick?.(row, localSelections[row[rowKey] ?? index], index)"
                    >
                      <svg
                        v-if="action.loading?.(row, index)"
                        class="animate-spin w-4 h-4"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      <i v-else :class="action.icon" />
                    </button>

                    <!-- Custom slot action -->
                    <slot
                      v-else-if="action.type === 'slot'"
                      :name="`action-${action.key}`"
                      :row="row"
                      :index="index"
                      :selection="localSelections[row[rowKey] ?? index]"
                    />
                  </template>

                  <!-- Error per row -->
                  <p
                    v-if="rowErrors?.[row[rowKey] ?? index]"
                    class="text-red-500 text-xs"
                  >{{ rowErrors[row[rowKey] ?? index] }}</p>
                </div>
              </td>
            </tr>

            <!-- Empty state -->
            <tr v-if="!rows.length" key="empty">
              <td :colspan="allColumns.length" class="py-10 text-center text-[#7c83a0] text-sm">
                <slot name="empty">Aucune donnée disponible.</slot>
              </td>
            </tr>
          </transition-group>
        </template>
      </tbody>
    </table>

    <!-- Pagination -->
    <div v-if="meta" class="mt-2 flex justify-end text-slate-500">
      <Pagination :meta="meta" @change-page="$emit('change-page', $event)" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// ─── Props ────────────────────────────────────────────────────────────────────

const props = defineProps({
  /**
   * Column definitions.
   * @type {Array<{
   *   key: string,
   *   label: string,
   *   badge?: boolean,
   *   mono?: boolean,
   *   semibold?: boolean,
   *   nowrap?: boolean,
   *   size?: string
   * }>}
   */
  columns: {
    type: Array,
    required: true,
  },

  /**
   * Row data.
   */
  rows: {
    type: Array,
    default: () => [],
  },

  /**
   * The field used as unique key per row.
   */
  rowKey: {
    type: String,
    default: 'id',
  },

  /**
   * Whether the table is loading.
   */
  loading: {
    type: Boolean,
    default: false,
  },

  /**
   * Number of skeleton rows to show while loading.
   */
  skeletonRows: {
    type: Number,
    default: 6,
  },

  /**
   * Pagination meta object (passed to <Pagination />).
   */
  meta: {
    type: Object,
    default: null,
  },

  /**
   * Action column definitions.
   * @type {Array<{
   *   key: string,
   *   type: 'button' | 'select' | 'slot',
   *
   *   // For type === 'select'
   *   placeholder?: string,
   *   options?: Array<{value, label}> | ((row) => Array<{value, label}>),
   *   onChange?: (row, value) => void,
   *
   *   // For type === 'button'
   *   icon?: string,          // e.g. 'ri-file-pdf-2-line'
   *   onClick?: (row, selection, index) => void,
   *   loading?: (row, index) => boolean,
   * }>}
   */
  actions: {
    type: Array,
    default: null,
  },

  /**
   * Map of rowKey → error message to display inline.
   */
  rowErrors: {
    type: Object,
    default: null,
  },

  /**
   * Initial selections map (rowKey → selected value).
   */
  initialSelections: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['change-page', 'update:selections'])

// ─── Local state ──────────────────────────────────────────────────────────────

const localSelections = ref({ ...props.initialSelections })

watch(
  () => props.initialSelections,
  (val) => {
    localSelections.value = { ...val }
  },
)

watch(localSelections, (val) => emit('update:selections', val), { deep: true })

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** All columns including the actions column placeholder (for colspan). */
const allColumns = computed(() => {
  if (props.actions) return [...props.columns, { key: '__actions__' }]
  return props.columns
})

/** Resolve options: static array or factory function. */
function resolveOptions(options, row) {
  if (typeof options === 'function') return options(row)
  return options ?? []
}

/** Randomise skeleton cell widths for a natural look. */
const widths = ['40%', '55%', '70%', '85%', '60%', '45%', '75%']
let widthIdx = 0
function randomWidth() {
  return widths[widthIdx++ % widths.length]
}
</script>

<style scoped>
/* Row fade-in / fade-out transition (transition-group) */
.row-fade-enter-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.row-fade-leave-active {
  transition: opacity 0.15s ease;
  position: absolute;
}
.row-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.row-fade-leave-to {
  opacity: 0;
}
</style>
