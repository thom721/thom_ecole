<!-- src/views/NotesView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Devoirs & Notes</h1>
        <p class="text-[#7c83a0] text-sm">28 devoirs · 8 à corriger en urgence</p>
      </div>
      <div class="flex gap-2">
        <!-- <button class="px-4 py-2 bg-[#1e2335] text-[#e8eaf0] rounded-xl text-sm font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0">Exporter</button> -->
        <button type="button" class="btn-outline-orange" @click="modalBulletin = true">Bulletin</button>
        <!-- <button class="px-4 py-2 text-white rounded-xl text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0" :style="{ background: 'var(--accent,#4f8ef7)' }">+ Nouveau Notes</button> -->
          <router-link :style="{ background: 'var(--accent,#4f8ef7)' }" to="/ajouter-notes" class="px-4 py-2 text-white rounded-md text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0">
            + Ajouter / Modifier notes
          </router-link>
      </div>
    </div>

    <!-- Filters -->
     <div class="flex flex-col md:flex-row justify-between">
    <div class="flex gap-2 flex-wrap">
      <button v-for="f in filters" :key="f.id"
        @click="active = f.id"
        class="flex items-center gap-1.5 px-4 py-1.5 rounded-full text-[13px] font-medium transition-all cursor-pointer border"
        :class="active === f.id
          ? 'text-[var(--accent)] border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_12%,transparent)]'
          : 'bg-[#1e2335] border-white/[0.07] text-[#7c83a0] hover:text-[#e8eaf0]'"
        :style="active === f.id ? { borderColor: 'var(--accent,#4f8ef7)', color: 'var(--accent,#4f8ef7)', background: 'rgba(79,142,247,0.1)' } : {}"
      >
        {{ f.label }}
        <span v-if="f.count" class="bg-white/10 text-[11px] px-1.5 py-0.5 rounded-full">{{ f.count }}</span>
      </button>
    </div>

        <!-- <div class=""> -->
      <div class="w-full md:w-5/12">
        <input 
          v-model="search" 
          type="text" 
          placeholder="Rechercher un étudiant..." 
          class="w-full px-4 py-1.5 border rounded-lg focus:ring-0 focus:border-sky-500 outline-none border-slate-200"
        />
      <!-- </div> -->
    </div>
    </div>

    <!-- Table -->
    <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6 overflow-x-scroll">
      <table class="w-full min-w-[700px]">
        <thead>
          <tr class="border-b border-white/[0.07]">
            <th v-for="h in ['Identifiant','Nom','Prénom','Classe','Cycle','Année','']" :key="h"
              class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3 pr-4 last:pr-0"
            >{{ h }}</th>
          </tr>
        </thead>
        <!-- <tbody>
          <tr v-for="d in filtered" :key="d.title" class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
            <td class="py-3 pr-4">
              <p class="text-[13px] font-medium text-[#e8eaf0]">{{ d.title }}</p>
              <p class="text-[11px] text-[#7c83a0]">{{ d.type }}</p>
            </td>
            <td class="py-3 pr-4"><span class="text-[11px] px-2 py-0.5 rounded-md bg-white/[0.06] text-[#b0b5cc]">{{ d.class }}</span></td>
            <td class="py-3 pr-4 text-[13px] text-[#b0b5cc] whitespace-nowrap">{{ d.deadline }}</td>
            <td class="py-3 pr-4">
              <div class="w-16 h-1 bg-[#1e2335] rounded-full overflow-hidden mb-1">
                <div class="h-full rounded-full" :style="{ width: (d.rendus/d.total*100)+'%', background: 'var(--accent,#4f8ef7)' }" />
              </div>
              <span class="text-[11px] text-[#7c83a0]">{{ d.rendus }}/{{ d.total }}</span>
            </td>
            <td class="py-3 pr-4 text-[14px] font-semibold" :style="{ color: d.avg>=14?'#6ee7b7':d.avg>=10?'#f59e0b':'#f87171' }">{{ d.avg>0?d.avg:'—' }}</td>
            <td class="py-3 pr-4">
              <span class="text-[11px] px-2.5 py-1 rounded-full font-medium whitespace-nowrap"
                :class="{
                  'bg-[#6ee7b7]/10 text-[#6ee7b7]': d.status==='green',
                  'bg-[#f59e0b]/10 text-[#f59e0b]': d.status==='amber',
                  'bg-[#f87171]/10 text-[#f87171]': d.status==='red',
                  'bg-[#4f8ef7]/10 text-[#4f8ef7]': d.status==='blue',
                }"
              >{{ d.statusLabel }}</span>
            </td>
            <td class="py-3">
              <button class="px-3 py-1.5 bg-[#1e2335] text-[#e8eaf0] rounded-lg text-[12px] font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0 whitespace-nowrap">Corriger</button>
            </td>
          </tr>
        </tbody> -->
         <tbody>
          <template v-if="studentLoading">
            <tr class="text-center">
           <td colspan="7"  class="text-center">
             <svg  class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg> 
           </td>  
              </tr>                  
          </template>
          <template v-else>
          <tr v-for="(note, index) in CoursEtudiantData.data" :key="note.id" class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors" :class="index % 2 === 1 ? 'bg-white/[0.01]' : ''">
            <td class="py-2 pr-4 text-[#b0b5cc] text-[13px] font-medium">
               {{ note.identifiant }}
            </td>
            <td class="py-2 pr-4"><span class="text-[11px] px-2 py-0.5 rounded-md bg-white/[0.06] text-[#b0b5cc]">{{ note.fname }}</span></td>
            <td class="py-2 pr-4 text-[13px]  whitespace-nowrap text-[#b0b5cc]">{{ note.lname }}</td>
            <td class="py-2 pr-4 text-[12px] font-semibold text-[#b0b5cc]" >{{ note.nom_classe }}</td>
            <td class="py-2 pr-4 text-[#b0b5cc]"> 
             {{ note.name }}
            </td>

            <td class="py-2 pr-4 text-[12px] text-[#b0b5cc]">
              {{ note.annee_academique }} 
            </td>
            <td class="py-2 text-[#b0b5cc]">
                 <div class="flex items-center justify-center gap-2">
                  
                  <div class="min-w-[100px] py-1.5 bg-[#1e2335] text-[#e8eaf0] rounded-lg text-[12px] font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0 whitespace-nowrap">
                    <select 
                      v-if="note.evaluation_par?.toLowerCase() === 'mois'" 
                      v-model="selections[note.id]"
                      class="border border-0 focus:border-0 active:border-0 text-sky-600"
                    >
                      <option value="all">Annuel</option>
                      <option v-for="k in month" :key="k" :value="k">{{ k }}</option>
                    </select>

                    <select 
                      v-else-if="note.evaluation_par === 'Trimestre'" 
                      v-model="selections[note.id]"
                      class="border border-0 focus:border-0 active:border-0 text-sky-600 w-full"
                    >
                      <option value="" disabled selected>Trimestre</option>
                      <option v-for="t in EVAL_OPTIONS.trimestres" :key="t.id" :value="t.value">{{ t.title }}</option>
                    </select>

                    <select 
                      v-else-if="note.evaluation_par === 'Controle'" 
                      v-model="selections[note.id]"
                      class="border border-0 focus:border-0 active:border-0 text-sky-600 w-full"
                    >
                      <option value="" disabled selected>Contrôle</option>
                      <option v-for="c in EVAL_OPTIONS.controles" :key="c.id" :value="c.value">{{ c.title }}</option>
                    </select>

                    <select 
                      v-else 
                      v-model="selections[note.id]"
                      class="border border-0 focus:border-0 active:border-0 text-sky-600 w-full"
                    >
                      <option value="" disabled selected>Session</option>
                      <option v-for="s in EVAL_OPTIONS.sessions" :key="s.id" :value="s.value">{{ s.title }}</option>
                    </select>
                  </div>
                   <button 
                      @click="submitPdf('/imprime-bulletin', { mois: selections[note.id], bulletin: note.id }, index)"
                      class="bg-[#1e2335] text-[#e8eaf0] rounded shadow-sm hover:text-sky-600 hover:border-sky-200 transition-all cursor-pointer"
                      :disabled="loadingMap[index] === true"
                    >
                      <svg v-if="loadingMap[index] === true" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                      </svg> 
                      <i v-else class="ri-file-pdf-2-line text-[#b0b5cc]"></i>
                    </button>
                  <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
                </div>
            </td>
          </tr>
          </template>
        </tbody>
      </table>
       <div
            v-if="CoursEtudiantData.meta"
            class="mt-2 flex justify-end text-slate-500"
          > 
          <Pagination
              :meta="CoursEtudiantData.meta" 
              @change-page="searchCoursEtudiant" 
            />

          </div>
    </div>

    <DialogModal :show="modalBulletin" max-width="2xl" @close="closeModal">
        <template #title>
            <div class="flex justify-between items-center py-2">
                <p class="text-lg font-bold text-gray-800">Bulletin</p>
                <p class="far fa-circle-xmark text-xl text-red-500 cursor-pointer hover:scale-110 transition flex justify-end" @click="closeModal"></p>
            </div>

        </template>
        <template #content>
            <div class="flex jutify-between items-center gap-4">
                  <select v-model="data_print.annee_academique" class="input-select">
                    <option value="" disabled>Choisir une Année</option>
                    <option v-for="a in annee_global" :key="a.id" :value="a.annee_academique">{{ a.annee_academique }}</option>
                  </select>
              <select v-model="data_print.mois" class="input-select">
                   <option value="" disabled>Choisir le mois</option>
                    <option value="Annuel">Annuel</option>
                    
                  <option v-for="cls in month" :key="cls" :value="cls">
                  {{ cls }}
                  </option>
              </select>
            </div>

              <div class="flex jutify-between items-center gap-4 pt-4">
                <div class="w-full">
                  <label class="text-sm">Classe</label>
                  <select v-model="data_print.classe" class="input-select">
                    <option value="" disabled>Choisir la classe</option>
                    <option v-for="c in classes_global" :key="c.id" :value="c.id">{{ c.nom_classe }}</option>
                  </select>
                </div>

              <div class="w-5/12">
                <label class="text-sm"></label><br>
                  <button 
                    @click="handlePrintBulletin(id=false,'imprime-mas-bulletin', data_print)"
                    class="btn-outline-sky w-24"
                  >
                    Imprimer
                  </button>
              </div>
            </div> 
           
        </template>
    </DialogModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, reactive } from 'vue'
