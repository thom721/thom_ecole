<script setup>
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import AdminLayout from '@/layouts/AdminLayout.vue'; 
import InputError from "@/components/InputError.vue";
import InputLabel from "@/components/InputLabel.vue";
import PrimaryButton from "@/components/PrimaryButton.vue";
import DialogModal from "@/components/DialogModal.vue";
import DangerButton from "@/components/DangerButton.vue";
import Swal from 'sweetalert2';

const url = import.meta.env.VITE_APP_BASE_URL;

defineOptions({ layout: AdminLayout });

const props = defineProps({
  faculte: Object,
  niveau: Object,
  annee: Object,
  professeur: Object,
  filtersP: Object,
  filtersC: Object,
});

// --- ÉTATS ---
const activeTab = ref('cours'); // Gère l'affichage des onglets (cours, programmes, horaire)
const dataCours = ref({ data: [], meta: { links: [] } });
const dataProgramme = ref({ data: [], meta: { links: [] } });

const search_cours = ref(props.filtersC?.search_cours || "");
const search_programme = ref(props.filtersP?.search_programme || "");
const pages_cours = ref(1);
const pages_prog = ref(1);

const isModalHoraireOpen = ref(false);
const fetch_actual_class = ref([]);
const choseNiveau = ref({});

// --- FORMULAIRES (OBJETS RÉACTIFS) ---
const formHoraire = ref({
  niveau_id: "",
  faculte_id: "",
  annee_academique: "",
  class: "",
  session: "",
});

// --- LOGIQUE API ---
const searchCours = async () => {
  try {
    const res = await axios.get(`${url}/cours`, {
      params: { search: search_cours.value, page: pages_cours.value }
    });
    dataCours.value = res.data;
  } catch (e) { console.error(e); }
};

const searchProgramme = async () => {
  try {
    const res = await axios.get(`${url}/programme`, {
      params: { search: search_programme.value, page: pages_prog.value }
    });
    dataProgramme.value = res.data;
  } catch (e) { console.error(e); }
};

const fetchNiveauDetails = async () => {
  if (!formHoraire.value.niveau_id) return;
  try {
    const res = await axios.get(`${url}/niveau-with-class/${formHoraire.value.niveau_id}`);
    choseNiveau.value = res.data.niveau;
    fetch_actual_class.value = res.data.classe_actuelle;
  } catch (e) { console.error(e); }
};

// --- ACTIONS ---
const handlePrintHoraire = () => {
  const query = new URLSearchParams(formHoraire.value).toString();
  window.open(`${url}/print-horaire?${query}`, '_blank');
};

const deleteCours = (id) => {
  Swal.fire({
    title: 'Supprimer ?',
    text: "Cette action est irréversible",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    confirmButtonText: 'Supprimer'
  }).then(async (result) => {
    if (result.isConfirmed) {
      await axios.delete(`${url}/cours/${id}`);
      searchCours();
    }
  });
};

// --- WATCHERS ---
watch(search_cours, () => { pages_cours.value = 1; searchCours(); });
watch(search_programme, () => { pages_prog.value = 1; searchProgramme(); });
watch(pages_cours, searchCours);
watch(pages_prog, searchProgramme);

onMounted(() => {
  searchCours();
});
</script>

