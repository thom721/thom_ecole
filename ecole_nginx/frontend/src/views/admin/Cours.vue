<script setup>
import { ref, onMounted, watch, watchEffect } from "vue";
import axios from "axios";
import AdminLayout from '@/layouts/AdminLayout.vue';
import StyleModal from "@/components/StyleModal.vue";
import Swal from 'sweetalert2';
import { useSchoolStore } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';
import Pagination from '@/components/Pagination.vue';
import InputLabel from "@/components/InputLabel.vue";
 
const schoolStore = useSchoolStore();
const { niveau, annee,classes,faculte,cours} = storeToRefs(schoolStore);

const url = import.meta.env.VITE_APP_BASE_URL;
defineOptions({ layout: AdminLayout });

const props = defineProps({
  faculte: Object,
  niveau: Object,
  annee: Object,
  filtersP: Object,
  filtersC: Object,
});

const activeTab          = ref('cours');
const transitioning      = ref(false);
const dataCours          = ref({ data: [] });
const dataProgramme      = ref({ data: [] });
const search_cours       = ref(props.filtersC?.search_cours || "");
const search_programme   = ref(props.filtersP?.search_programme || "");
const pages_cours        = ref(1);
const pages_prog         = ref(1);
const isModalHoraireOpen = ref(false);
const fetch_actual_class = ref([]);
const choseNiveau        = ref({});

const programme_niveau_id =ref('')
const programme_annee_academique =ref('')
const programme_class =ref('')

const formHoraire = ref({
  niveau_id: "", faculte_id: "",
  annee_academique: "", class: "", session: "",
});

const TABS = [
  { id: 'cours',      label: 'Cours',      icon: '📖' },
  { id: 'programmes', label: 'Programmes', icon: '🗂️' },
];

const searchCours = async (page=1) => {
  try {
    const res = await axios.get(`${url}/cours`, {
      params: { search: search_cours.value, page: page }
    });
    dataCours.value = res.data;
  } catch (e) { console.error(e); }
};

const searchProgramme = async (page=1) => {
  try {
    const res = await axios.get(`${url}/programme`, {
      params: { 
        search: search_programme.value, 
        page: page,
        class_id:programme_class.value,
        annee_academique_id:programme_annee_academique.value,
        niveau_id:programme_niveau_id.value
       }
    });
    dataProgramme.value = res.data;
  } catch (e) { console.error(e); }
};

const fetchNiveauDetails = async () => {
  if (!formHoraire.value.niveau_id) return;
  try {
    const res = await axios.get(`${url}/niveau-with-class/${formHoraire.value.niveau_id}`);
    choseNiveau.value        = res.data.niveau;
    fetch_actual_class.value = res.data.classe_actuelle;
  } catch (e) { console.error(e); }
};

const handlePrintHoraire = () => {
  const query = new URLSearchParams(formHoraire.value).toString();
  window.open(`${url}/print-horaire?${query}`, '_blank');
};

const deleteCours = (id) => {
  Swal.fire({
    title: 'Supprimer ce cours ?',
    text: "Cette action est irréversible.",
    icon: 'warning',
    background: '#13171f',
    color: '#c9d1d9',
    showCancelButton: true,
    confirmButtonColor: '#c0392b',
    cancelButtonColor: '#2d3748',
    confirmButtonText: 'Supprimer',
    cancelButtonText: 'Annuler',
  }).then(async (result) => {
    if (result.isConfirmed) {
      await axios.delete(`${url}/cours/${id}`);
      searchCours();
    }
  });
};

function switchTab(tabId) {
  if (tabId === activeTab.value || transitioning.value) return;
  transitioning.value = true;
  setTimeout(() => {
    activeTab.value = tabId;
    transitioning.value = false;
    if (tabId === 'programmes') searchProgramme();
  }, 180);
}

watch(programme_class,     () => { programme_class.value; searchProgramme(); });
watch(programme_niveau_id,     () => { programme_niveau_id.value; searchProgramme(); });
watch(programme_annee_academique,     () => { programme_annee_academique.value; searchProgramme(); });


watch(search_cours,     () => { pages_cours.value = 1; searchCours(); });
 

