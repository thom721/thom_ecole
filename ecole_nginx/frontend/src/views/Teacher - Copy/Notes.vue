<script setup>
import { ref, onMounted, watch, reactive } from "vue";
import axios from "axios";
import DialogModal from '@/components/DialogModal.vue';
import { useSchoolStore,useSchoolStoreInfo } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';

import Swal from 'sweetalert2';
const showSwal = (text, icon = 'info') => {
  Swal.fire({
    position: "top-end",
    text: text,
    icon: icon,
    showConfirmButton: false,
    timer: 2000,
  });
};
 

const {classes_global,annee_global} =useSchoolStoreInfo()

const url = import.meta.env.VITE_APP_BASE_URL;
 
 
const props = defineProps({    
  filters: Object
});
const month = ["Septembre", "Octobre", "Novembre", "Décembre", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août"]
// --- ÉTATS ---
const CoursEtudiantData = ref({ data: [], meta: { links: [] } });
const search = ref(props.filters?.search || "");
const pages = ref(1);

const modalBulletin = ref(false);

const closeModal = () => {
    modalBulletin.value = false; 
};

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

// --- LOGIQUE API ---
const searchCoursEtudiant = async () => {
  try {
    const response = await axios.get(`${url}/coursEtudiant`, {
      params: { search: search.value, page: pages.value },
    });
    console.log(response.data);
    
    CoursEtudiantData.value = response.data;
  } catch (error) {
    console.error("Erreur de chargement des cours");
  }
};



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
    console.error("Erreur Impression:", error);
    alert("Erreur lors de la génération du document.");
  }
};

// --- NAVIGATION ---
const changePage = (link) => {
  if (!link.url || link.active) return;
  const urlParams = new URLSearchParams(link.url.split('?')[1]);
  pages.value = parseInt(urlParams.get('page')) || 1;
};

// --- WATCHERS & LIFECYCLE ---
watch(search, () => {
  pages.value = 1;
  searchCoursEtudiant();
});

watch(pages, searchCoursEtudiant);

onMounted(()=>{
  searchCoursEtudiant()  
});
</script>

<template>
  <div class="max-w-7xl px-4 mx-auto pb-16 text-slate-600">
        <div class="flex flex-wrap gap-3 mb-6"> 
      <router-link to="/ajouter-notes" class="btn-outline-green">
    Ajouter / Modifier notes
  </router-link>
 <button type="button" class="btn-outline-orange" @click="modalBulletin = true">Bulletin</button>
  </div>

    <div class="flex justify-end mt-8">
      <div class="w-full md:w-6/12 pb-2">
        <input 
          v-model="search" 
          type="text" 
          placeholder="Rechercher un étudiant..." 
          class="w-full px-4 py-2 border rounded-lg focus:ring-0 focus:border-sky-500 outline-none border-slate-200 mb-2"
        />
      </div>
    </div>

    <div class="mt-4 bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-center">
          <thead class="bg-slate-700 text-white uppercase text-xs">
            <tr>
              <th class="px-4 py-3">Identifiant</th>
              <th class="px-4 py-3">Nom</th>
              <th class="px-4 py-3">Prénom</th>
              <th class="px-4 py-3">Classe & Cycle</th>
              <th class="px-4 py-3">Année</th>
              <th class="px-4 py-3">Impression</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr 
              v-for="(note, index) in CoursEtudiantData.data" 
              :key="note.id"
              :class="index % 2 === 1 ? 'bg-slate-50' : ''"
              class="hover:bg-sky-50 transition-colors"
            >
              <td class="px-4 py-3 font-mono text-xs">{{ note.identifiant }}</td>
              <td class="px-4 py-3 font-bold">{{ note.fname }}</td>
              <td class="px-4 py-3">{{ note.lname }}</td>
              <td class="px-4 py-3">
                <div class="text-sky-600 font-medium">{{ note.name }}</div>
                <div class="text-[10px] text-slate-400">{{ note.nom_classe }}</div>
              </td>
              <td class="px-4 py-3 text-xs">{{ note.annee_academique }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-center gap-2">
                  
                  <div class="min-w-[100px]">
                    <select 
                      v-if="note.evaluation_par?.toLowerCase() === 'mois'" 
                      v-model="selections.mois"
                      class="select w-10"
                    >
                      <option value="all">Annuel</option>
                      <option v-for="k in month" :key="k" :value="k">{{ k }}</option>
                    </select>

                    <select 
                      v-else-if="note.evaluation_par === 'Trimestre'" 
                      v-model="selections.Trimestre"
                      class="select w-10"
                    >
                      <option value="" disabled selected>Trimestre</option>
                      <option v-for="t in EVAL_OPTIONS.trimestres" :key="t.id" :value="t.value">{{ t.title }}</option>
                    </select>

                    <select 
                      v-else-if="note.evaluation_par === 'Controle'" 
                      v-model="selections.Controle"
                      class="select w-10"
                    >
                      <option value="" disabled selected>Contrôle</option>
                      <option v-for="c in EVAL_OPTIONS.controles" :key="c.id" :value="c.value">{{ c.title }}</option>
                    </select>

                    <select 
                      v-else 
                      v-model="selections.session"
                      class="select w-10"
                    >
                      <option value="" disabled selected>Session</option>
                      <option v-for="s in EVAL_OPTIONS.sessions" :key="s.id" :value="s.value">{{ s.title }}</option>
                    </select>
                  </div>

                  <button 
                    @click="handlePrintBulletin(note.id,'imprime-bulletin', note.evaluation_par)"
                    class="p-2 bg-white border border-slate-200 rounded shadow-sm hover:text-sky-600 hover:border-sky-200 transition-all cursor-pointer"
                  >
                    <i class="ri-file-pdf-2-line"></i>
                  </button>

                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="CoursEtudiantData.meta" class="p-4 bg-slate-50 border-t flex justify-end gap-1">
        <button 
          v-for="link in CoursEtudiantData.meta.links" 
          :key="link.label"
          @click="changePage(link)"
          v-html="link.label"
          :disabled="!link.url"
          class="px-3 py-1 text-xs rounded transition-all"
          :class="link.active ? 'bg-sky-600 text-white shadow-md' : 'bg-white text-slate-500 border border-slate-200 hover:bg-slate-100'"
        ></button>
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
                  <button 
                    @click="handlePrintBulletin(id=false,'imprime-mas-bulletin', data_print.print_all)"
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
 