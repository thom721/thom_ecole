<template>
  <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6 overflow-x-scroll">
    <table class="w-full border-collapse text-start">

      <thead>
        <tr class="border-b border-white/[0.07]">
          <th
            v-for="col in columns"
            :key="col.key"
            class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3"
          >{{ col.label }}</th>

          <th
            v-if="actions?.length"
            class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3"
          >{{ actionsLabel }}</th>
        </tr>
      </thead>

      <!-- ── Skeleton (chargement) ── -->
      <tbody v-if="loading">
        <tr
          v-for="n in skeletonRows"
          :key="'sk-' + n"
          class="border-b border-white/[0.04]"
          :class="n % 2 === 0 ? 'bg-white/[0.01]' : ''"
        >
          <td
            v-for="col in columns"
            :key="col.key"
            class="py-3 pr-6"
          >
            <div
              class="h-2.5 rounded-full bg-white/[0.07] animate-pulse"
              :style="{ width: skeletonWidth(n, col.key) }"
            />
          </td>
          <td v-if="actions?.length" class="py-3">
            <div class="h-2.5 rounded-full bg-white/[0.07] animate-pulse w-20" />
          </td>
        </tr>
      </tbody>

      <!-- ── Lignes réelles ── -->
      <tbody v-else>
        <!-- État vide -->
        <tr v-if="!rows.length">
          <td
            :colspan="columns.length + (actions?.length ? 1 : 0)"
            class="py-10 text-center text-[#7c83a0] text-sm"
          >
            <slot name="empty">Aucune donnée disponible.</slot>
          </td>
        </tr>

        <!-- Lignes de données -->
        <tr
          v-for="(row, index) in rows"
          :key="row[rowKey] ?? index"
          class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors duration-150 row-in"
          :class="index % 2 === 1 ? 'bg-white/[0.01]' : ''"
          :style="{ animationDelay: `${index * 18}ms` }"
        >
          <!-- Cellules de données -->
          <td
            v-for="col in columns"
            :key="col.key ?? 'Non definie'"
            class="py-2 pl-4"
          >
            <!-- Slot custom par colonne -->
            <slot
              v-if="$slots[`cell-${col.key}`]"
              :name="`cell-${col.key}`"
              :row="row"
              :value="row[col.key]"
              :index="index"
            />

            <!-- Badge -->
            <span
              v-else-if="col.badge"
              class="text-[11px] px-2 py-1 rounded-md bg-white/[0.06] text-[#b0b5cc]"
            >{{ row[col.key] }}</span>

            <!-- Défaut -->
            <span
              v-else
              :class="[
                'text-[#b0b5cc]',
                col.mono     ? 'font-mono'         : '',
                col.semibold ? 'font-semibold'      : '',
                col.nowrap   ? 'whitespace-nowrap'  : '',
                col.size     ?? 'text-[13px]',
              ]"
            >{{ row[col.key] }}</span>
          </td>

          <!-- Cellule actions -->
          <td v-if="actions?.length" class="py-2">
            <div class="flex items-center gap-2">
              <template v-for="action in actions" :key="action.key">

                <!-- Select -->
                <div
                  v-if="action.type === 'select'"
                  class="min-w-[110px] bg-[#1e2335] rounded-lg hover:bg-[#262d44] transition-colors"
                >
                  <select
                    v-model="localSelections[row[rowKey] ?? index]"
                    class="w-full bg-transparent text-sky-500 text-[12px] outline-none px-2 py-1.5 cursor-pointer"
                    @change="action.onChange?.(row, localSelections[row[rowKey] ?? index])"
                  >
                    <option v-if="action.placeholder" value="" disabled selected>
                      {{ action.placeholder }}
                    </option>
                    <option
                      v-for="opt in resolveOptions(action.options, row)"
                      :key="opt.value"
                      :value="opt.value"
                    >{{ opt.label }}</option>
                  </select>
                </div>

                <!-- Bouton -->
                <button
                  v-else-if="action.type === 'button'"
                  :disabled="action.loading?.(row, index) ?? false"
                  class="bg-[#1e2335] text-[#b0b5cc] rounded-full p-1.5 hover:text-sky-500 transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed flex justify-center items-center text-xs"
                  @click="action.onClick?.(row, localSelections[row[rowKey] ?? index], index)"
                >
                  <svg v-if="action.loading?.(row, index)" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <i v-else :class="action.icon" />
                </button>

                <!-- Slot custom action -->
                <slot
                  v-else-if="action.type === 'slot'"
                  :name="`action-${action.key}`"
                  :row="row"
                  :index="index"
                  :selection="localSelections[row[rowKey] ?? index]"
                />

              </template>

              <!-- Erreur par ligne -->
              <p v-if="rowErrors?.[row[rowKey] ?? index]" class="text-red-500 text-xs">
                {{ rowErrors[row[rowKey] ?? index] }}
              </p>
            </div>
          </td>
        </tr>
      </tbody>

    </table> 
    <!-- Pagination -->
    <div v-if="meta" class="mt-3 flex justify-end text-slate-500">
      <Pagination :meta="meta" @change-page="$emit('change-page', $event)" />
    </div>
  </div>
