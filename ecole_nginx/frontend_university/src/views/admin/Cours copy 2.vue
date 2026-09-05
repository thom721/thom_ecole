<script setup>
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import AdminLayout from '@/layouts/AdminLayout.vue';
import StyleModal from "@/components/StyleModal.vue";
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

// ── State ──────────────────────────────────────────────────────────────────────
const activeTab          = ref('cours');
const transitioning      = ref(false);
const dataCours          = ref({ data: [], meta: { links: [] } });
const dataProgramme      = ref({ data: [], meta: { links: [] } });
const search_cours       = ref(props.filtersC?.search_cours || "");
const search_programme   = ref(props.filtersP?.search_programme || "");
const pages_cours        = ref(1);
const pages_prog         = ref(1);
const isModalHoraireOpen = ref(false);
const fetch_actual_class = ref([]);
const choseNiveau        = ref({});

const formHoraire = ref({
  niveau_id: "", faculte_id: "",
  annee_academique: "", class: "", session: "",
});

const TABS = [
  { id: 'cours',      label: 'Cours',       icon: '📖', count: () => dataCours.value.data?.length },
  { id: 'programmes', label: 'Programmes',  icon: '🗂️', count: () => dataProgramme.value.data?.length },
];

// ── API ────────────────────────────────────────────────────────────────────────
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
    choseNiveau.value       = res.data.niveau;
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

// ── Tab switch with transition ─────────────────────────────────────────────────
function switchTab(tabId) {
  if (tabId === activeTab.value || transitioning.value) return;
  transitioning.value = true;
  setTimeout(() => {
    activeTab.value = tabId;
    transitioning.value = false;
    if (tabId === 'programmes') searchProgramme();
  }, 180);
}

// ── Watchers ───────────────────────────────────────────────────────────────────
watch(search_cours,    () => { pages_cours.value = 1; searchCours(); });
watch(search_programme,() => { pages_prog.value  = 1; searchProgramme(); });
watch(pages_cours,    searchCours);
watch(pages_prog,     searchProgramme);

onMounted(searchCours);
</script>