<template>
  <div class="max-w-7xl px-4 mx-auto pt-6 pb-14 text-slate-600">
    
    <div class="flex flex-wrap gap-3 mb-6"> 
      <router-link to="/admin/ajouter-cours" class="btn-outline-green">
    Ajouter Cours
  </router-link>
  <router-link to="/admin/ajouter-programme" class="btn-outline-sky">
    Nouveau Programme
  </router-link>
      <button @click="isModalHoraireOpen = true" class="btn-outline-orange">Imprimer Horaire</button>
    </div>

    <div class="bg-sky-50 p-1 rounded-xl flex gap-1 mb-6 border border-sky-100 shadow-sm">
      <button 
        v-for="tab in ['cours', 'programmes', 'horaire']" 
        :key="tab"
        @click="activeTab = tab; tab === 'programmes' ? searchProgramme() : null"
        class="flex-1 py-2 text-sm font-medium rounded-lg transition-all capitalize"
        :class="activeTab === tab ? 'bg-white text-sky-600 shadow-sm' : 'text-slate-500 hover:text-sky-500'"
      >
        {{ tab }}
      </button>
    </div>

    <div v-if="activeTab === 'cours'" class="space-y-4">
     
          <div class="flex justify-end py-2">
  <div class="w-full md:w-6/12">
        <input 
          v-model="search" 
          type="text" 
          placeholder="Rechercher un cours..." 
          class="w-full px-4 py-2 border rounded-lg focus:ring-0 focus:border-sky-500 outline-none border-slate-200 mb-2"
        />
      </div>
    </div>
      
      <div class="table-container">
        <table class="w-full text-sm">
          <thead class="bg-slate-700 text-white">
            <tr>
              <th class="px-4 py-2 text-center">Nom</th>
              <th class="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody class="">
            <tr v-for="cours in dataCours.data" :key="cours.id" class="hover:bg-slate-50">
              <td class="px-4 py-2 font-medium text-center">{{ cours.cours_nom }}</td>
              <td class="px-4 py-2 space-x-10">
                <button @click="() => {}" class="text-yellow-500 hover:scale-110 mr-3"><i class="ri-edit-circle-fill"></i></button>
                <button @click="deleteCours(cours.id)" class="text-red-500 hover:scale-110"><i class="ri-delete-bin-6-line"></i></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="activeTab === 'programmes'" class="space-y-4">
   

          <div class="flex justify-end pt-4">
      <div class="w-full md:w-5/12">
        <input 
          v-model="search_programme" 
          type="text" 
          placeholder="Filtrer les programmes..." 
          class="w-full px-4 py-2 border rounded-lg focus:ring-0 focus:border-sky-500 outline-none border-slate-200"
        />
      </div>
    </div> 
      <div class="table-container">
        <table class="w-full text-sm">
          <thead class="bg-slate-700 text-white">
            <tr>
              <th class="px-4 py-2 text-center">Cours</th>
              <th class="px-4 py-2 text-center">Professeur</th>
              <th class="px-4 py-2 text-center">Niveau/Cycle</th>
              <th class="px-4 py-2 text-center">Classe</th>
              <th class="px-4 py-2 text-center">Année</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="prog in dataProgramme.data" :key="prog.id" class="hover:bg-slate-50">
              <td class="px-4 py-2 text-center">{{ prog.cours }}</td>
              <td class="px-4 py-2 text-center text-xs">{{ prog.professeur }}</td>
              <td class="px-4 py-2 text-center">{{ prog.niveau_name }}</td>
              <td class="px-4 py-2 text-center">{{ prog.classe }}</td>
              <td class="px-4 py-2 text-center font-mono text-xs">{{ prog.annee_academique }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <DialogModal :show="isModalHoraireOpen" @close="isModalHoraireOpen = false">
      <template #title>Imprimer l'horaire de cours</template>
      <template #content>
        <div class="space-y-4 pt-4">
          <div>
            <InputLabel value="Niveau d'étude" />
            <select v-model="formHoraire.niveau_id" @change="fetchNiveauDetails" class="input-modern">
              <option value="" disabled>Sélectionner un niveau</option>
              <option v-for="n in niveau" :key="n.id" :value="n.id">{{ n.name }}</option>
            </select>
          </div>

          <div v-if="choseNiveau.name === 'Universitaire'">
            <InputLabel value="Faculté / Option" />
            <select v-model="formHoraire.faculte_id" class="input-modern">
              <option v-for="f in faculte" :key="f.id" :value="f.id">{{ f.nom }}</option>
            </select>
          </div>

          <div>
            <InputLabel value="Classe" />
            <select v-model="formHoraire.class" class="input-modern">
              <option v-for="c in fetch_actual_class" :key="c.id" :value="c.id">{{ c.nom_classe }}</option>
            </select>
          </div>

          <div>
            <InputLabel value="Année Académique" />
            <select v-model="formHoraire.annee_academique" class="input-modern">
              <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
            </select>
          </div>
        </div>
      </template>
      <template #footer>
        <div class="flex gap-2">
            <DangerButton @click="isModalHoraireOpen = false">Annuler</DangerButton>
            <PrimaryButton @click="handlePrintHoraire">Imprimer PDF</PrimaryButton>
        </div>
      </template>
    </DialogModal>
  </div>
</template>

 