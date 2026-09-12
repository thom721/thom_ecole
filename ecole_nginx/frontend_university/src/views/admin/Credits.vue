<script setup>
import { ref, computed, onMounted, watch } from "vue";
import axios from "axios";
import Swal from 'sweetalert2';
import AdminLayout from '@/layouts/AdminLayout.vue';
import StyleModal from '@/components/StyleModal.vue';
import { useSchoolStore } from '@/stores/schoolStore';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';

defineOptions({ layout: AdminLayout });

const url = import.meta.env.VITE_APP_BASE_URL;

const schoolStore = useSchoolStore();
const { niveau, annee } = storeToRefs(schoolStore);
const authStore = useAuthStore();

const canModifierCours       = computed(() => authStore.hasPermission('Modifier cours'));
const canAjouterInscription  = computed(() => authStore.hasPermission('Ajouter inscription cours'));
const canVoirInscription     = computed(() => authStore.hasPermission('Voir inscription cours'));
const canSaisirNote          = computed(() =>
  authStore.hasRole(['admin', 'Responsable pédagogique', 'teacher']) && authStore.hasPermission('Ajouter note')
);
const canOverridePrerequis   = computed(() => authStore.hasRole(['admin', 'Responsable pédagogique']));

// ── Niveau Universitaire (gate) ─────────────────────────────────────────
const universitaireNiveau = computed(() => niveau.value?.find(n => n.name === 'Universitaire'));
const universitaireActif  = computed(() => universitaireNiveau.value?.status === true);
const anneeActive         = computed(() => annee.value?.find(a => a.status === true));

// ── Cours (scopés au niveau Universitaire) ──────────────────────────────
const coursAll = ref([]);
const coursUniversitaire = computed(() =>
  coursAll.value.filter(c => c.niveau_id === universitaireNiveau.value?.id)
);
const coursNom = (id) => coursAll.value.find(c => c.id === id)?.cours_nom || id;

const fetchCoursAll = async () => {
  try {
    const res = await axios.get(`${url}/cours`);
    coursAll.value = Array.isArray(res.data) ? res.data : (res.data?.data ?? []);
  } catch (e) {
    console.error('Erreur chargement des cours:', e);
  }
};

// ── Onglets ──────────────────────────────────────────────────────────────
const TABS = [
  { id: 'prerequis',   label: 'Prérequis',   icon: '🔗' },
  { id: 'inscription', label: 'Inscription', icon: '📝' },
  { id: 'notes',       label: 'Notes',       icon: '🧮' },
  { id: 'progres',     label: 'Progrès',     icon: '📊' },
];
const activeTab = ref('prerequis');

// ── Recherche étudiant (partagée entre Inscription/Notes/Progrès) ──────
const searchStudentVal = ref('');
const studentResults = ref([]);
const selectedStudent = ref(null);

const fetchStudent = async () => {
  if (searchStudentVal.value.length < 2) {
    studentResults.value = [];
    return;
  }
  try {
    const res = await axios.post(`${url}/live-student`, { val: searchStudentVal.value, niveau: universitaireNiveau.value?.id });
    studentResults.value = res.data.data;
  } catch (e) {
    console.error('Erreur recherche étudiant:', e);
  }
};

const selectStudent = (student) => {
  selectedStudent.value = student;
  searchStudentVal.value = '';
  studentResults.value = [];
};

const clearStudent = () => {
  selectedStudent.value = null;
  inscriptionsList.value = [];
  progresData.value = null;
};

// ══════════════════════════════════════════════════════════════════════
// Onglet Prérequis
// ══════════════════════════════════════════════════════════════════════
const selectedCoursId = ref('');
const prerequisList = ref([]);
const addPrerequisCoursId = ref('');

const coursDisponiblesPourAjout = computed(() =>
  coursUniversitaire.value.filter(c =>
    c.id !== selectedCoursId.value &&
    !prerequisList.value.some(p => p.prerequis_cours_id === c.id)
  )
);