import axios, { Axios } from 'axios'

import { useSchoolStore,useSchoolStoreInfo } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';
import DialogModal from '@/components/DialogModal.vue'
import Swal from 'sweetalert2';
import { usePdfWithLoading } from '@/stores/usePdf';
import Pagination from '@/components/Pagination.vue';
const { submitPdf, loading, error, loadingMap } = usePdfWithLoading()


const showSwal = (text, icon = 'info') => {
  Swal.fire({
    position: "top-end",
    text: text,
    icon: icon,
    showConfirmButton: false,
    timer: 2000,
  });
};
 
const active = ref('all') 
const filters = [
  { id:'all',     label:'Tous',       count:12 },
  { id:'pending', label:'En attente', count:8  },
  { id:'grading', label:'À corriger', count:3  },
  { id:'done',    label:'Terminés',   count:null },
]
const devoirs = [
  { title:'Contrôle Intégration',  type:'Contrôle · 2h',      class:'Tle S1', deadline:'24 Fév 2026', rendus:28,total:28, avg:14.2, status:'green', statusLabel:'Corrigé',    filter:'done'    },
  { title:'DM Probabilités n°3',   type:'Devoir maison',       class:'Tle S2', deadline:'28 Fév 2026', rendus:22,total:30, avg:0,    status:'amber', statusLabel:'En attente', filter:'pending' },
  { title:'Exercices Dérivées',    type:'Travaux pratiques',   class:'1re S1', deadline:'21 Fév 2026', rendus:15,total:27, avg:0,    status:'red',   statusLabel:'Urgent',     filter:'pending' },
  { title:'DS Géométrie espace',   type:'Devoir surveillé',    class:'1re S2', deadline:'20 Fév 2026', rendus:29,total:29, avg:15.0, status:'green', statusLabel:'À corriger', filter:'grading' },
  { title:'Quiz Arithmétique',     type:'Quiz en ligne',       class:'2de B',  deadline:'25 Fév 2026', rendus:10,total:28, avg:0,    status:'amber', statusLabel:'En attente', filter:'pending' },
  { title:'Bilan T2 Algèbre',      type:'Contrôle · 1h',       class:'2de C',  deadline:'18 Fév 2026', rendus:26,total:26, avg:13.0, status:'green', statusLabel:'À corriger', filter:'grading' },
]
const filtered = computed(() => active.value==='all' ? devoirs : devoirs.filter(d=>d.filter===active.value))


