<!-- src/views/NotesView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div class="flex flex-wrap items-start justify-between gap-3">
 
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.6" class="w-5 h-5 text-emerald-400">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125"/>
        </svg>
      </div>
      <div>
        <h1 class="text-[15px] font-bold text-[#e8eaf0] leading-tight">Notes & Évaluations</h1>
        <p class="text-[12px] text-[#7c83a0]">Saisie et gestion des résultats académiques</p>
      </div>
    </div>


      <div class="flex gap-2"> 
        <!-- :style="{ background: 'var(--accent,#4f8ef7)' }"  -->
        <button type="button"  @click="modalBulletin = true"  class="btn-sky">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/>
            </svg>
            Bulletin
        </button> 
          <router-link 
            to="/professeur-ajouter-notes" 
                class="btn-emerald">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125"/>
                </svg>
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

        
      <div class="w-full md:w-5/12">
          <div class="relative flex-1">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
              class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#3d4d62] pointer-events-none">
              <path fill-rule="evenodd" d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" clip-rule="evenodd" />
            </svg>
            <input
              v-model="search" type="text"
              placeholder="Rechercher un étudiant..."
              class="field-search"
            />
          </div> 
    </div>
    </div>
    

    <DataTable
    :columns="columns"
    :rows="CoursEtudiantData.data"
    row-key="id"
    :loading="studentLoading"
    :skeleton-rows="12"
    :meta="CoursEtudiantData.meta"
    :actions="actions"
    :row-errors="error"
    :initial-selections="selections"
    @change-page="searchCoursEtudiant"
    @update:selections="selections = $event"
  >
    <!-- Optional: custom cell for a specific column -->
    <template #cell-nom_classe="{ value }">
      <span class="text-[12px] font-semibold text-sky-400">{{ value }}</span>
    </template>

        <!-- Optional: empty state override -->
        <template #empty>
          Aucun étudiant trouvé pour cette recherche.
        </template>
      </DataTable>
        <!-- </div> -->

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
import DataTable from '@/components/DataTable.vue'
import Swal from 'sweetalert2';
import { usePdfWithLoading } from '@/stores/usePdf'; 
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

 const columns = [
  { key: 'identifiant', label: 'Identifiant' },
  { key: 'fname',       label: 'Nom',    badge: true },
  { key: 'lname',       label: 'Prénom', nowrap: true },
  { key: 'nom_classe',  label: 'Classe', semibold: true },
  { key: 'name',        label: 'Cycle' },
  { key: 'annee_academique', label: 'Année', size: 'text-[12px]' },
]

const selections = reactive({});

const EVAL_OPTIONS = {
  trimestres: [
    { id: 1, value: 'T1', title: 'Trimestre 1' },
    { id: 2, value: 'T2', title: 'Trimestre 2' },
    { id: 3, value: 'T3', title: 'Trimestre 3' },
  ],
  controles: [
    { id: 1, value: 'C1', title: 'Contrôle 1' },
    { id: 2, value: 'C2', title: 'Contrôle 2' },
  ],
  sessions: [
    { id: 1, value: 'S1', title: 'Session 1' },
    { id: 2, value: 'S2', title: 'Session 2' },
  ],
}

const actions = [
  {
    key: 'periode',
    type: 'select',
    // Dynamic options based on the row's evaluation_par field
    options: (row) => {
      const ep = row.evaluation_par?.toLowerCase()
      if (ep === 'mois')
        return [{ value: 'all', label: 'Annuel' }, ...month.map(m => ({ value: m, label: m }))]
      if (row.evaluation_par === 'Trimestre')
        return EVAL_OPTIONS.trimestres.map(t => ({ value: t.value, label: t.title }))
      if (row.evaluation_par === 'Controle')
        return EVAL_OPTIONS.controles.map(c => ({ value: c.value, label: c.title }))
      return EVAL_OPTIONS.sessions.map(s => ({ value: s.value, label: s.title }))
    },
    placeholder: 'Période',
    onChange: (row, value) => {
      console.log('Selection changed:', row.id, value)
    },
  },
  {
    key: 'pdf',
    type: 'button',
    icon: 'ri-file-pdf-2-line',
    loading: (_row, index) => loadingMap[index] === true,
    onClick: async (row, selection, index) => {
      await submitPdf('/imprime-bulletin', { mois: selection, bulletin: row.id }, index)
    },
  },
]



const searchCoursEtudiant = async (page = 1) => {
  try {
    studentLoading.value=true
    const response = await axios.get(`${url}/coursEtudiant`, {
      params: { search: search.value, page: page },
    });
    console.log(response.data); 
    CoursEtudiantData.value = response.data;
  } catch (error) {    
    console.error("Erreur de chargement des cours",error);
  }finally{
    studentLoading.value=false
  }
};

const data_print = reactive({
mois: '', 
classe: '', 
annee_academique: ''
})

const handlePrintBulletin = async (studentId, endpoint, evalType,selections) => { 
  
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