const fetchPrerequis = async () => {
  if (!selectedCoursId.value) { prerequisList.value = []; return; }
  try {
    const res = await axios.get(`${url}/cours/${selectedCoursId.value}/prerequis`);
    prerequisList.value = res.data;
  } catch (e) {
    prerequisList.value = [];
    Swal.fire('Erreur', e.response?.data?.detail || 'Impossible de charger les prérequis.', 'error');
  }
};
watch(selectedCoursId, fetchPrerequis);

const addPrerequis = async () => {
  if (!addPrerequisCoursId.value) return;
  try {
    const res = await axios.post(`${url}/cours/${selectedCoursId.value}/prerequis`, {
      prerequis_cours_id: addPrerequisCoursId.value,
    });
    prerequisList.value.push(res.data);
    addPrerequisCoursId.value = '';
    Swal.fire({ icon: 'success', text: 'Prérequis ajouté', timer: 1500, showConfirmButton: false, background: '#13171f', color: '#e8eaf0' });
  } catch (e) {
    Swal.fire('Erreur', e.response?.data?.detail || 'Impossible d\'ajouter ce prérequis.', 'error');
  }
};

const deletePrerequis = (prerequis) => {
  Swal.fire({
    title: 'Retirer ce prérequis ?',
    icon: 'warning',
    background: '#13171f', color: '#c9d1d9',
    showCancelButton: true,
    confirmButtonColor: '#c0392b', cancelButtonColor: '#2d3748',
    confirmButtonText: 'Retirer', cancelButtonText: 'Annuler',
  }).then(async (result) => {
    if (!result.isConfirmed) return;
    try {
      await axios.delete(`${url}/cours/${selectedCoursId.value}/prerequis/${prerequis.prerequis_cours_id}`);
      prerequisList.value = prerequisList.value.filter(p => p.id !== prerequis.id);
    } catch (e) {
      Swal.fire('Erreur', e.response?.data?.detail || 'Impossible de retirer ce prérequis.', 'error');
    }
  });
};

// ══════════════════════════════════════════════════════════════════════
// Onglet Inscription
// ══════════════════════════════════════════════════════════════════════
const inscriptionForm = ref({ cours_id: '', annee_academique_id: '', override_prerequisite: false, override_max_tentatives: false });
const prerequisErrors = ref([]);
const inscriptionLoading = ref(false);

watch(anneeActive, (a) => {
  if (a && !inscriptionForm.value.annee_academique_id) inscriptionForm.value.annee_academique_id = a.id;
}, { immediate: true });

watch([() => inscriptionForm.value.cours_id, selectedStudent], () => { prerequisErrors.value = []; });

const submitInscription = async () => {
  if (!selectedStudent.value || !inscriptionForm.value.cours_id || !inscriptionForm.value.annee_academique_id) return;
  prerequisErrors.value = [];
  inscriptionLoading.value = true;
  try {
    await axios.post(`${url}/credits/inscriptions`, {
      etudiant_id: selectedStudent.value.id,
      cours_id: inscriptionForm.value.cours_id,
      annee_academique_id: inscriptionForm.value.annee_academique_id,
      programme_id: null,
      override_prerequisite: inscriptionForm.value.override_prerequisite,
      override_max_tentatives: inscriptionForm.value.override_max_tentatives,
    });
    Swal.fire({ icon: 'success', text: 'Étudiant inscrit avec succès', timer: 1800, showConfirmButton: false, background: '#13171f', color: '#e8eaf0' });
    inscriptionForm.value.cours_id = '';
    inscriptionForm.value.override_prerequisite = false;
    inscriptionForm.value.override_max_tentatives = false;
  } catch (e) {
    const detail = e.response?.data?.detail;
    if (e.response?.status === 422 && detail && typeof detail === 'object' && detail.errors?.prerequis) {
      prerequisErrors.value = detail.errors.prerequis;
    } else if (typeof detail === 'string') {
      Swal.fire('Erreur', detail, 'error');
    } else {
      Swal.fire('Erreur', "Une erreur est survenue lors de l'inscription.", 'error');
    }
  } finally {
    inscriptionLoading.value = false;
  }
};

