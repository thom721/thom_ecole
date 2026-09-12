<script setup>
import { ref, computed, onMounted, watch, reactive } from "vue";
import axios from "axios";
import Swal from 'sweetalert2';
import { useSchoolStore,useSchoolStoreInfo } from '@/stores/schoolStore';
import { useAuthStore } from '@/stores/auth';
 import StyleModal from '@/components/StyleModal.vue';
import DataTable from '@/components/DataTable.vue'
import { usePdfWithLoading } from '@/stores/usePdf';
const { submitPdf, loading, error, loadingMap } = usePdfWithLoading()

const authStore = useAuthStore();
const {classes_global,annee_global,niveau_global} =useSchoolStoreInfo()
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
  // value = "<session>::<phase>" — encode les deux dimensions dans un seul
  // select (le DataTable générique ne garde qu'UNE sélection par ligne, voir
  // buildBulletinPayload) : phase parmi 'all'/'intra'/'finale', exigé tel
  // quel par /imprime-bulletin pour ce niveau (voir BulletinPrint.py).
  sessions: [
    { id: 1, value: '1ère::all',    title: '1ère Session — Intra + Finale' },
    { id: 2, value: '1ère::intra',  title: '1ère Session — Intra' },
    { id: 3, value: '1ère::finale', title: '1ère Session — Finale' },
    { id: 4, value: '2ème::all',    title: '2ème Session — Intra + Finale' },
    { id: 5, value: '2ème::intra',  title: '2ème Session — Intra' },
    { id: 6, value: '2ème::finale', title: '2ème Session — Finale' },
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

// Les étudiants Universitaire (système bloc) n'ont pas de ParamExam.evaluation_par
// (colonne "periode" retombe donc sur EVAL_OPTIONS.sessions, seule option restante,
// voir action "periode" plus bas) — leur bulletin est routé par session ('1ère'/'2ème'),
// pas par mois : /imprime-bulletin exige alors `session` + `mois` parmi
// 'intra'/'finale'/'all' (voir BulletinPrint.py::impression_bulletin), jamais un mois classique.
const isSessionValue = (val) => EVAL_OPTIONS.sessions.some(s => s.value === val)
const buildBulletinPayload = (rowId, selection) => {
  if (isSessionValue(selection)) {
    const [session, phase] = selection.split('::')
    return { bulletin: rowId, session, mois: phase }
  }
  return { bulletin: rowId, mois: selection }
}

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

// --- SUPPRESSION GROUPÉE DE NOTES ---------------------------------------
// Action destructive et irréversible : on impose un aperçu (comptage) à
// jour avant d'autoriser la suppression, et toute modification d'un des
// 4 filtres invalide l'aperçu déjà obtenu pour éviter de supprimer sur la
// base d'une sélection différente de celle vérifiée.
const modalDeleteNotes = ref(false);
const deleteFilters = reactive({
  niveau_id: "",
  classe_id: "",
  annee_academique: "",
  mois: "",
  identifiant: "", // optionnel — restreint la suppression à UN étudiant de la classe
});
const deletePreview = ref(null); // { etudiants_concernes, notes_a_supprimer } | null
const deletePreviewLoading = ref(false);
const deleteInFlight = ref(false);

const classesForDeleteNiveau = computed(() =>
  (classes_global ?? []).filter((c) => c.niveau_id === deleteFilters.niveau_id)
);

const deleteFiltersComplete = computed(() =>
  !!(deleteFilters.niveau_id && deleteFilters.classe_id && deleteFilters.annee_academique && deleteFilters.mois)
);

// undefined (pas "") pour qu'axios omette le paramètre/champ plutôt que
// d'envoyer une chaîne vide — même comportement que côté Flutter
// (note_state.dart::previewDeleteNotes/deleteNotes).
const trimmedIdentifiant = computed(() => deleteFilters.identifiant.trim() || undefined);

watch(
  () => [deleteFilters.niveau_id, deleteFilters.classe_id, deleteFilters.annee_academique, deleteFilters.mois, deleteFilters.identifiant],
  () => { deletePreview.value = null; }
);
watch(
  () => deleteFilters.niveau_id,
  () => { deleteFilters.classe_id = ""; }
);

const openDeleteNotesModal = () => {
  deleteFilters.niveau_id = "";
  deleteFilters.classe_id = "";
  deleteFilters.annee_academique = "";
  deleteFilters.mois = "";
  deleteFilters.identifiant = "";
  deletePreview.value = null;
  modalDeleteNotes.value = true;
};
const closeDeleteNotesModal = () => { modalDeleteNotes.value = false; };

const previewDeleteNotes = async () => {
  if (!deleteFiltersComplete.value) return;
  deletePreviewLoading.value = true;
  deletePreview.value = null;
  try {
    const { data } = await axios.get(`${url}/coursEtudiant/notes/apercu-suppression`, {
      params: {
        niveau_id: deleteFilters.niveau_id,
        classe_id: deleteFilters.classe_id,
        annee_academique: deleteFilters.annee_academique,
        mois: deleteFilters.mois,
        identifiant: trimmedIdentifiant.value,
      },
    });
    deletePreview.value = data;
  } catch (e) {
    console.error("Erreur aperçu suppression notes:", e);
    Swal.fire({ icon: "error", text: e.response?.data?.detail?.errors || "Erreur lors de l'aperçu." });
  } finally {
    deletePreviewLoading.value = false;
  }
};

const confirmDeleteNotes = async () => {
  if (!deletePreview.value || deletePreview.value.notes_a_supprimer === 0) return;

  const { value: typed } = await Swal.fire({
    icon: "warning",
    title: "Suppression définitive",
    html: `Vous allez supprimer <b>${deletePreview.value.notes_a_supprimer}</b> note(s) `
        + `pour <b>${deletePreview.value.etudiants_concernes}</b> étudiant(s) `
        + `(${deleteFilters.mois}, ${deleteFilters.annee_academique})`
        + (trimmedIdentifiant.value ? ` — étudiant <b>${trimmedIdentifiant.value}</b> uniquement` : "") + `. `
        + `Cette action est irréversible.<br><br>Tapez <b>SUPPRIMER</b> pour confirmer.`,
    input: "text",
    inputPlaceholder: "SUPPRIMER",
    showCancelButton: true,
    confirmButtonText: "Supprimer définitivement",
    confirmButtonColor: "#dc2626",
    cancelButtonText: "Annuler",
    inputValidator: (value) => (value !== "SUPPRIMER" ? 'Veuillez taper exactement "SUPPRIMER".' : undefined),
  });
  if (typed !== "SUPPRIMER") return;

  deleteInFlight.value = true;
  try {
    const { data } = await axios.delete(`${url}/coursEtudiant/notes/suppression`, {
      data: {
        niveau_id: deleteFilters.niveau_id,
        classe_id: deleteFilters.classe_id,
        annee_academique: deleteFilters.annee_academique,
        mois: deleteFilters.mois,
        identifiant: trimmedIdentifiant.value,
      },
    });
    Swal.fire({ icon: "success", text: data.success, timer: 2500, showConfirmButton: false });
    deletePreview.value = null;
    closeDeleteNotesModal();
  } catch (e) {
    console.error("Erreur suppression notes:", e);
    Swal.fire({ icon: "error", text: e.response?.data?.detail?.errors || "Erreur lors de la suppression." });
  } finally {
    deleteInFlight.value = false;
  }
};


 const columns = [
  { key: 'identifiant', label: 'Identifiant' },
  { key: 'fname',       label: 'Nom',    badge: true },
  { key: 'lname',       label: 'Prénom', nowrap: true },
  { key: 'nom_classe',  label: "Session / Année d'étude", semibold: true },
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
      
      await submitPdf('/imprime-bulletin', buildBulletinPayload(row.id, selection), index)
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

  <button v-if="authStore.hasPermission('Supprimer note')" type="button" @click="openDeleteNotesModal"
    class="btn-red">
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/>
    </svg>
    Supprimer notes
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
          
          @click="submitPdf('/imprime-bulletin', buildBulletinPayload(row.id, selection), row.id)"
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
                  <label class="text-sm">Session / Année d'étude</label>
                  <select v-model="data_print.print_all.classe" class="input-select">
                    <option value="" disabled>Choisir la session/année d'étude</option>
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

    <StyleModal :show="modalDeleteNotes" max-width="2xl" @close="closeDeleteNotesModal">
        <template #title>
            <div class="flex justify-between items-center py-2">
                <p class="text-lg text-gray-800">Supprimer des notes</p>
                <p class="far fa-circle-xmark text-xl text-red-500 cursor-pointer hover:scale-110 transition flex justify-end" @click="closeDeleteNotesModal"></p>
            </div>
        </template>
        <template #content>
            <p class="text-sm text-slate-500 mb-3">
              Supprime les notes d'un mois précis pour tous les étudiants du niveau / classe / année choisis (ou un seul étudiant si son identifiant est précisé ci-dessous). Cette action est irréversible.
            </p>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm">Niveau</label>
                <select v-model="deleteFilters.niveau_id" class="input-select">
                  <option value="" disabled>Choisir un niveau</option>
                  <option v-for="n in niveau_global" :key="n.id" :value="n.id">{{ n.name }}</option>
                </select>
              </div>
              <div>
                <label class="text-sm">Session / Année d'étude</label>
                <select v-model="deleteFilters.classe_id" class="input-select" :disabled="!deleteFilters.niveau_id">
                  <option value="" disabled>Choisir une session/année d'étude</option>
                  <option v-for="c in classesForDeleteNiveau" :key="c.id" :value="c.id">{{ c.nom_classe }}</option>
                </select>
              </div>
              <div>
                <label class="text-sm">Année académique</label>
                <select v-model="deleteFilters.annee_academique" class="input-select">
                  <option value="" disabled>Choisir une année</option>
                  <option v-for="a in annee_global" :key="a.id" :value="a.annee_academique">{{ a.annee_academique }}</option>
                </select>
              </div>
              <div>
                <label class="text-sm">Mois</label>
                <select v-model="deleteFilters.mois" class="input-select">
                  <option value="" disabled>Choisir le mois</option>
                  <option v-for="m in month" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>
            </div>

            <div class="pt-4">
              <label class="text-sm">Étudiant (optionnel)</label>
              <input type="text" v-model="deleteFilters.identifiant" class="input-select"
                placeholder="Identifiant — laissez vide pour toute la session/année d'étude" />
            </div>

            <div class="pt-4 flex items-center gap-3">
              <button type="button" class="btn-outline-sky disabled:opacity-40 disabled:cursor-not-allowed"
                :disabled="!deleteFiltersComplete || deletePreviewLoading" @click="previewDeleteNotes">
                <span v-if="!deletePreviewLoading">Vérifier</span>
                <span v-else>Vérification…</span>
              </button>

              <div v-if="deletePreview" class="text-sm">
                <span v-if="deletePreview.notes_a_supprimer === 0" class="text-slate-400">
                  Aucune note trouvée pour ces critères.
                </span>
                <span v-else class="text-amber-500 font-semibold">
                  {{ deletePreview.notes_a_supprimer }} note(s) pour {{ deletePreview.etudiants_concernes }} étudiant(s) seront supprimées.
                </span>
              </div>
            </div>

            <div class="pt-4 flex justify-end">
              <button type="button" class="btn-red disabled:opacity-40 disabled:cursor-not-allowed"
                :disabled="!deletePreview || deletePreview.notes_a_supprimer === 0 || deleteInFlight"
                @click="confirmDeleteNotes">
                <span v-if="!deleteInFlight">Supprimer définitivement</span>
                <span v-else>Suppression…</span>
              </button>
            </div>
        </template>
    </StyleModal>
  </div>
</template>
 