<script setup>
import { ref, onMounted, watch, reactive } from "vue";
import axios from "axios";
import Swal from 'sweetalert2';
import { useSchoolStore,useSchoolStoreInfo } from '@/stores/schoolStore';
 import StyleModal from '@/components/StyleModal.vue';
import DataTable from '@/components/DataTable.vue'
import { usePdfWithLoading } from '@/stores/usePdf';
const { submitPdf, loading, error, loadingMap } = usePdfWithLoading()

const {classes_global,annee_global} =useSchoolStoreInfo()
const global_bulletin = ref(false)
const dataLoading = ref(false)
const data_print = reactive({
bulletin:"",
print_all: { mois: '', classe: '', annee_academique: ''},
})

const handlePrintBulletin = async (studentId, endpoint, evalType) => {
  if (studentId) {    
    data_print.bulletin = studentId;
    const type = evalType?.toLowerCase();
    if (type === 'mois') data_print['mois']= selections.value.mois;
    else if (evalType === 'Trimestre') data_print['Trimestre']=selections.value.Trimestre;
    else if (evalType === 'Controle') data_print['Controle']=selections.value.Controle;
    else data_print['session']=selections.value.session;
  }
 
  
  try {
    const token = localStorage.getItem("auth-token");
    global_bulletin.value = true
    
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
    closeModal()
    window.open(url, '_blank');
    
    setTimeout(() => window.URL.revokeObjectURL(url), 100);
  } catch (error) {
    console.error("Erreur Impression:", error);
    alert("Erreur lors de la génération du document.");
  }finally{global_bulletin.value=false}
};

const url = import.meta.env.VITE_APP_BASE_URL;
 
const props = defineProps({   
  filters: Object
});

const showSwal = (text, icon = 'info') => {
  Swal.fire({
    position: "top-end",
    text: text,
    icon: icon,
    showConfirmButton: false,
    timer: 2000,
  });
};

const month = ["Septembre", "Octobre", "Novembre", "Décembre", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août"]
// --- ÉTATS ---
const CoursEtudiantData = ref({ data: [], meta: { links: [] } });
const search = ref(props.filters?.search || "");
const pages = ref(1);

// Paramètres pour l'impression (liés aux v-model des selects)
const selections = ref({
  mois: "September",
  Controle: "",
  Trimestre: "",
  session: ""
});

// Données statiques pour les évaluations
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

 
const searchCoursEtudiant = async (page=1) => {
  dataLoading.value=true
  try {
    const response = await axios.get(`${url}/coursEtudiant`, {
      params: { search: search.value, page: page },
    });
    CoursEtudiantData.value = response.data;
    console.log(response.data);
    
  } catch (error) {
    console.error("Erreur de chargement des cours");
  }finally{dataLoading.value=false}
};
 
watch(search, () => { 
  searchCoursEtudiant();
});

// watch(pages, searchCoursEtudiant);

onMounted(searchCoursEtudiant);
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
    type: 'slot',
    icon: 'ri-file-pdf-2-line',
    
    onClick: async (row, selection, index) => {
      console.log(row.id);
      
      await submitPdf('/imprime-bulletin', { mois: selection, bulletin: row.id }, index)
    },
  },
]
</script>

<template>
  <div class="max-w-7xl px-2 mx-auto pb-16 text-slate-600 animate-[fadeUp_0.4s_ease_both]">
    <!-- <div class="flex flex-col md:flex-row flex-wrap gap-3 "> 
      <router-link to="/admin/ajouter-notes" class="btn-outline-green text-center">
        Ajouter / Modifier notes
      </router-link>
      <button type="button" class="btn-outline-orange" @click="modalBulletin = true">Bulletin</button> -->

      <div class="flex items-center gap-3 mb-5">
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

<div class="flex flex-wrap gap-2">
  <router-link to="/admin/ajouter-notes"
    class="btn-emerald">
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125"/>
    </svg>
    Ajouter / Modifier notes
  </router-link>

  <button type="button" @click="modalBulletin = true"
    class="btn-sky">
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/>
    </svg>
    Bulletin
  </button>
 
  </div>

    <div class="flex justify-end mt-2 md:mt-0">
  <div class="w-full md:w-5/12 mb-2 md:mr-4">
          <div class="relative flex-1">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
              class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#3d4d62] pointer-events-none">
              <path fill-rule="evenodd" d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" clip-rule="evenodd" />
            </svg>
        <input 
          v-model="search" 
          type="text" 
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
    :loading="dataLoading"
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

        <template #action-pdf="{row, value,selection }">      
          <button
          
          @click="submitPdf('/imprime-bulletin', { mois: selection, bulletin: row.id }, row.id)"
          :disabled="loadingMap[row.id] == true"
          class="font-mono hover:underline cursor-pointer text-sm">
          
          <i v-if="loadingMap[row.id] != true" class="ri-file-pdf-2-line"></i>
         
          <span v-else class="inline-flex items-center gap-1.5 text-sky-500 text-sm">
          <svg class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10"
              stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
          </svg>
          Waiting…
        </span>
        </button>
    </template>

        <!-- Optional: empty state override -->
        <template #empty>
          Aucun étudiant trouvé pour cette recherche.
        </template>
      </DataTable>
    
    
    
    <StyleModal :show="modalBulletin" max-width="2xl" @close="closeModal">
        <template #title>
            <div class="flex justify-between items-center py-2">
                <p class="text-lg  text-gray-800">Bulletin</p>
                <p class="far fa-circle-xmark text-xl text-red-500 cursor-pointer hover:scale-110 transition flex justify-end" @click="closeModal"></p>
            </div>

        </template>
        <template #content>
            <div class="flex jutify-between items-center gap-4">
                  <select v-model="data_print.print_all.annee_academique" class="input-select">
                    <option value="" disabled>Choisir une Année</option>
                    <option v-for="a in annee_global" :key="a.id" :value="a.annee_academique">{{ a.annee_academique }}</option>
                  </select>
              <select v-model="data_print.print_all.mois" class="input-select">
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
                  <select v-model="data_print.print_all.classe" class="input-select">
                    <option value="" disabled>Choisir la classe</option>
                    <option v-for="c in classes_global" :key="c.id" :value="c.id">{{ c.nom_classe }}</option>
                  </select>
                </div>

              <div class="w-5/12">
                <label class="text-sm"></label><br>
                  <button v-if="!global_bulletin" 
                    @click="handlePrintBulletin(id=false,'imprime-mas-bulletin', data_print.print_all)"
                    class="btn-outline-sky w-24"
                  >
                    Imprimer
                  </button>
                   <span v-else class="inline-flex items-center gap-1.5 text-sky-500 text-sm">
                      <svg class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10"
                          stroke="currentColor" stroke-width="4"/>
                        <path class="opacity-75" fill="currentColor"
                          d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
                      </svg>
                      Waiting…
                    </span>
              </div>
            </div> 
           
        </template>
    </StyleModal>
  </div>
</template>
 