watch(search_programme, () => { pages_prog.value  = 1; searchProgramme(); });
watchEffect(pages_cours,  searchCours());
watchEffect(pages_prog,   searchProgramme());

onMounted(()=>{
  searchCours();
  searchProgramme()
  schoolStore.fetchAllDependencies();
});


const getClassesByNiveau = (niveauId) => { 
  if (!niveauId || !classes.value) return [];  
  return classes.value.filter(c => c.niveau_id === niveauId);
};


const handleNiveauChange =()=>{
getClassesByNiveau(programme_niveau_id.value)
}

</script>

<template>
  <div
    class="min-h-screen bg-[#0d1117] text-[#c9d1d9] px-4 sm:px-6 pb-7 max-w-6xl mx-auto animate-[fadeUp_0.4s_ease_both]"
    style="font-family:'DM Sans','Segoe UI',sans-serif"
  >

    <!-- ── Header ──────────────────────────────────────────────── -->
    <div class="flex flex-wrap items-center justify-between gap-4 mb-7">

      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-[#1f6feb]/10 border border-[#1f6feb]/20 flex items-center justify-center text-lg shrink-0">
          📚
        </div>
        <div>
          <h1 class="text-[17px] font-semibold text-[#e2e8f5] tracking-tight leading-tight m-0">
            Gestion académique
          </h1>
          <p class="text-[12px] text-[#3d4d62] mt-0.5 m-0">Cours, programmes et horaires</p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <!-- Ghost buttons -->
        <router-link
          to="/admin/ajouter-cours"
          class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-[12.5px] font-medium no-underline
                 bg-white/[0.04] text-[#6b7a90] border border-white/[0.07]
                 hover:bg-white/[0.07] hover:text-[#9aa5bb] transition-all duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
            <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
          </svg>
          Ajouter un cours
        </router-link>

        <router-link
          to="/admin/ajouter-programme"
          class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-[12.5px] font-medium no-underline
                 bg-white/[0.04] text-[#6b7a90] border border-white/[0.07]
                 hover:bg-white/[0.07] hover:text-[#9aa5bb] transition-all duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
            <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
          </svg>
          Nouveau programme
        </router-link>

        <!-- Primary button -->
        <button
          @click="isModalHoraireOpen = true"
          class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-[12.5px] font-medium text-white
                 bg-gradient-to-r from-[#2d5dd4] to-[#4a7cff] border border-white/10
                 shadow-[0_2px_10px_rgba(45,93,212,.28)]
                 hover:from-[#3568e8] hover:to-[#5a8cff]
                 hover:shadow-[0_4px_16px_rgba(45,93,212,.4)] hover:-translate-y-px
                 transition-all duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
            <path fill-rule="evenodd" d="M4 2a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2h.5A2.5 2.5 0 0 1 15 6.5v4A2.5 2.5 0 0 1 12.5 13H12v1a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-1h-.5A2.5 2.5 0 0 1 1 10.5v-4A2.5 2.5 0 0 1 3.5 4H4V2Zm2 0v2h4V2H6Zm-1 9v3h6v-3H5Zm8-4.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0Z" clip-rule="evenodd" />
          </svg>
          Imprimer horaire
        </button>
      </div>
    </div>

    <!-- ── Tab bar ─────────────────────────────────────────────── -->
    <div class="flex gap-0.5 bg-[#161b22] border border-white/[0.06] rounded-xl p-1 w-fit mb-5">
      <button
        v-for="tab in TABS" :key="tab.id"
        type="button"
        @click="switchTab(tab.id)"
        :class="[
          'flex items-center gap-2 px-5 py-2 rounded-[9px] text-[13px] font-medium transition-all duration-200',
          activeTab === tab.id
            ? 'bg-[#21262d] text-[#e2e8f5] shadow-[0_1px_4px_rgba(0,0,0,.4)]'
            : 'text-[#4a5568] hover:text-[#8a95a8] hover:bg-white/[0.03]'
        ]"
      >
        <span class="text-sm">{{ tab.icon }}</span>
        {{ tab.label }}
        <span :class="[
          'text-[10px] font-semibold font-mono px-1.5 py-px rounded-full transition-all duration-200',
          activeTab === tab.id
            ? 'bg-[#1f6feb]/15 text-[#7aaeff]'
            : 'bg-white/[0.06] text-[#3d4d62]'
        ]">
          {{ tab.id === 'cours' ? (dataCours.data?.length ?? 0) : (dataProgramme.data?.length ?? 0) }}
        </span>
      </button>
    </div>

    <!-- ── Tab content with transition ────────────────────────── -->
    <Transition name="tab-slide" mode="out-in">

      <!-- ══ COURS ══ -->
      <div v-if="activeTab === 'cours'" key="cours">

        <!-- Toolbar -->
        <div class="flex items-center justify-between gap-3 mb-3">
          <div class="relative flex-1 max-w-sm">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
              class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#3d4d62] pointer-events-none">
              <path fill-rule="evenodd" d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" clip-rule="evenodd" />
            </svg>
            <input
              v-model="search_cours" type="text"
              placeholder="Rechercher un cours..."
              class="w-full bg-[#161b22] border border-white/[0.07] rounded-lg
                     pl-8 pr-3 py-[7px] text-[13px] text-[#c9d1d9] placeholder-[#2e3a4a]
                     outline-none focus:border-[#4a7cff]/40 focus:ring-2 focus:ring-[#4a7cff]/[0.08]
                     transition-all duration-150"
            />
          </div>
          <span class="text-[11px] text-[#3d4d62] shrink-0">{{ dataCours.data?.length ?? 0 }} résultat(s)</span>
        </div>

        <!-- Table -->
        <div class="bg-[#161b22] border border-white/[0.06] rounded-xl overflow-hidden">
          <table class="w-full border-collapse">
            <thead>
              <tr class="bg-[#0d1117] border-b border-white/[0.05]">
                <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62] w-10">#</th>
                <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Nom du cours</th>
                <th class="px-4 py-2.5 text-right text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(cours, i) in dataCours.data" :key="cours.id"
                class="border-b border-white/[0.04] last:border-0
                       hover:bg-white/[0.02] transition-colors duration-100
                       [animation:rowIn_.2s_ease_both]"
                :style="{ animationDelay: `${i * 28}ms` }"
              >
                <td class="px-4 py-2.5 text-[11px] font-mono text-[#2e3a4a]">{{ i + 1 }}</td>
                <td class="px-4 py-2.5">
                  <div class="flex items-center gap-2.5">
                    <span class="w-1.5 h-1.5 rounded-full bg-[#4a7cff]/50 shrink-0"></span>
                    <span class="text-[13px] font-medium text-[#c9d1d9]">{{ cours.cours_nom }}</span>
                  </div>
                </td>
                <td class="px-4 py-2.5">
                  <div class="flex items-center justify-end gap-1">
                    <button
                      class="w-7 h-7 rounded-lg flex items-center justify-center text-[#3d4d62]
                             border border-transparent
                             hover:bg-[#4a7cff]/10 hover:border-[#4a7cff]/20 hover:text-[#7aaeff]
                             transition-all duration-150"
                      title="Modifier"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
                        <path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.848 2.047a.75.75 0 0 0 .98.98l2.047-.848a2.75 2.75 0 0 0 .892-.596l4.261-4.262a1.75 1.75 0 0 0 0-2.474Z" />
                        <path d="M4.75 3.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V9A.75.75 0 0 1 14 9v2.25A2.75 2.75 0 0 1 11.25 14h-6.5A2.75 2.75 0 0 1 2 11.25v-6.5A2.75 2.75 0 0 1 4.75 2H7a.75.75 0 0 1 0 1.5H4.75Z" />
                      </svg>
                    </button>
                    <button
                      @click="deleteCours(cours.id)"
                      class="w-7 h-7 rounded-lg flex items-center justify-center text-[#3d4d62]
                             border border-transparent
                             hover:bg-red-500/10 hover:border-red-500/20 hover:text-red-400
                             transition-all duration-150"
                      title="Supprimer"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
                        <path fill-rule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Zm2.25-.75a.75.75 0 0 0-.75.75V4h3v-.75a.75.75 0 0 0-.75-.75h-1.5ZM6.05 6a.75.75 0 0 1 .787.713l.275 5.5a.75.75 0 0 1-1.498.075l-.275-5.5A.75.75 0 0 1 6.05 6Zm3.9 0a.75.75 0 0 1 .712.787l-.275 5.5a.75.75 0 0 1-1.498-.075l.275-5.5A.75.75 0 0 1 9.95 6Z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="!dataCours.data?.length">
                <td colspan="3" class="py-14 text-center text-[#3d4d62] text-[13px]">
                  <span class="text-3xl block mb-2">📭</span>Aucun cours trouvé
                </td>
              </tr>
            </tbody>
          </table>
          
              <div
                  v-if="dataCours.meta"
                  class="mt-2 flex justify-end"
                > 
                <Pagination
                    :meta="dataCours.meta" 
                    @change-page="searchCours" 
                  />
              </div>
        </div>
      </div>

      <!-- ══ PROGRAMMES ══ -->
      <div v-else-if="activeTab === 'programmes'" key="programmes">

        <!-- Toolbar -->
        <div class="flex flex-col md:flex-row items-center justify-between gap-3 mb-3">
          <div class="relative w-full">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
              class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#3d4d62] pointer-events-none">
              <path fill-rule="evenodd" d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" clip-rule="evenodd" />
            </svg>
            <input
              v-model="search_programme" type="text"
              placeholder="Filtrer les programmes..."
              class="w-full bg-[#161b22] border border-white/[0.07] rounded-lg
                     pl-8 pr-3 py-[7px] text-[13px] text-[#c9d1d9] placeholder-[#2e3a4a]
                     outline-none focus:border-[#4a7cff]/40 focus:ring-2 focus:ring-[#4a7cff]/[0.08]
                     transition-all duration-150"
            />

          </div>

          <div class="w-full">
            <InputLabel value="Niveau d'étude" />
            <select v-model="programme_niveau_id" @change="handleNiveauChange" class="field-input">
              <option value="" disabled>Choisir Niveau</option>
              <option v-for="n in niveau" :key="n.id" :value="n.id">{{ n.name }}</option>
            </select>
           
          </div>

         <div class="w-full">
            <InputLabel value="Année Académique" />
            <select v-model="programme_annee_academique" class="field-input">
              <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
            </select>
          </div>

        <div class="w-full">
            <InputLabel value="Classe" />
              <select v-model="programme_class" class="field-input">
               <option value="" disabled>Choisir Classe</option>
               <option v-for="cls in getClassesByNiveau(programme_niveau_id)" 
                         :key="cls.id" 
                         :value="cls.id">
               {{ cls.nom_classe }}
               </option>
               </select>
          </div>
 

          <span class="text-[11px] text-[#3d4d62] shrink-0">{{ dataProgramme.data?.length ?? 0 }} résultat(s)</span>
        </div>

        <!-- Table -->
        <div class="bg-[#161b22] border border-white/[0.06] rounded-xl overflow-hidden">
          <table class="w-full border-collapse">
            <thead>
              <tr class="bg-[#0d1117] border-b border-white/[0.05]">
                <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Cours</th>
                <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Professeur</th>
                <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Niveau</th>
                <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Classe</th>
                <th class="px-4 py-2.5 text-right text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Année</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(prog, i) in dataProgramme.data" :key="prog.id"
                class="border-b border-white/[0.04] last:border-0
                       hover:bg-white/[0.02] transition-colors duration-100
                       [animation:rowIn_.2s_ease_both]"
                :style="{ animationDelay: `${i * 28}ms` }"
              >
                <td class="px-4 py-2.5">
                  <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-[#a78bfa]/50 shrink-0"></span>
                    <span class="text-[13px] font-medium text-[#c9d1d9]">{{ prog.cours }}</span>
                  </div>
                </td>
                <td class="px-4 py-2.5">
                  <span class="inline-flex text-[11px] px-2 py-0.5 rounded-full font-medium
                               bg-[#4a7cff]/10 text-[#7aaeff] border border-[#4a7cff]/15">
                    {{ prog.professeur }}
                  </span>
                </td>
                <td class="px-4 py-2.5">
                  <span class="inline-flex text-[11px] px-2 py-0.5 rounded-full font-medium
                               bg-white/[0.05] text-[#6b7a90] border border-white/[0.08]">
                    {{ prog.niveau_name }}
                  </span>
                </td>
                <td class="px-4 py-2.5 text-[12px] text-[#5c6880]">{{ prog.classe }}</td>
                <td class="px-4 py-2.5 text-right">
                  <span class="font-mono text-[11px] text-[#5c6880] bg-[#0d1017] border border-[#1e2535] px-2 py-0.5 rounded">
                    {{ prog.annee_academique }}
                  </span>
                </td>
              </tr>
              <tr v-if="!dataProgramme.data?.length">
                <td colspan="5" class="py-14 text-center text-[#3d4d62] text-[13px]">
                  <span class="text-3xl block mb-2">📭</span>Aucun programme trouvé
                </td>
              </tr>
            </tbody>
          </table>
          
              <div
                  v-if="dataProgramme.meta"
                  class="mt-2 flex justify-end"
                > 
                <Pagination
                    :meta="dataProgramme.meta" 
                    @change-page="searchProgramme" 
                  />
              </div>
        </div>
      </div>

    </Transition>

    <!-- ── Modal Horaire ────────────────────────────────────────── -->
    <StyleModal :show="isModalHoraireOpen" @close="isModalHoraireOpen = false" max-width="lg">

      <template #icon>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
          <path fill-rule="evenodd" d="M4 2a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2h.5A2.5 2.5 0 0 1 15 6.5v4A2.5 2.5 0 0 1 12.5 13H12v1a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-1h-.5A2.5 2.5 0 0 1 1 10.5v-4A2.5 2.5 0 0 1 3.5 4H4V2Zm2 0v2h4V2H6Zm-1 9v3h6v-3H5Zm8-4.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0Z" clip-rule="evenodd" />
        </svg>
      </template>
      <template #title>Imprimer l'horaire</template>
      <template #subtitle>Configurez les filtres puis générez le PDF.</template>

      <template #content>
        <form id="horaire-form" @submit.prevent="handlePrintHoraire" class="flex flex-col gap-4">

          <!-- Niveau -->
          <div class="flex flex-col gap-1.5">
            <label class="text-[11px] font-medium uppercase tracking-[0.06em] text-[#3d4d62]">
              Niveau d'étude
            </label>
            <div class="relative">
              <select
                v-model="formHoraire.niveau_id" @change="fetchNiveauDetails"
                class="w-full bg-[#0d1017] border border-white/[0.08] rounded-lg
                       px-3 py-2 pr-8 text-[13px] text-[#c9d1d9] appearance-none cursor-pointer
                       outline-none focus:border-[#4a7cff]/40 focus:ring-2 focus:ring-[#4a7cff]/[0.08]
                       transition-all duration-150"
              >
                <option value="" disabled>Sélectionner un niveau</option>
                <option v-for="n in niveau" :key="n.id" :value="n.id" class="bg-[#13171f]">{{ n.name }}</option>
              </select>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
                class="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#2e3a4a] pointer-events-none">
                <path fill-rule="evenodd" d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>

          <!-- Faculté conditionnelle -->
          <Transition name="accordion">
            <div v-if="choseNiveau.name === 'Universitaire'" class="flex flex-col gap-1.5">
              <label class="text-[11px] font-medium uppercase tracking-[0.06em] text-[#3d4d62]">Faculté / Option</label>
              <div class="relative">
                <select
                  v-model="formHoraire.faculte_id"
                  class="w-full bg-[#0d1017] border border-white/[0.08] rounded-lg
                         px-3 py-2 pr-8 text-[13px] text-[#c9d1d9] appearance-none cursor-pointer
                         outline-none focus:border-[#4a7cff]/40 focus:ring-2 focus:ring-[#4a7cff]/[0.08]
                         transition-all duration-150"
                >
                  <option value="" disabled>Sélectionner</option>
                  <option v-for="f in faculte" :key="f.id" :value="f.id" class="bg-[#13171f]">{{ f.nom }}</option>
                </select>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
                  class="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#2e3a4a] pointer-events-none">
                  <path fill-rule="evenodd" d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </Transition>

          <!-- Classe + Année -->
          <div class="grid grid-cols-2 gap-3">
            <div class="flex flex-col gap-1.5">
              <label class="text-[11px] font-medium uppercase tracking-[0.06em] text-[#3d4d62]">Classe</label>
              <div class="relative">
                <select
                  v-model="formHoraire.class"
                  class="w-full bg-[#0d1017] border border-white/[0.08] rounded-lg
                         px-3 py-2 pr-8 text-[13px] text-[#c9d1d9] appearance-none cursor-pointer
                         outline-none focus:border-[#4a7cff]/40 focus:ring-2 focus:ring-[#4a7cff]/[0.08]
                         transition-all duration-150"
                >
                  <option value="" disabled>Sélectionner</option>
                  <option v-for="c in fetch_actual_class" :key="c.id" :value="c.id" class="bg-[#13171f]">{{ c.nom_classe }}</option>
                </select>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
                  class="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#2e3a4a] pointer-events-none">
                  <path fill-rule="evenodd" d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-[11px] font-medium uppercase tracking-[0.06em] text-[#3d4d62]">Année académique</label>
              <div class="relative">
                <select
                  v-model="formHoraire.annee_academique"
                  class="w-full bg-[#0d1017] border border-white/[0.08] rounded-lg
                         px-3 py-2 pr-8 text-[13px] text-[#c9d1d9] appearance-none cursor-pointer
                         outline-none focus:border-[#4a7cff]/40 focus:ring-2 focus:ring-[#4a7cff]/[0.08]
                         transition-all duration-150"
                >
                  <option value="" disabled>Sélectionner</option>
                  <option v-for="a in annee" :key="a.id" :value="a.id" class="bg-[#13171f]">{{ a.annee_academique }}</option>
                </select>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
                  class="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#2e3a4a] pointer-events-none">
                  <path fill-rule="evenodd" d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>

        </form>
      </template>

      <!-- Footer — lié au form via id -->
      <template #footer>
        <button
          type="button"
          @click="isModalHoraireOpen = false"
          class="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-[13px] font-medium
                 bg-white/[0.04] text-[#5c6880] border border-white/[0.07]
                 hover:bg-white/[0.07] hover:text-[#8a95a8] transition-all duration-150"
        >
          Annuler
        </button>
        <button
          type="submit"
          form="horaire-form"
          class="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-[13px] font-medium text-white
                 bg-gradient-to-r from-[#2d5dd4] to-[#4a7cff] border border-white/10
                 shadow-[0_2px_10px_rgba(45,93,212,.28)]
                 hover:from-[#3568e8] hover:to-[#5a8cff]
                 hover:shadow-[0_4px_14px_rgba(45,93,212,.4)] hover:-translate-y-px
                 transition-all duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
            <path fill-rule="evenodd" d="M4 2a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2h.5A2.5 2.5 0 0 1 15 6.5v4A2.5 2.5 0 0 1 12.5 13H12v1a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-1h-.5A2.5 2.5 0 0 1 1 10.5v-4A2.5 2.5 0 0 1 3.5 4H4V2Zm2 0v2h4V2H6Zm-1 9v3h6v-3H5Zm8-4.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0Z" clip-rule="evenodd" />
          </svg>
          Générer le PDF
        </button>
      </template>

    </StyleModal>
  </div>
</template>

<style scoped>
/* 3 animations impossibles en Tailwind pur — c'est tout */
.tab-slide-enter-active, .tab-slide-leave-active {
  transition: opacity .18s ease, transform .18s ease;
}
.tab-slide-enter-from { opacity: 0; transform: translateY(7px); }
.tab-slide-leave-to   { opacity: 0; transform: translateY(-5px); }

.accordion-enter-active, .accordion-leave-active {
  transition: all .22s ease; overflow: hidden;
}
.accordion-enter-from, .accordion-leave-to  { opacity: 0; max-height: 0; }
.accordion-enter-to, .accordion-leave-from  { opacity: 1; max-height: 120px; }

@keyframes rowIn {
  from { opacity: 0; transform: translateX(-5px); }
  to   { opacity: 1; transform: translateX(0); }
}
</style>