<template>
  <div class="page-root">

    <!-- ── Page header ────────────────────────────────────────────────────── -->
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-header-icon">📚</div>
        <div>
          <h1 class="page-title">Gestion académique</h1>
          <p class="page-subtitle">Cours, programmes et horaires</p>
        </div>
      </div>

      <!-- CTA buttons -->
      <div class="page-actions">
        <router-link to="/admin/ajouter-cours" class="action-btn action-btn--ghost">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
            <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
          </svg>
          Ajouter un cours
        </router-link>
        <router-link to="/admin/ajouter-programme" class="action-btn action-btn--ghost">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
            <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
          </svg>
          Nouveau programme
        </router-link>
        <button class="action-btn action-btn--primary" @click="isModalHoraireOpen = true">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
            <path fill-rule="evenodd" d="M7.487 2.89a.75.75 0 1 0-1.474-.28l-.455 2.388H3.61a.75.75 0 0 0 0 1.5h1.663l-.571 2.998H2.75a.75.75 0 0 0 0 1.5h1.666l-.403 2.114a.75.75 0 0 0 1.474.28l.456-2.394h2.973l-.403 2.114a.75.75 0 0 0 1.474.28l.456-2.394h1.947a.75.75 0 0 0 0-1.5h-1.663l.57-2.998h1.953a.75.75 0 0 0 0-1.5h-1.666l.403-2.114a.75.75 0 0 0-1.474-.28l-.456 2.394H7.49l.402-2.114ZM9.586 7.996H6.61l-.57 2.998h2.976l.57-2.998Z" clip-rule="evenodd" />
          </svg>
          Imprimer horaire
        </button>
      </div>
    </div>

    <!-- ── Tab bar ─────────────────────────────────────────────────────────── -->
    <div class="tab-bar">
      <button
        v-for="tab in TABS" :key="tab.id"
        type="button"
        class="tab-btn"
        :class="{ 'tab-btn--active': activeTab === tab.id }"
        @click="switchTab(tab.id)"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        {{ tab.label }}
        <span class="tab-count" :class="{ 'tab-count--active': activeTab === tab.id }">
          {{ tab.count() ?? 0 }}
        </span>
      </button>
    </div>

    <!-- ── Tab content ─────────────────────────────────────────────────────── -->
    <Transition name="tab-slide" mode="out-in">

      <!-- ══ COURS ══ -->
      <div v-if="activeTab === 'cours'" key="cours" class="tab-content">

        <!-- Toolbar -->
        <div class="table-toolbar">
          <div class="search-wrap">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="search-icon">
              <path fill-rule="evenodd" d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" clip-rule="evenodd" />
            </svg>
            <input
              v-model="search_cours"
              type="text"
              placeholder="Rechercher un cours..."
              class="search-input"
            />
          </div>
          <span class="result-count">{{ dataCours.data?.length ?? 0 }} résultat(s)</span>
        </div>

        <!-- Table -->
        <div class="table-card">
          <table class="data-table">
            <thead>
              <tr>
                <th class="th">#</th>
                <th class="th">Nom du cours</th>
                <th class="th th--right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(cours, i) in dataCours.data" :key="cours.id"
                class="tr"
                :style="{ animationDelay: `${i * 30}ms` }"
              >
                <td class="td td--index">{{ i + 1 }}</td>
                <td class="td">
                  <div class="flex items-center gap-2.5">
                    <span class="row-dot"></span>
                    <span class="td-main">{{ cours.cours_nom }}</span>
                  </div>
                </td>
                <td class="td td--right">
                  <div class="row-actions">
                    <button class="row-btn row-btn--edit" title="Modifier">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
                        <path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.848 2.047a.75.75 0 0 0 .98.98l2.047-.848a2.75 2.75 0 0 0 .892-.596l4.261-4.262a1.75 1.75 0 0 0 0-2.474Z" />
                        <path d="M4.75 3.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V9A.75.75 0 0 1 14 9v2.25A2.75 2.75 0 0 1 11.25 14h-6.5A2.75 2.75 0 0 1 2 11.25v-6.5A2.75 2.75 0 0 1 4.75 2H7a.75.75 0 0 1 0 1.5H4.75Z" />
                      </svg>
                    </button>
                    <button class="row-btn row-btn--delete" title="Supprimer" @click="deleteCours(cours.id)">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
                        <path fill-rule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Zm2.25-.75a.75.75 0 0 0-.75.75V4h3v-.75a.75.75 0 0 0-.75-.75h-1.5ZM6.05 6a.75.75 0 0 1 .787.713l.275 5.5a.75.75 0 0 1-1.498.075l-.275-5.5A.75.75 0 0 1 6.05 6Zm3.9 0a.75.75 0 0 1 .712.787l-.275 5.5a.75.75 0 0 1-1.498-.075l.275-5.5A.75.75 0 0 1 9.95 6Z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>

              <!-- Empty state -->
              <tr v-if="!dataCours.data?.length">
                <td colspan="3" class="td-empty">
                  <span class="text-2xl mb-2 block">📭</span>
                  Aucun cours trouvé
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ══ PROGRAMMES ══ -->
      <div v-else-if="activeTab === 'programmes'" key="programmes" class="tab-content">

        <!-- Toolbar -->
        <div class="table-toolbar">
          <div class="search-wrap">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="search-icon">
              <path fill-rule="evenodd" d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" clip-rule="evenodd" />
            </svg>
            <input
              v-model="search_programme"
              type="text"
              placeholder="Filtrer les programmes..."
              class="search-input"
            />
          </div>
          <span class="result-count">{{ dataProgramme.data?.length ?? 0 }} résultat(s)</span>
        </div>

        <!-- Table -->
        <div class="table-card">
          <table class="data-table">
            <thead>
              <tr>
                <th class="th">Cours</th>
                <th class="th">Professeur</th>
                <th class="th">Niveau</th>
                <th class="th">Classe</th>
                <th class="th th--right">Année</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(prog, i) in dataProgramme.data" :key="prog.id"
                class="tr"
                :style="{ animationDelay: `${i * 30}ms` }"
              >
                <td class="td">
                  <div class="flex items-center gap-2">
                    <span class="row-dot row-dot--purple"></span>
                    <span class="td-main">{{ prog.cours }}</span>
                  </div>
                </td>
                <td class="td">
                  <span class="td-badge td-badge--blue">{{ prog.professeur }}</span>
                </td>
                <td class="td">
                  <span class="td-badge td-badge--slate">{{ prog.niveau_name }}</span>
                </td>
                <td class="td td-secondary">{{ prog.classe }}</td>
                <td class="td td--right">
                  <span class="font-mono text-[11px] text-[#5c6880] bg-[#0d1017] border border-[#1e2535] px-2 py-0.5 rounded">
                    {{ prog.annee_academique }}
                  </span>
                </td>
              </tr>

              <!-- Empty state -->
              <tr v-if="!dataProgramme.data?.length">
                <td colspan="5" class="td-empty">
                  <span class="text-2xl mb-2 block">📭</span>
                  Aucun programme trouvé
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </Transition>

    <!-- ── Horaire Modal ────────────────────────────────────────────────────── -->
    <StyleModal :show="isModalHoraireOpen" @close="isModalHoraireOpen = false" max-width="lg">

      <template #icon>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
          <path fill-rule="evenodd" d="M7.487 2.89a.75.75 0 1 0-1.474-.28l-.455 2.388H3.61a.75.75 0 0 0 0 1.5h1.663l-.571 2.998H2.75a.75.75 0 0 0 0 1.5h1.666l-.403 2.114a.75.75 0 0 0 1.474.28l.456-2.394h2.973l-.403 2.114a.75.75 0 0 0 1.474.28l.456-2.394h1.947a.75.75 0 0 0 0-1.5h-1.663l.57-2.998h1.953a.75.75 0 0 0 0-1.5h-1.666l.403-2.114a.75.75 0 0 0-1.474-.28l-.456 2.394H7.49l.402-2.114ZM9.586 7.996H6.61l-.57 2.998h2.976l.57-2.998Z" clip-rule="evenodd" />
        </svg>
      </template>
      <template #title>Imprimer l'horaire</template>
      <template #subtitle>Configurez les filtres puis générez le PDF.</template>

      <template #content>
        <form id="horaire-form" @submit.prevent="handlePrintHoraire" class="horaire-form">

          <div class="h-field">
            <label class="h-label" for="h-niveau">Niveau d'étude</label>
            <div class="h-select-wrap">
              <select id="h-niveau" class="h-select" v-model="formHoraire.niveau_id" @change="fetchNiveauDetails">
                <option value="" disabled>Sélectionner un niveau</option>
                <option v-for="n in niveau" :key="n.id" :value="n.id">{{ n.name }}</option>
              </select>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="h-select-arrow">
                <path fill-rule="evenodd" d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>

          <Transition name="accordion">
            <div v-if="choseNiveau.name === 'Universitaire'" class="h-field">
              <label class="h-label" for="h-faculte">Faculté / Option</label>
              <div class="h-select-wrap">
                <select id="h-faculte" class="h-select" v-model="formHoraire.faculte_id">
                  <option value="" disabled>Sélectionner</option>
                  <option v-for="f in faculte" :key="f.id" :value="f.id">{{ f.nom }}</option>
                </select>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="h-select-arrow">
                  <path fill-rule="evenodd" d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </Transition>

          <div class="h-grid">
            <div class="h-field">
              <label class="h-label" for="h-classe">Classe</label>
              <div class="h-select-wrap">
                <select id="h-classe" class="h-select" v-model="formHoraire.class">
                  <option value="" disabled>Sélectionner</option>
                  <option v-for="c in fetch_actual_class" :key="c.id" :value="c.id">{{ c.nom_classe }}</option>
                </select>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="h-select-arrow">
                  <path fill-rule="evenodd" d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>

            <div class="h-field">
              <label class="h-label" for="h-annee">Année académique</label>
              <div class="h-select-wrap">
                <select id="h-annee" class="h-select" v-model="formHoraire.annee_academique">
                  <option value="" disabled>Sélectionner</option>
                  <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
                </select>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="h-select-arrow">
                  <path fill-rule="evenodd" d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>

        </form>
      </template>

      <template #footer>
        <button type="button" class="hbtn hbtn--cancel" @click="isModalHoraireOpen = false">Annuler</button>
        <button type="submit" form="horaire-form" class="hbtn hbtn--print">
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
/* ── Page root ───────────────────────────────────────────────── */
.page-root {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.75rem 1.25rem 4rem;
  font-family: 'DM Sans', 'Segoe UI', sans-serif;
  color: #c9d1d9;
  min-height: 100vh;
  background: #0d1117;
}