</template>

<script setup>
// import { ref, watch } from 'vue'
import { ref, watch, nextTick } from 'vue'
import Pagination from '@/components/Pagination.vue';
const props = defineProps({
  /**
   * Définitions des colonnes.
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
  columns: { type: Array, required: true },

  /** Données du tableau */
  rows: { type: Array, default: () => [] },

  /** Champ servant de clé unique par ligne */
  rowKey: { type: String, default: 'id' },

  /** Affiche le skeleton pendant le chargement */
  loading: { type: Boolean, default: false },

  /** Nombre de lignes skeleton */
  skeletonRows: { type: Number, default: 6 },

  /** Objet meta de pagination (transmis au composant <Pagination />) */
  meta: { type: Object, default: null },

  /** Label optionnel de la colonne actions */
  actionsLabel: { type: String, default: 'Actions' },

  /**
   * Définitions des actions (colonne à droite).
   * @type {Array<{
   *   key: string,
   *   type: 'button' | 'select' | 'slot',
   *   placeholder?: string,
   *   options?: Array<{value, label}> | ((row) => Array<{value, label}>),
   *   onChange?: (row, value) => void,
   *   icon?: string,
   *   onClick?: (row, selection, index) => void,
   *   loading?: (row, index) => boolean,
   * }>}
   */
  actions: { type: Array, default: null },

  /** Map rowKey → message d'erreur affiché sur la ligne */
  rowErrors: { type: Object, default: null },

  /** Sélections initiales : rowKey → valeur sélectionnée */
  initialSelections: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['change-page', 'update:selections'])

// ── Sélections locales ────────────────────────────────────────────────────────
// const localSelections = ref({ ...props.initialSelections })

// watch(
//   () => props.initialSelections,
//   val => { localSelections.value = { ...val } },
// )
// watch(localSelections, val => emit('update:selections', val), { deep: true })

const localSelections = ref({ ...props.initialSelections })
let internalUpdate = false

watch(
  () => props.initialSelections,
  val => {
    if (internalUpdate) return
    localSelections.value = { ...val }
  },
)

watch(localSelections, val => {
  internalUpdate = true
  emit('update:selections', val)
  nextTick(() => { internalUpdate = false })
}, { deep: true })

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Options statiques ou issues d'une factory function. */
function resolveOptions(options, row) {
  return typeof options === 'function' ? options(row) : (options ?? [])
}

/**
 * Largeur skeleton déterministe (pas de re-render aléatoire au reconciliation).
 * On combine l'index de ligne et le premier caractère de la clé.
 */
const W = ['38%', '52%', '68%', '80%', '45%', '62%', '74%', '55%']
function skeletonWidth(rowIdx, colKey) {
  return W[(rowIdx * 3 + (colKey?.charCodeAt(0) ?? 0)) % W.length]
}
</script>

<style scoped>
/* Apparition des lignes réelles après chargement */
@keyframes rowIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0);   }
}
.row-in {
  animation: rowIn 0.22s ease both;
}
</style>