// ══════════════════════════════════════════════════════════════════════
// Onglet Notes
// ══════════════════════════════════════════════════════════════════════
const inscriptionsList = ref([]);
const inscriptionsLoading = ref(false);
const noteModalOpen = ref(false);
const noteModalInscription = ref(null);
// Intra et Final sont deux notes distinctes (voir plan Épic 24, même
// principe que NoteForm.vue côté système bloc) — la modal cible l'une ou
// l'autre selon le bouton cliqué, jamais une saisie unique.
const noteModalPhase = ref('intra');
const noteValue = ref('');

const fetchInscriptions = async () => {
  if (!selectedStudent.value) { inscriptionsList.value = []; return; }
  inscriptionsLoading.value = true;
  try {
    const res = await axios.get(`${url}/credits/inscriptions`, {
      params: { etudiant_id: selectedStudent.value.id },
    });
    inscriptionsList.value = res.data;
  } catch (e) {
    inscriptionsList.value = [];
    Swal.fire('Erreur', e.response?.data?.detail || 'Impossible de charger les inscriptions.', 'error');
  } finally {
    inscriptionsLoading.value = false;
  }
};

const openNoteModal = (inscription, phase) => {
  noteModalInscription.value = inscription;
  noteModalPhase.value = phase;
  noteValue.value = '';
  noteModalOpen.value = true;
};
const closeNoteModal = () => { noteModalOpen.value = false; noteModalInscription.value = null; };

const noteValueValide = computed(() => noteValue.value !== '' && !isNaN(Number(noteValue.value)) && isFinite(Number(noteValue.value)));

// Contribution devoirs de la phase ciblée par la modal — pas de mise à
// l'échelle nécessaire ici (contrairement au système bloc, où
// Coeff.≠100) : les notes crédits sont déjà sur 100, comme note_de_passage.
const noteModalDevoirs = computed(() => {
  if (!noteModalInscription.value) return null;
  return noteModalPhase.value === 'intra'
    ? noteModalInscription.value.note_devoirs_intra
    : noteModalInscription.value.note_devoirs_finale;
});

// Total envoyé = note manuelle + contribution des devoirs de la phase
// ciblée — "prêt à être additionné", pas juste affiché.
const noteTotal = computed(() => {
  const manuel = noteValueValide.value ? Number(noteValue.value) : 0;
  const devoirs = Number(noteModalDevoirs.value);
  return manuel + (isNaN(devoirs) ? 0 : devoirs);
});

const submitNote = async () => {
  if (!noteModalInscription.value || !noteValueValide.value) return;
  try {
    const res = await axios.put(`${url}/credits/inscriptions/${noteModalInscription.value.id}/note`, {
      phase: noteModalPhase.value,
      note: noteTotal.value,
    });
    const idx = inscriptionsList.value.findIndex(i => i.id === res.data.id);
    if (idx !== -1) inscriptionsList.value[idx] = res.data;
    closeNoteModal();
    Swal.fire({ icon: 'success', text: 'Note enregistrée', timer: 1500, showConfirmButton: false, background: '#13171f', color: '#e8eaf0' });
  } catch (e) {
    Swal.fire('Erreur', e.response?.data?.detail || 'Impossible d\'enregistrer cette note.', 'error');
  }
};

const statutStyle = (statut) => ({
  'en_cours': 'bg-white/[0.06] text-[#8a95a8] border-white/[0.08]',
  'valide':   'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  'echoue':   'bg-red-500/10 text-red-400 border-red-500/20',
  'abandonne': 'bg-white/[0.04] text-[#4a5568] border-white/[0.06]',
}[statut] || 'bg-white/[0.06] text-[#8a95a8] border-white/[0.08]');

// ══════════════════════════════════════════════════════════════════════
// Onglet Progrès
// ══════════════════════════════════════════════════════════════════════
const progresData = ref(null);
const progresLoading = ref(false);