/* ── Header ──────────────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.75rem;
}
.page-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.page-header-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(74,124,255,.15), rgba(74,124,255,.05));
  border: 1px solid rgba(74,124,255,.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.page-title {
  font-size: 17px;
  font-weight: 600;
  color: #e2e8f5;
  letter-spacing: -0.01em;
  margin: 0;
}
.page-subtitle {
  font-size: 12px;
  color: #3d4d62;
  margin: 2px 0 0;
}

/* ── Action buttons ──────────────────────────────────────────── */
.page-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s;
  text-decoration: none;
  font-family: inherit;
  white-space: nowrap;
}
.action-btn--ghost {
  background: rgba(255,255,255,.04);
  color: #6b7a90;
  border-color: rgba(255,255,255,.07);
}
.action-btn--ghost:hover {
  background: rgba(255,255,255,.07);
  color: #9aa5bb;
  border-color: rgba(255,255,255,.11);
}
.action-btn--primary {
  background: linear-gradient(135deg, #2d5dd4, #4a7cff);
  color: #fff;
  border-color: rgba(255,255,255,.1);
  box-shadow: 0 2px 10px rgba(45,93,212,.3);
}
.action-btn--primary:hover {
  background: linear-gradient(135deg, #3568e8, #5a8cff);
  box-shadow: 0 4px 16px rgba(45,93,212,.4);
  transform: translateY(-1px);
}

/* ── Tab bar ─────────────────────────────────────────────────── */
.tab-bar {
  display: flex;
  gap: 2px;
  background: #161b22;
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 12px;
  padding: 4px;
  width: fit-content;
  margin-bottom: 1.5rem;
}
.tab-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 20px;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 500;
  color: #4a5568;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.18s;
  font-family: inherit;
}
.tab-btn:hover { color: #8a95a8; background: rgba(255,255,255,.03); }
.tab-btn--active {
  background: #21262d;
  color: #e2e8f5;
  box-shadow: 0 1px 4px rgba(0,0,0,.4);
}
.tab-icon { font-size: 14px; }
.tab-count {
  font-size: 10px;
  font-weight: 600;
  background: rgba(255,255,255,.06);
  color: #3d4d62;
  border-radius: 20px;
  padding: 1px 6px;
  font-family: monospace;
  transition: all 0.18s;
}
.tab-count--active {
  background: rgba(74,124,255,.15);
  color: #7aaeff;
}

/* ── Tab content ─────────────────────────────────────────────── */
.tab-content { animation: fadeUp .22s ease both; }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Toolbar ─────────────────────────────────────────────────── */
.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.875rem;
}
.search-wrap {
  position: relative;
  flex: 1;
  max-width: 360px;
}
.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  color: #3d4d62;
  pointer-events: none;
}
.search-input {
  width: 100%;
  background: #161b22;
  border: 1px solid rgba(255,255,255,.07);
  border-radius: 8px;
  padding: 7px 11px 7px 32px;
  color: #c9d1d9;
  font-size: 13px;
  outline: none;
  transition: border-color .15s, box-shadow .15s;
  font-family: inherit;
}
.search-input::placeholder { color: #2e3a4a; }
.search-input:focus {
  border-color: rgba(74,124,255,.4);
  box-shadow: 0 0 0 3px rgba(74,124,255,.08);
}
.result-count {
  font-size: 11px;
  color: #3d4d62;
  white-space: nowrap;
}

/* ── Table card ──────────────────────────────────────────────── */
.table-card {
  background: #161b22;
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 12px;
  overflow: hidden;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
}
.th {
  padding: 10px 16px;
  text-align: left;
  font-size: 10.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #3d4d62;
  border-bottom: 1px solid rgba(255,255,255,.05);
  background: #0d1017;
}
.th--right { text-align: right; }

.tr {
  border-bottom: 1px solid rgba(255,255,255,.04);
  transition: background 0.12s;
  animation: rowIn 0.2s ease both;
}
.tr:last-child { border-bottom: none; }
.tr:hover { background: rgba(255,255,255,.02); }
@keyframes rowIn {
  from { opacity: 0; transform: translateX(-6px); }
  to   { opacity: 1; transform: translateX(0); }
}

.td {
  padding: 10px 16px;
  font-size: 13px;
  color: #8a95a8;
  vertical-align: middle;
}
.td--right { text-align: right; }
.td--index {
  font-size: 11px;
  color: #2e3a4a;
  font-family: monospace;
  width: 40px;
}
.td-main { color: #c9d1d9; font-weight: 500; font-size: 13px; }
.td-secondary { color: #5c6880; font-size: 12px; }

.td-empty {
  padding: 3rem 1rem;
  text-align: center;
  color: #3d4d62;
  font-size: 13px;
}

/* Row decorative dot */
.row-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(74,124,255,.4);
  flex-shrink: 0;
}
.row-dot--purple { background: rgba(167,139,250,.4); }

/* Badges */
.td-badge {
  display: inline-flex;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 20px;
  font-weight: 500;
}
.td-badge--blue {
  background: rgba(74,124,255,.1);
  color: #7aaeff;
  border: 1px solid rgba(74,124,255,.15);
}
.td-badge--slate {
  background: rgba(255,255,255,.05);
  color: #6b7a90;
  border: 1px solid rgba(255,255,255,.08);
}

/* Row action buttons */
.row-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
}
.row-btn {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s;
  background: transparent;
  color: #3d4d62;
}
.row-btn--edit:hover {
  background: rgba(74,124,255,.1);
  border-color: rgba(74,124,255,.2);
  color: #7aaeff;
}
.row-btn--delete:hover {
  background: rgba(220,80,80,.1);
  border-color: rgba(220,80,80,.2);
  color: #e57373;
}

/* ── Tab slide transition ────────────────────────────────────── */
.tab-slide-enter-active, .tab-slide-leave-active {
  transition: opacity .18s ease, transform .18s ease;
}
.tab-slide-enter-from { opacity: 0; transform: translateY(7px); }
.tab-slide-leave-to   { opacity: 0; transform: translateY(-5px); }

/* ── Accordion (faculté reveal) ──────────────────────────────── */
.accordion-enter-active, .accordion-leave-active {
  transition: all .22s ease; overflow: hidden;
}
.accordion-enter-from, .accordion-leave-to {
  opacity: 0; max-height: 0;
}
.accordion-enter-to, .accordion-leave-from {
  opacity: 1; max-height: 120px;
}

/* ── Horaire modal form ──────────────────────────────────────── */
.horaire-form { display: flex; flex-direction: column; gap: 1rem; }
.h-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.h-field { display: flex; flex-direction: column; gap: 5px; }
.h-label {
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #3d4d62;
}
.h-select-wrap { position: relative; }
.h-select {
  width: 100%;
  background: #0d1017;
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 8px;
  padding: 8px 32px 8px 11px;
  color: #c9d1d9;
  font-size: 13px;
  outline: none;
  appearance: none;
  cursor: pointer;
  transition: border-color .15s, box-shadow .15s;
  font-family: inherit;
}
.h-select:focus {
  border-color: rgba(74,124,255,.4);
  box-shadow: 0 0 0 3px rgba(74,124,255,.08);
}
.h-select option { background: #13171f; color: #c9d1d9; }
.h-select-arrow {
  position: absolute;
  right: 9px;
  top: 50%;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  color: #2e3a4a;
  pointer-events: none;
}

/* ── Horaire footer buttons ──────────────────────────────────── */
.hbtn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all .15s;
  font-family: inherit;
}
.hbtn--cancel {
  background: rgba(255,255,255,.04);
  color: #5c6880;
  border-color: rgba(255,255,255,.07);
}
.hbtn--cancel:hover {
  background: rgba(255,255,255,.07);
  color: #8a95a8;
}
.hbtn--print {
  background: linear-gradient(135deg, #2d5dd4, #4a7cff);
  color: #fff;
  border-color: rgba(255,255,255,.1);
  box-shadow: 0 2px 10px rgba(45,93,212,.3);
}
.hbtn--print:hover {
  background: linear-gradient(135deg, #3568e8, #5a8cff);
  box-shadow: 0 4px 14px rgba(45,93,212,.4);
  transform: translateY(-1px);
}

@media (max-width: 600px) {
  .page-header { flex-direction: column; align-items: flex-start; }
  .h-grid { grid-template-columns: 1fr; }
  .tab-btn { padding: 8px 12px; font-size: 12px; }
}
</style>
