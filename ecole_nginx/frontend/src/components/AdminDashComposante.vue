<template>
  <div
    class="group relative bg-[#161b26] border border-white/[0.07] rounded-2xl p-4 cursor-pointer
           hover:border-white/[0.12] hover:-translate-y-0.5 hover:shadow-xl hover:shadow-black/20
           transition-all duration-200 overflow-hidden"
  >
    <!-- Glow accent en haut à gauche -->
    <div
      class="absolute top-0 left-0 w-1 h-full rounded-l-2xl transition-all duration-200"
      :class="accentBar"
    />

    <!-- Header : titre + bouton -->
    <div class="flex items-start justify-between mb-3 pl-2">
      <span class="text-[10px] font-semibold uppercase tracking-widest" :class="textColor">
        {{ title }}
      </span>
      <button
        @click.stop="$emit('show-details')"
        class="w-6 h-6 flex items-center justify-center rounded-lg bg-white/[0.04]
               border border-white/[0.06] hover:bg-white/[0.09] transition-colors shrink-0"
      >
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2"
             class="w-3 h-3" :class="textColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/>
        </svg>
      </button>
    </div>

    <!-- Valeur + icône -->
    <div class="flex items-end justify-between pl-2">
      <div
        class="w-9 h-9 rounded-xl flex items-center justify-center border transition-colors"
        :class="iconBg"
      >
        <i class="text-[16px]" :class="[icon, textColor]"></i>
      </div>
      <div class="text-right">
        <div class="text-[20px] font-bold text-[#e8eaf0] leading-none tracking-tight">
          {{ formattedValue }}
        </div>
        <div v-if="devise" class="text-[10px] text-[#7c83a0] mt-0.5">{{ devise }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  title:  String,
  icon:   String,
  value:  [Number, String],
  devise: String,
  // 'blue' | 'emerald' | 'violet' | 'amber' | 'sky' | 'rose'
  color:  { type: String, default: 'blue' },
});

defineEmits(['show-details']);

const palette = {
  blue:    { bar: 'bg-[#4f8ef7]',    text: 'text-[#7aaeff]',   bg: 'bg-[#4f8ef7]/10 border-[#4f8ef7]/20'   },
  emerald: { bar: 'bg-emerald-500',  text: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
  violet:  { bar: 'bg-violet-500',   text: 'text-violet-400',  bg: 'bg-violet-500/10 border-violet-500/20'  },
  amber:   { bar: 'bg-amber-500',    text: 'text-amber-400',   bg: 'bg-amber-500/10 border-amber-500/20'    },
  sky:     { bar: 'bg-sky-500',      text: 'text-sky-400',     bg: 'bg-sky-500/10 border-sky-500/20'        },
  rose:    { bar: 'bg-rose-500',     text: 'text-rose-400',    bg: 'bg-rose-500/10 border-rose-500/20'      },
  teal:    { bar: 'bg-teal-500',     text: 'text-teal-400',    bg: 'bg-teal-500/10 border-teal-500/20'      },
  olive:    { bar: 'bg-olive-500',     text: 'text-olive-400',    bg: 'bg-olive-500/10 border-olive-500/20'      },
  purple:    { bar: 'bg-purple-500',     text: 'text-purple-400',    bg: 'bg-purple-500/10 border-purple-500/20'      },
};

const theme        = computed(() => palette[props.color] ?? palette.blue);
const accentBar    = computed(() => theme.value.bar);
const textColor    = computed(() => theme.value.text);
const iconBg       = computed(() => theme.value.bg);

const formattedValue = computed(() => {
  const n = Number(props.value);
  if (!isNaN(n) && n >= 1000) return n.toLocaleString('fr-FR');
  return props.value;
});
</script>