const {classes_global,annee_global} =useSchoolStoreInfo()

const url = import.meta.env.VITE_APP_BASE_URL;
const props = defineProps({    
  filters: Object
});
const month = ["Septembre", "Octobre", "Novembre", "Décembre", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août"]
const CoursEtudiantData = ref({ data: [], meta: { links: [] } });
const search = ref(props.filters?.search || "");
const pages = ref(1);
const studentLoading = ref(false)

const modalBulletin = ref(false);

const closeModal = () => {
    modalBulletin.value = false; 
};
// const selections = reactive({
//   mois: "September",
//   Controle: "",
//   bulletin:"",
//   Trimestre: "",
//   session: ""
// });

const selections = reactive({});

const EVAL_OPTIONS = {
  sessions: [
    { id: 1, value: '1 ere Session', title: '1ère Session' },
    { id: 2, value: '2 eme Session', title: '2ème Session' }
  ],
  controles: [
    { id: 1, value: 'Contr. I', title: 'Contrôle I' },
    { id: 2, value: 'Contr. II', title: 'Contrôle II' },
    { id: 3, value: 'Contr. III', title: 'Contrôle III' },
    { id: 4, value: 'Contr. IV', title: 'Contrôle IV' }
  ],
  trimestres: [
    { id: 1, value: 'Trimestre I', title: 'Trimestre I' },
    { id: 2, value: 'Trimestre II', title: 'Trimestre II' },
    { id: 3, value: 'Trimestre III', title: 'Trimestre III' }
  ]
};


const searchCoursEtudiant = async (page = 1) => {
  try {
    studentLoading.value=true
    const response = await axios.get(`${url}/coursEtudiant`, {
      params: { search: search.value, page: page },
    });
    console.log(response.data);
    studentLoading.value=false
    CoursEtudiantData.value = response.data;
  } catch (error) {
    studentLoading.value=false
    console.error("Erreur de chargement des cours",error);
  }
};

const data_print = reactive({
mois: '', 
classe: '', 
annee_academique: ''
})

const handlePrintBulletin = async (studentId, endpoint, evalType,selections) => {
  console.log(studentId, endpoint, evalType,selections,reactive.value);
  
  if (studentId) {    
    data_print.bulletin = studentId;
    const type = evalType?.toLowerCase();
    if (type === 'mois') data_print['mois']= selections;
    else if (evalType === 'Trimestre') data_print['Trimestre']=selections //selections.value.Trimestre;
    else if (evalType === 'Controle') data_print['Controle']=selections //selections.value.Controle;
    else data_print['session']=selections//selections.value.session;
  }
 
  
  try {
    const token = localStorage.getItem("auth-token");
    
    closeModal()
    const response = await axios.post(endpoint, studentId==false ? evalType : data_print, {
      headers: { 
        "Authorization": `Bearer ${token}`,
        "Accept": "application/pdf" 
      },
      responseType: 'blob'
    });
showSwal("génération du document")
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    window.open(url, '_blank');
    
    setTimeout(() => window.URL.revokeObjectURL(url), 100);
  } catch (error) {
    showSwal("Erreur lors de la génération du document.")
    console.error("Erreur Impression:", error); 
  }
};

watch(search, () => {
  pages.value = 1;
  searchCoursEtudiant();
});

watch(pages, searchCoursEtudiant);
onMounted(()=>{
  searchCoursEtudiant()  
});
</script>
