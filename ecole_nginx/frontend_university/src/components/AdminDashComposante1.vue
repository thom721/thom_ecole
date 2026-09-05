<template>
  <div class="mb-2">
    <div class="bg-[#171b26] border-l-3 shadow-lg rounded-r-lg text-slate-600 cursor-pointer hover:shadow-lg hover:-translate-y-1 transition-all duration-500  transition-all p-4" 
         :class="colors">
      
      <div class="flex justify-between items-start">
        <h5 class="text-xs  uppercase tracking-wider" :class="'text-' + colorsText">
          {{ title }}
        </h5>
        <button @click.stop="$emit('show-details')" class="hover:bg-gray-300 transition-colors cursor-pointer">
          <i class="ri-add-large-line text-md" :class="'text-' + colorsText"></i>
        </button>
      </div> 
      <div class="flex justify-between items-end">
        <div class="rounded-full flex justify-center items-center ">
          <i class="text-xl text-gray-600 text-slate-300 " :class="icon"></i>
        </div>
        <div class="text-md text-slate-500">
          {{ value }} <span v-if="devise" class="text-[11px] font-normal">{{ devise }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  colors: String,      
  colorsText: String,  
  icon: String,
  value: [Number, String],
  devise: String
});

defineEmits(['show-details']);
</script>