const fetchProgres = async () => {
  if (!selectedStudent.value) { progresData.value = null; return; }
  progresLoading.value = true;
  try {
    const res = await axios.get(`${url}/credits/etudiants/${selectedStudent.value.id}/progres`);
    progresData.value = res.data;
  } catch (e) {
    progresData.value = null;
    Swal.fire('Erreur', e.response?.data?.detail || 'Impossible de charger la progression.', 'error');
  } finally {
    progresLoading.value = false;
  }
};

watch([selectedStudent, activeTab], () => {
  if (activeTab.value === 'notes') fetchInscriptions();
  if (activeTab.value === 'progres') fetchProgres();
});

onMounted(async () => {
  await schoolStore.fetchAllDependencies();
  await fetchCoursAll();
});
</script>

<template>
  <div
    class="min-h-screen bg-[#0d1117] text-[#c9d1d9] px-4 sm:px-6 pb-7 max-w-6xl mx-auto animate-[fadeUp_0.4s_ease_both]"
    style="font-family:'DM Sans','Segoe UI',sans-serif"
  >
    <!-- ── Header ──────────────────────────────────────────────── -->
    <div class="flex flex-wrap items-center justify-between gap-4 mb-7 pt-6">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-[#1f6feb]/10 border border-[#1f6feb]/20 flex items-center justify-center text-lg shrink-0">
          🎓
        </div>
        <div>
          <h1 class="text-[17px] font-semibold text-[#e2e8f5] tracking-tight leading-tight m-0">
            Système à crédits
          </h1>
          <p class="text-[12px] text-[#3d4d62] mt-0.5 m-0">Prérequis, inscriptions, notes et progrès — niveau Universitaire</p>
        </div>
      </div>
    </div>

    <!-- ── Bandeau niveau inactif (informatif, non bloquant) ────── -->
    <div
      v-if="!universitaireActif"
      class="mb-5 px-4 py-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[13px]"
    >
      Le niveau Universitaire n'est pas actif — les actions d'écriture échoueront tant qu'il n'est pas réactivé dans Paramètres.
    </div>

    <!-- ── Tab bar ─────────────────────────────────────────────── -->
    <div class="flex gap-0.5 bg-[#161b22] border border-white/[0.06] rounded-xl p-1 w-fit mb-5">
      <button
        v-for="tab in TABS" :key="tab.id"
        type="button"
        @click="activeTab = tab.id"
        :class="[
          'flex items-center gap-2 px-5 py-2 rounded-[9px] text-[13px] font-medium transition-all duration-200',
          activeTab === tab.id
            ? 'bg-[#21262d] text-[#e2e8f5] shadow-[0_1px_4px_rgba(0,0,0,.4)]'
            : 'text-[#4a5568] hover:text-[#8a95a8] hover:bg-white/[0.03]'
        ]"
      >
        <span class="text-sm">{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </div>

    <!-- ── Recherche étudiant (partagée : Inscription / Notes / Progrès) ── -->
    <div v-if="['inscription', 'notes', 'progres'].includes(activeTab)" class="mb-5">
      <div v-if="!selectedStudent" class="relative max-w-sm">
        <input
          v-model="searchStudentVal" type="text"
          placeholder="Rechercher un étudiant (nom, identifiant...)"
          @keyup="fetchStudent"
          class="w-full bg-[#161b22] border border-white/[0.07] rounded-lg
                 px-3 py-[7px] text-[13px] text-[#c9d1d9] placeholder-[#2e3a4a]
                 outline-none focus:border-[#4a7cff]/40 focus:ring-2 focus:ring-[#4a7cff]/[0.08]
                 transition-all duration-150"
        />
        <div v-if="studentResults.length" class="mt-1 bg-[#171b26] border border-white/[0.07] rounded-lg overflow-hidden divide-y divide-white/[0.05]">
          <div
            v-for="s in studentResults" :key="s.id"
            @click="selectStudent(s)"
            class="grid grid-cols-3 gap-2 px-3 py-2 hover:bg-white/[0.04] cursor-pointer transition text-[13px]"
          >
            <span class="font-mono text-[11px] text-[#3d4d62]">{{ s.identifiant }}</span>
            <span class="uppercase text-[#c9d1d9]">{{ s.nom }}</span>
            <span class="capitalize text-[#c9d1d9]">{{ s.prenom }}</span>
          </div>
        </div>
        <div v-else-if="searchStudentVal.length > 1" class="mt-1 text-[12px] text-[#3d4d62]">Aucun étudiant trouvé...</div>
      </div>
      <div v-else class="inline-flex items-center gap-2 bg-[#161b22] border border-white/[0.07] rounded-lg px-3 py-1.5">
        <span class="text-[13px] text-[#c9d1d9]">
          <span class="font-mono text-[11px] text-[#3d4d62]">{{ selectedStudent.identifiant }}</span>
          — {{ selectedStudent.nom }} {{ selectedStudent.prenom }}
        </span>
        <button @click="clearStudent" class="text-[#4a5568] hover:text-[#e57373] transition text-[15px] leading-none">×</button>
      </div>
    </div>

    <!-- ── Contenu des onglets ─────────────────────────────────── -->
    <Transition name="tab-slide" mode="out-in">

      <!-- ══ PRÉREQUIS ══ -->
      <div v-if="activeTab === 'prerequis'" key="prerequis">
        <div class="flex items-center gap-3 mb-4">
          <select
            v-model="selectedCoursId"
            class="bg-[#161b22] border border-white/[0.08] rounded-lg px-3 py-[7px] text-[13px] text-[#c9d1d9]
                   outline-none focus:border-[#4a7cff]/40 focus:ring-2 focus:ring-[#4a7cff]/[0.08] min-w-[240px]"
          >
            <option value="" disabled>Choisir un cours (Universitaire)</option>
            <option v-for="c in coursUniversitaire" :key="c.id" :value="c.id">{{ c.cours_nom }}</option>
          </select>
        </div>

        <div v-if="selectedCoursId" class="bg-[#161b22] border border-white/[0.06] rounded-xl overflow-hidden">
          <table class="w-full border-collapse">
            <thead>
              <tr class="bg-[#0d1117] border-b border-white/[0.05]">
                <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Prérequis</th>
                <th v-if="canModifierCours" class="px-4 py-2.5 text-right text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!prerequisList.length">
                <td :colspan="canModifierCours ? 2 : 1" class="py-8 text-center text-[13px] text-[#3d4d62]">Aucun prérequis défini.</td>
              </tr>
              <tr v-for="p in prerequisList" :key="p.id" class="border-b border-white/[0.04] last:border-0 hover:bg-white/[0.02] transition-colors">
                <td class="px-4 py-2.5 text-[13px] text-[#c9d1d9]">{{ p.prerequis_cours_nom || p.prerequis_cours_id }}</td>
                <td v-if="canModifierCours" class="px-4 py-2.5 text-right">
                  <button
                    @click="deletePrerequis(p)"
                    class="w-7 h-7 rounded-lg inline-flex items-center justify-center text-[#3d4d62] hover:text-[#e57373] hover:bg-red-500/10 transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
                      <path fill-rule="evenodd" d="M5 3.25V4H2.75a.75.75 0 000 1.5h.3l.815 8.15A1.5 1.5 0 005.357 15h5.285a1.5 1.5 0 001.493-1.35l.815-8.15h.3a.75.75 0 000-1.5H11v-.75A2.25 2.25 0 008.75 1h-1.5A2.25 2.25 0 005 3.25zm2.25-.75a.75.75 0 00-.75.75V4h3v-.75a.75.75 0 00-.75-.75h-1.5zM6.05 6a.75.75 0 01.787.713l.275 5.5a.75.75 0 11-1.498.075l-.275-5.5A.75.75 0 016.05 6zm3.9 0a.75.75 0 01.712.787l-.275 5.5a.75.75 0 11-1.498-.075l.275-5.5a.75.75 0 01.786-.712z" clip-rule="evenodd"/>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="canModifierCours" class="flex items-center gap-2 px-4 py-3 border-t border-white/[0.05]">
            <select
              v-model="addPrerequisCoursId"
              class="flex-1 bg-[#0d1017] border border-white/[0.08] rounded-lg px-3 py-[6px] text-[13px] text-[#c9d1d9]
                     outline-none focus:border-[#4a7cff]/40 focus:ring-2 focus:ring-[#4a7cff]/[0.08]"
            >
              <option value="" disabled>Ajouter un prérequis...</option>
              <option v-for="c in coursDisponiblesPourAjout" :key="c.id" :value="c.id">{{ c.cours_nom }}</option>
            </select>
            <button
              @click="addPrerequis"
              :disabled="!addPrerequisCoursId"
              class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-[12.5px] font-medium text-white
                     bg-gradient-to-r from-[#2d5dd4] to-[#4a7cff] border border-white/10
                     disabled:opacity-40 disabled:cursor-not-allowed
                     hover:from-[#3568e8] hover:to-[#5a8cff] transition-all duration-150"
            >
              Ajouter
            </button>
          </div>
        </div>
      </div>

      <!-- ══ INSCRIPTION ══ -->
      <div v-else-if="activeTab === 'inscription'" key="inscription">
        <div v-if="!selectedStudent" class="text-[13px] text-[#3d4d62] py-8 text-center">Recherchez un étudiant pour l'inscrire à un cours.</div>
        <div v-else-if="!canAjouterInscription" class="text-[13px] text-[#3d4d62] py-8 text-center">Vous n'avez pas la permission d'inscrire un étudiant.</div>
        <div v-else class="bg-[#161b22] border border-white/[0.06] rounded-xl p-5 max-w-lg space-y-4">
          <div>
            <label class="block text-[11px] uppercase tracking-wide text-[#6b7a90] mb-1.5">Cours (Universitaire)</label>
            <select
              v-model="inscriptionForm.cours_id"
              class="w-full bg-[#0d1017] border border-white/[0.08] rounded-lg px-3 py-[7px] text-[13px] text-[#c9d1d9]
                     outline-none focus:border-[#4a7cff]/40 focus:ring-2 focus:ring-[#4a7cff]/[0.08]"
            >
              <option value="" disabled>Choisir un cours</option>
              <option v-for="c in coursUniversitaire" :key="c.id" :value="c.id">{{ c.cours_nom }}</option>
            </select>
          </div>
          <div>
            <label class="block text-[11px] uppercase tracking-wide text-[#6b7a90] mb-1.5">Année académique</label>
            <select
              v-model="inscriptionForm.annee_academique_id"
              class="w-full bg-[#0d1017] border border-white/[0.08] rounded-lg px-3 py-[7px] text-[13px] text-[#c9d1d9]
                     outline-none focus:border-[#4a7cff]/40 focus:ring-2 focus:ring-[#4a7cff]/[0.08]"
            >
              <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
            </select>
          </div>

          <div v-if="prerequisErrors.length" class="px-3 py-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[12.5px] space-y-1">
            <p v-for="(msg, i) in prerequisErrors" :key="i" class="m-0">{{ msg }}</p>
          </div>

          <label v-if="canOverridePrerequis" class="flex items-center gap-2 text-[12.5px] text-[#8a95a8] cursor-pointer">
            <input type="checkbox" v-model="inscriptionForm.override_prerequisite" class="accent-[#4a7cff]" />
            Ignorer les prérequis
          </label>
          <label v-if="canOverridePrerequis" class="flex items-center gap-2 text-[12.5px] text-[#8a95a8] cursor-pointer">
            <input type="checkbox" v-model="inscriptionForm.override_max_tentatives" class="accent-[#4a7cff]" />
            Ignorer la limite de reprises
          </label>

          <button
            @click="submitInscription"
            :disabled="!inscriptionForm.cours_id || !inscriptionForm.annee_academique_id || inscriptionLoading"
            class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-[13px] font-medium text-white
                   bg-gradient-to-r from-[#2d5dd4] to-[#4a7cff] border border-white/10
                   disabled:opacity-40 disabled:cursor-not-allowed
                   hover:from-[#3568e8] hover:to-[#5a8cff] transition-all duration-150"
          >
            Inscrire
          </button>
        </div>
      </div>

      <!-- ══ NOTES ══ -->
      <div v-else-if="activeTab === 'notes'" key="notes">
        <div v-if="!selectedStudent" class="text-[13px] text-[#3d4d62] py-8 text-center">Recherchez un étudiant pour saisir ses notes.</div>
        <div v-else class="bg-[#161b22] border border-white/[0.06] rounded-xl overflow-hidden">
          <table class="w-full border-collapse">
            <thead>
              <tr class="bg-[#0d1117] border-b border-white/[0.05]">
                <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Cours</th>
                <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Crédits</th>
                <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Intra</th>
                <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Final</th>
                <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Statut</th>
                <th class="px-4 py-2.5 text-right text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!inscriptionsLoading && !inscriptionsList.length">
                <td colspan="6" class="py-8 text-center text-[13px] text-[#3d4d62]">Aucune inscription pour cet étudiant.</td>
              </tr>
              <tr v-for="i in inscriptionsList" :key="i.id" class="border-b border-white/[0.04] last:border-0 hover:bg-white/[0.02] transition-colors">
                <td class="px-4 py-2.5 text-[13px] text-[#c9d1d9]">{{ coursNom(i.cours_id) }}</td>
                <td class="px-4 py-2.5 text-[13px] text-[#8a95a8]">{{ i.credits }}</td>
                <td class="px-4 py-2.5 text-[13px] text-[#8a95a8]">
                  {{ i.note_intra ?? '—' }}
                  <span v-if="i.note_devoirs_intra != null" class="text-[10.5px] text-[#4a7cff]">({{ i.note_devoirs_intra }}%)</span>
                </td>
                <td class="px-4 py-2.5 text-[13px] text-[#8a95a8]">
                  {{ i.note_finale ?? '—' }}
                  <span v-if="i.note_devoirs_finale != null" class="text-[10.5px] text-[#4a7cff]">({{ i.note_devoirs_finale }}%)</span>
                </td>
                <td class="px-4 py-2.5">
                  <span class="text-[11px] px-2 py-1 rounded-md border" :class="statutStyle(i.statut)">{{ i.statut }}</span>
                </td>
                <td class="px-4 py-2.5 text-right">
                  <div v-if="canSaisirNote" class="inline-flex gap-1.5">
                    <button
                      @click="openNoteModal(i, 'intra')"
                      class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[12px] font-medium text-[#7aaeff]
                             bg-[#4a7cff]/10 border border-[#4a7cff]/20 hover:bg-[#4a7cff]/15 transition-colors"
                    >
                      Intra
                    </button>
                    <button
                      @click="openNoteModal(i, 'finale')"
                      :disabled="i.note_intra == null"
                      :title="i.note_intra == null ? 'La note Intra doit être saisie d\'abord' : ''"
                      class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[12px] font-medium text-[#7aaeff]
                             bg-[#4a7cff]/10 border border-[#4a7cff]/20 hover:bg-[#4a7cff]/15 transition-colors
                             disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-[#4a7cff]/10"
                    >
                      Final
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ══ PROGRÈS ══ -->
      <div v-else-if="activeTab === 'progres'" key="progres">
        <div v-if="!canVoirInscription" class="text-[13px] text-[#3d4d62] py-8 text-center">Vous n'avez pas la permission de consulter la progression des étudiants.</div>
        <div v-else-if="!selectedStudent" class="text-[13px] text-[#3d4d62] py-8 text-center">Recherchez un étudiant pour voir sa progression.</div>
        <div v-else>
          <div v-if="progresData" class="grid grid-cols-3 gap-3 mb-5">
            <div class="bg-[#161b22] border border-white/[0.06] rounded-xl p-4">
              <p class="text-[10.5px] uppercase tracking-wide text-[#3d4d62] mb-1">GPA</p>
              <p class="text-[22px] font-semibold text-[#e2e8f5]">{{ progresData.gpa }}</p>
            </div>
            <div class="bg-[#161b22] border border-white/[0.06] rounded-xl p-4">
              <p class="text-[10.5px] uppercase tracking-wide text-[#3d4d62] mb-1">Crédits tentés</p>
              <p class="text-[22px] font-semibold text-[#e2e8f5]">{{ progresData.credits_tentes }}</p>
            </div>
            <div class="bg-[#161b22] border border-white/[0.06] rounded-xl p-4">
              <p class="text-[10.5px] uppercase tracking-wide text-[#3d4d62] mb-1">Crédits validés</p>
              <p class="text-[22px] font-semibold text-[#e2e8f5]">{{ progresData.credits_valides }}</p>
            </div>
          </div>

          <div class="bg-[#161b22] border border-white/[0.06] rounded-xl overflow-hidden">
            <table class="w-full border-collapse">
              <thead>
                <tr class="bg-[#0d1117] border-b border-white/[0.05]">
                  <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Cours</th>
                  <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Crédits</th>
                  <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Note</th>
                  <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Crédits obtenus</th>
                  <th class="px-4 py-2.5 text-left text-[10.5px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Statut</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="progresData && !progresData.inscriptions.length">
                  <td colspan="5" class="py-8 text-center text-[13px] text-[#3d4d62]">Aucune inscription.</td>
                </tr>
                <tr v-for="i in (progresData?.inscriptions || [])" :key="i.id" class="border-b border-white/[0.04] last:border-0">
                  <td class="px-4 py-2.5 text-[13px] text-[#c9d1d9]">{{ coursNom(i.cours_id) }}</td>
                  <td class="px-4 py-2.5 text-[13px] text-[#8a95a8]">{{ i.credits }}</td>
                  <td class="px-4 py-2.5 text-[13px] text-[#8a95a8]">{{ i.note_finale ?? '—' }}</td>
                  <td class="px-4 py-2.5 text-[13px] text-[#8a95a8]">{{ i.credits_obtenus ?? '—' }}</td>
                  <td class="px-4 py-2.5">
                    <span class="text-[11px] px-2 py-1 rounded-md border" :class="statutStyle(i.statut)">{{ i.statut }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </Transition>

    <!-- ── Modal saisie de note (Intra ou Final) ──────────────────── -->
    <StyleModal :show="noteModalOpen" max-width="sm" @close="closeNoteModal">
      <template #title><h3>Saisir la note {{ noteModalPhase === 'intra' ? 'Intra' : 'Final' }}</h3></template>
      <template #subtitle>{{ noteModalInscription ? coursNom(noteModalInscription.cours_id) : '' }}</template>
      <template #content>
        <label class="block mb-1.5">Note {{ noteModalPhase === 'intra' ? 'Intra' : 'Final' }}</label>
        <input type="number" step="0.01" v-model="noteValue" placeholder="ex: 65" />
        <p v-if="noteModalDevoirs != null" class="text-[12px] text-[#7aaeff] mt-2">
          Devoirs : {{ noteModalDevoirs }}% — Total : {{ noteTotal }}
        </p>
      </template>
      <template #footer>
        <button class="btn-secondary" @click="closeNoteModal">Annuler</button>
        <button class="btn-primary" :disabled="!noteValueValide" @click="submitNote">Enregistrer</button>
      </template>
    </StyleModal>
  </div>
</template>

<style scoped>
.tab-slide-enter-active, .tab-slide-leave-active {
  transition: opacity .18s ease, transform .18s ease;
}
.tab-slide-enter-from { opacity: 0; transform: translateY(7px); }
.tab-slide-leave-to   { opacity: 0; transform: translateY(-5px); }
</style>
