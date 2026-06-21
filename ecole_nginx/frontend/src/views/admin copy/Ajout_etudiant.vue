<script setup>
import { ref, onMounted, computed, h, defineComponent } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import Swal from 'sweetalert2';
import DialogModal from '@/components/DialogModal.vue';
import { useSchoolStore, useSchoolStoreInfo } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';

const router = useRouter();
const route  = useRoute();
const url    = import.meta.env.VITE_APP_BASE_URL;

const { classes_global, annee_global, niveau_global } = useSchoolStoreInfo();
const schoolStore = useSchoolStore();
const { classes, faculte } = storeToRefs(schoolStore);
schoolStore.fetchAllDependencies();

// ── Inline sub-components ──────────────────────────────────────────────────────

const SectionCard = defineComponent({
  props: ['title', 'icon'],
  setup(props, { slots }) {
    return () => h('div', { class: 'bg-[#161b22] border border-[#21262d] rounded-xl overflow-hidden' }, [
      h('div', { class: 'flex items-center gap-2 px-4 py-3 bg-[#0d1117] border-b border-[#21262d]' }, [
        h('span', { class: 'text-base' }, props.icon),
        h('span', { class: 'text-[12px] font-semibold text-[#e6edf3] uppercase tracking-wide' }, props.title),
      ]),
      h('div', { class: 'p-4' }, slots.default?.()),
    ])
  }
});

const FormField = defineComponent({
  props: ['label', 'error'],
  setup(props, { slots }) {
    return () => h('div', { class: 'flex flex-col gap-1' }, [
      h('label', { class: 'text-[11px] font-medium text-[#7d8590] uppercase tracking-wide' }, props.label),
      slots.default?.(),
      props.error
        ? h('span', { class: 'text-[11px] text-[#f85149] flex items-center gap-1 mt-0.5' }, [
            h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 16 16', fill: 'currentColor', class: 'w-3 h-3 flex-shrink-0' },
              h('path', { 'fill-rule': 'evenodd', d: 'M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14Zm0-4a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM7.25 6a.75.75 0 0 1 1.5 0v2a.75.75 0 0 1-1.5 0V6Z', 'clip-rule': 'evenodd' })
            ),
            props.error,
          ])
        : null,
    ])
  }
});

const InfoRow = defineComponent({
  props: ['label', 'value', 'mono', 'accent'],
  setup(props) {
    return () => h('div', { class: 'flex justify-between items-baseline gap-2 py-0.5' }, [
      h('span', { class: 'text-[11px] text-[#484f58] flex-shrink-0' }, props.label),
      h('span', {
        class: [
          'text-[12px] text-right',
          props.accent ? 'text-[#58a6ff] font-medium' : 'text-[#8b949e]',
          props.mono   ? 'font-mono text-[11px]'      : '',
        ]
      }, props.value || '—'),
    ])
  }
});

// ── Tabs ───────────────────────────────────────────────────────────────────────
const TABS = [
  { id: 'inscription', label: 'Inscription', icon: '🎓' },
  { id: 'responsable', label: 'Responsable', icon: '👤' },
  { id: 'documents',   label: 'Documents',   icon: '📎' },
  { id: 'details',     label: 'Détails',     icon: '🔍', requiresId: true },
];
const activeTab     = ref('inscription');
const transitioning = ref(false);

const visibleTabs = computed(() =>
  TABS.filter(t => !t.requiresId || route.params.etudiantId)
);

function switchTab(tabId) {
  if (tabId === activeTab.value || transitioning.value) return;
  transitioning.value = true;
  setTimeout(() => { activeTab.value = tabId; transitioning.value = false; }, 200);
}

// ── State ──────────────────────────────────────────────────────────────────────
const studentDetails          = ref(null);
const studentData             = ref([]);
const showPayment             = ref(false);
const searchForDetails        = ref(false);
const choseNiveau             = ref({});
const classe_actuelle_        = ref('');
const openAccordionIndex      = ref(null);
const openAccordionIndexPieces = ref(null);
const parcours_cours          = ref([]);
const parcours_paiement       = ref([]); // notes
const parcours_notes          = ref([]); // paiements
const searhStudent            = ref('');

const documentTypes = [
  'Attestation', 'Certificat', 'Certificat de naissance',
  "Carte d'identité", 'Diplôme', 'Relevé de notes',
  "Photo d'identité", 'Autre',
];

const documents = ref([{
  type_de_document: '', document_numero: '',
  document_date_dexpiration: '', document_status: '',
  document_image: '', etudiant_id: '',
}]);

const formEtudiant = ref({
  documentss: [], id: '', dernier_etablissement: '', nisu: '',
  aide_financiere: 'Aucune', nom: '', prenom: '', telephone: '',
  sexe: '', date_de_naissance: '', adresse: '', lieu_de_naissance: '',
  religion: '', niveau_id: '', classe_actuelle_id: '', annee_academique_id: '',
  faculte_id: '', email: '',
  nom_responsable: '', prenom_responsable: '', email_responsable: '',
  relation_responsable: '', sexe_responsable: '', telephone_responsable: '',
  metier_responsable: '', adresse_responsable: '',
  errors: {}
});

const studentDetailsShow = computed(() => !!route.params.etudiantId);

// ── Methods ────────────────────────────────────────────────────────────────────
const toDateInput = (d) => d ? d.split(' ')[0] : '';

const showSwalInfo = (text, color) =>
  Swal.fire({ position: 'top-end', text, showConfirmButton: false, timer: 3000, color });

const actionOnRadionButton = async () => {
  formEtudiant.value.classe_actuelle_id = '';
  formEtudiant.value.faculte_id = '';
  try {
    const r = await axios.get(`${url}/niveau-with-class/${formEtudiant.value.niveau_id}`);
    if (r.status === 200) {
      choseNiveau.value  = r.data.niveau;
      faculte.value      = r.data.facultes;
    }
  } catch (e) { console.error(e); }
};

const addDocument = () => documents.value.push({
  type_de_document: '', document_numero: '',
  document_date_dexpiration: '', document_status: '',
  document_image: '', etudiant_id: '',
});
const removeDocument = (i) => documents.value.splice(i, 1);

const handleFileChange = (e, i) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => { documents.value[i].document_image = reader.result; };
  reader.readAsDataURL(file);
};

const submitEtudiant = async () => {
  formEtudiant.value.documentss = documents.value;
  formEtudiant.value.errors = {};
  try {
    const r = await axios.post(`${url}/etudiant`, formEtudiant.value);
    if (r.data) {
      showSwalInfo(r.data.success, '#34a853');
      if (formEtudiant.value.id) await fetchStudentDetails(formEtudiant.value.id);
      else router.push('/students');
    }
  } catch (e) {
    if (e.response?.data?.detail) showSwalInfo(e.response.data.detail, 'red');
    if (e.response?.data?.errors) formEtudiant.value.errors = e.response.data.errors;
  }
};

const getClassesByNiveau = (niveauId) => {
  if (!niveauId || !classes.value) return [];
  return classes.value.filter(c => c.niveau_id === niveauId);
};

const fetchStudentDetails = async (studentId) => {
  try {
    const r = await axios.get(`${url}/etudiant/${studentId}`);
    if (r.status !== 200) return;
    const data = r.data.data;
    studentDetails.value = data;
    const dC = data.classes_etudiant?.at(-1);
    const dF = data.etudiant_facultes?.at(-1);
    formEtudiant.value = {
      id: data.id || '', dernier_etablissement: data.dernier_etablissement || '',
      nisu: data.nisu || '', aide_financiere: data.aide_financiere || 'Aucune',
      nom: data.nom || '', prenom: data.prenom || '', telephone: data.telephone || '',
      sexe: data.sexe || '', date_de_naissance: toDateInput(data.date_de_naissance),
      adresse: data.adresse || '', lieu_de_naissance: data.lieu_de_naissance || '',
      religion: data.religion || '',
      niveau_id:           dC?.niveau_id           ?? dF?.niveau_id           ?? '',
      classe_actuelle_id:  dC?.classes_id          ?? dF?.classes_id          ?? '',
      annee_academique_id: dC?.annee_academique_id ?? dF?.annee_academique_id ?? '',
      faculte_id: dF?.faculte_id ?? '', email: data.email || '',
      nom_responsable:      data.responsable?.nom_responsable      || '',
      prenom_responsable:   data.responsable?.prenom_responsable   || '',
      email_responsable:    data.responsable?.email_responsable    || '',
      relation_responsable: data.responsable?.relation_responsable || '',
      sexe_responsable:     data.responsable?.sexe_responsable     || '',
      telephone_responsable:data.responsable?.telephone_responsable|| '',
      metier_responsable:   data.responsable?.metier_responsable   || '',
      adresse_responsable:  data.responsable?.adresse_responsable  || '',
      errors: {}
    };
    classe_actuelle_.value = dC?.classes?.nom_classe
      ?? dF?.classes?.nom_classe ?? dF?.classes_id ?? '';
  } catch (e) { console.error(e); }
};

const fetchStudent = async () => {
  try {
    const r = await axios.post(`${url}/fetch-student-paiement`, { val: searhStudent.value });
    if (r.status === 200) {
      showPayment.value      = true;
      studentData.value      = r.data.data;
      searchForDetails.value = true;
    }
  } catch (e) { console.error(e); }
};

const navigateToStudentDetails = (id) => {
  router.push(`/students/${id}`);
  searchForDetails.value = false;
};

const toggleParcours = async (index, classes_id, niveauId, annee_academique, studentId) => {
  if (openAccordionIndex.value === index) { openAccordionIndex.value = null; return; }
  openAccordionIndex.value = index;
  try {
    const r = await axios.get(`${url}/api/parcours-etudiant`, {
      params: { student_id: studentId, classes_id, annee_academique_id: annee_academique, niveau_id: niveauId },
    });
    if (r.status === 200) {
      parcours_cours.value     = r.data.cours;
      parcours_paiement.value  = r.data.notes;
      parcours_notes.value     = r.data.paiements;
    }
  } catch (e) { console.error(e); }
};

const togglePieces = (i) => {
  openAccordionIndexPieces.value = openAccordionIndexPieces.value === i ? null : i;
};

onMounted(async () => {
  if (route.params.etudiantId) await fetchStudentDetails(route.params.etudiantId);
});
</script>

<template>
  <div class="min-h-screen bg-[#0d1117] text-[#c9d1d9]" style="font-family:'DM Sans','Segoe UI',sans-serif">

    <!-- ── Sticky header ── -->
    <div class="sticky top-0 z-30 border-b border-[#21262d] bg-[#0d1117]/90 backdrop-blur-sm">
      <div class="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-[#58a6ff] to-[#1f6feb] flex items-center justify-center">
            🎓
          </div>
          <div>
            <h1 class="text-[#e6edf3] font-semibold text-[15px] leading-tight">
              {{ formEtudiant.id ? "Modifier l'étudiant" : 'Nouvel étudiant' }}
            </h1>
            <p class="text-[#7d8590] text-[11px]">
              {{ formEtudiant.id ? `ID : ${formEtudiant.id}` : "Formulaire d'inscription" }}
            </p>
          </div>
        </div>
        <div
          v-if="Object.keys(formEtudiant.errors).length"
          class="flex items-center gap-2 bg-[#3d1a1a] border border-[#f85149]/30 rounded-lg px-3 py-1.5"
        >
          <span class="w-2 h-2 rounded-full bg-[#f85149] animate-pulse"></span>
          <span class="text-[#f85149] text-[12px]">Erreurs dans le formulaire</span>
        </div>
      </div>
    </div>

    <div class="max-w-6xl mx-auto px-6 pt-5 pb-14">

      <!-- ── Tab bar ── -->
      <div class="flex gap-1 bg-[#161b22] border border-[#21262d] rounded-xl p-1 w-fit mb-6">
        <button
          v-for="tab in visibleTabs" :key="tab.id"
          type="button"
          @click="switchTab(tab.id)"
          :class="[
            'relative flex items-center gap-2 px-5 py-2.5 rounded-lg text-[13px] font-medium transition-all duration-200',
            activeTab === tab.id
              ? 'bg-[#21262d] text-[#e6edf3] shadow-sm'
              : 'text-[#7d8590] hover:text-[#c9d1d9] hover:bg-[#1c2129]'
          ]"
        >
          <span>{{ tab.icon }}</span>
          {{ tab.label }}
          <span v-if="activeTab === tab.id"
            class="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-[#58a6ff]">
          </span>
        </button>
      </div>

      <!-- ── Tab content with transition ── -->
      <form @submit.prevent="submitEtudiant">
        <Transition name="tab-slide" mode="out-in">

          <!-- ══ Inscription ══ -->
          <div v-if="activeTab === 'inscription'" key="inscription" class="space-y-5">

            <SectionCard title="Parcours scolaire" icon="📚">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FormField label="Niveau / Section" :error="formEtudiant.errors?.niveau_e">
                  <select class="field-select" v-model="formEtudiant.niveau_id" @change="actionOnRadionButton">
                    <option value="" disabled>Sélectionner un cycle</option>
                    <option v-for="n in niveau_global" :key="n.id" :value="n.id">{{ n.name }}</option>
                  </select>
                </FormField>
                <FormField label="Dernier établissement" :error="formEtudiant.errors?.dernier_etablissement?.[0]">
                  <input class="field-input" type="text" v-model="formEtudiant.dernier_etablissement" placeholder="Nom de l'établissement" />
                </FormField>
                <FormField label="NISU" :error="formEtudiant.errors?.nisu?.[0]">
                  <input class="field-input" type="text" v-model="formEtudiant.nisu" placeholder="Numéro NISU" />
                </FormField>
              </div>
            </SectionCard>

            <SectionCard title="Identité" icon="🪪">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FormField label="Nom" :error="formEtudiant.errors?.nom?.[0]">
                  <input class="field-input" type="text" v-model="formEtudiant.nom" placeholder="Nom de famille" />
                </FormField>
                <FormField label="Prénom" :error="formEtudiant.errors?.prenom?.[0]">
                  <input class="field-input" type="text" v-model="formEtudiant.prenom" placeholder="Prénom(s)" />
                </FormField>
                <FormField label="Sexe" :error="formEtudiant.errors?.sexe?.[0]">
                  <select class="field-select" v-model="formEtudiant.sexe">
                    <option value="" disabled>Sélectionner</option>
                    <option value="F">Féminin (F)</option>
                    <option value="M">Masculin (M)</option>
                  </select>
                </FormField>
                <FormField label="Date de naissance" :error="formEtudiant.errors?.date_de_naissance?.[0]">
                  <input class="field-input" type="date" v-model="formEtudiant.date_de_naissance" />
                </FormField>
                <FormField label="Lieu de naissance" :error="formEtudiant.errors?.lieu_de_naissance?.[0]">
                  <input class="field-input" type="text" v-model="formEtudiant.lieu_de_naissance" placeholder="Ville / Commune" />
                </FormField>
                <FormField label="Religion" :error="formEtudiant.errors?.religion?.[0]">
                  <input class="field-input" type="text" v-model="formEtudiant.religion" placeholder="Optionnel" />
                </FormField>
              </div>
            </SectionCard>

            <SectionCard title="Contact" icon="📡">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FormField label="Adresse" :error="formEtudiant.errors?.adresse?.[0]">
                  <input class="field-input" type="text" v-model="formEtudiant.adresse" placeholder="Adresse complète" />
                </FormField>
                <FormField label="Téléphone" :error="formEtudiant.errors?.telephone?.[0]">
                  <input class="field-input" type="text" v-model="formEtudiant.telephone" placeholder="+509 ..." />
                </FormField>
                <FormField label="Courriel" :error="formEtudiant.errors?.email?.[0]">
                  <input class="field-input" type="email" v-model="formEtudiant.email" placeholder="exemple@mail.com" />
                </FormField>
              </div>
            </SectionCard>

            <SectionCard title="Inscription académique" icon="📋">
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <FormField label="Année académique" :error="formEtudiant.errors?.annee_academique_id?.[0]">
                  <select class="field-select" v-model="formEtudiant.annee_academique_id">
                    <option value="" disabled>Sélectionner</option>
                    <option v-for="a in annee_global" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
                  </select>
                </FormField>
                <FormField
                  v-if="choseNiveau.name === 'Universitaire' || choseNiveau.name === 'Technique'"
                  label="Faculté / Domaine" :error="formEtudiant.errors?.faculte_id?.[0]"
                >
                  <select class="field-select" v-model="formEtudiant.faculte_id">
                    <option value="" disabled>Sélectionner</option>
                    <option v-for="f in faculte" :key="f.id" :value="f.id">{{ f.nom }}</option>
                  </select>
                </FormField>
                <FormField label="Classe" :error="formEtudiant.errors?.classe_actuelle_id?.[0]">
                  <select class="field-select" v-model="formEtudiant.classe_actuelle_id">
                    <option value="" disabled>Sélectionner</option>
                    <option v-for="c in getClassesByNiveau(formEtudiant.niveau_id)" :key="c.id" :value="c.id">{{ c.nom_classe }}</option>
                  </select>
                </FormField>
                <FormField label="Aide financière" :error="formEtudiant.errors?.aide_financiere">
                  <select class="field-select" v-model="formEtudiant.aide_financiere">
                    <option value="Aucune">Aucune</option>
                    <option value="1/4 Bourse">1/4 Bourse</option>
                    <option value="Démie Bourse">Demi-bourse</option>
                    <option value="Bourse">Bourse complète</option>
                  </select>
                </FormField>
              </div>
            </SectionCard>
          </div>

          <!-- ══ Responsable ══ -->
          <div v-else-if="activeTab === 'responsable'" key="responsable" class="space-y-5">
            <SectionCard title="Informations du responsable" icon="👤">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FormField label="Nom" :error="formEtudiant.errors?.nom_responsable">
                  <input class="field-input" type="text" v-model="formEtudiant.nom_responsable" placeholder="Nom" />
                </FormField>
                <FormField label="Prénom" :error="formEtudiant.errors?.prenom_responsable">
                  <input class="field-input" type="text" v-model="formEtudiant.prenom_responsable" placeholder="Prénom" />
                </FormField>
                <FormField label="Sexe" :error="formEtudiant.errors?.sexe_responsable">
                  <select class="field-select" v-model="formEtudiant.sexe_responsable">
                    <option value="" disabled>Sélectionner</option>
                    <option value="F">Féminin (F)</option>
                    <option value="M">Masculin (M)</option>
                  </select>
                </FormField>
                <FormField label="Adresse" :error="formEtudiant.errors?.adresse_responsable">
                  <input class="field-input" type="text" v-model="formEtudiant.adresse_responsable" placeholder="Adresse" />
                </FormField>
                <FormField label="Téléphone" :error="formEtudiant.errors?.telephone_responsable">
                  <input class="field-input" type="text" v-model="formEtudiant.telephone_responsable" placeholder="+509 ..." />
                </FormField>
                <FormField label="Courriel" :error="formEtudiant.errors?.email_responsable">
                  <input class="field-input" type="email" v-model="formEtudiant.email_responsable" placeholder="email@mail.com" />
                </FormField>
                <FormField label="Métier" :error="formEtudiant.errors?.metier_responsable">
                  <input class="field-input" type="text" v-model="formEtudiant.metier_responsable" placeholder="Profession" />
                </FormField>
                <FormField label="Relation" :error="formEtudiant.errors?.relation_responsable">
                  <input class="field-input" type="text" v-model="formEtudiant.relation_responsable" placeholder="Père, Mère, Tuteur..." />
                </FormField>
              </div>
            </SectionCard>
          </div>

          <!-- ══ Documents ══ -->
          <div v-else-if="activeTab === 'documents'" key="documents" class="space-y-4">
            <SectionCard title="Pièces soumises" icon="📎">
              <TransitionGroup name="doc-list" tag="div" class="space-y-3">
                <div
                  v-for="(doc, index) in documents" :key="index"
                  class="relative group bg-[#0d1117] border border-[#21262d] hover:border-[#30363d] rounded-xl p-4 transition-all duration-200"
                >
                  <span class="absolute -top-2.5 left-4 bg-[#21262d] text-[#58a6ff] text-[10px] font-mono px-2 py-0.5 rounded-full border border-[#30363d]">
                    Doc {{ index + 1 }}
                  </span>
                  <p v-if="formEtudiant.errors?.[`documentss.${index}.type_de_document`]"
                    class="text-[#f85149] text-[12px] mb-2">
                    {{ formEtudiant.errors[`documentss.${index}.type_de_document`] }}
                  </p>
                  <div class="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
                    <FormField label="Type">
                      <select class="field-select" v-model="doc.type_de_document">
                        <option value="" disabled>Sélectionner</option>
                        <option v-for="type in documentTypes" :key="type" :value="type">{{ type }}</option>
                      </select>
                    </FormField>
                    <FormField label="Numéro">
                      <input class="field-input" type="text" v-model="doc.document_numero" placeholder="ex: CIN-12345" />
                    </FormField>
                    <FormField label="Expiration">
                      <input class="field-input" type="date" v-model="doc.document_date_dexpiration" />
                    </FormField>
                    <FormField label="Fichier">
                      <label class="flex items-center gap-2 cursor-pointer bg-[#161b22] border border-[#30363d] hover:border-[#58a6ff]/50 rounded-lg px-3 py-2 transition-colors">
                        <span class="text-[#58a6ff]">📁</span>
                        <span class="text-[12px] text-[#7d8590] truncate">
                          {{ doc.document_image ? 'Sélectionné ✓' : 'Choisir un fichier' }}
                        </span>
                        <input type="file" class="hidden" @change="handleFileChange($event, index)" />
                      </label>
                    </FormField>
                  </div>
                  <button
                    type="button" @click="removeDocument(index)"
                    class="absolute top-3 right-3 opacity-0 group-hover:opacity-100 text-[#7d8590] hover:text-[#f85149] transition-all duration-150"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
                      <path d="M5.28 4.22a.75.75 0 0 0-1.06 1.06L6.94 8l-2.72 2.72a.75.75 0 1 0 1.06 1.06L8 9.06l2.72 2.72a.75.75 0 1 0 1.06-1.06L9.06 8l2.72-2.72a.75.75 0 0 0-1.06-1.06L8 6.94 5.28 4.22Z" />
                    </svg>
                  </button>
                </div>
              </TransitionGroup>

              <button type="button" @click="addDocument"
                class="mt-4 flex items-center gap-2 text-[#58a6ff] hover:text-[#79c0ff] text-[13px] font-medium transition-colors group">
                <span class="w-6 h-6 rounded-md bg-[#1f6feb]/20 border border-[#1f6feb]/30 flex items-center justify-center group-hover:bg-[#1f6feb]/30 transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
                    <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
                  </svg>
                </span>
                Ajouter un document
              </button>
            </SectionCard>

            <div class="flex justify-end">
              <button type="submit"
                class="flex items-center gap-2 bg-gradient-to-r from-[#1f6feb] to-[#388bfd] hover:from-[#388bfd] hover:to-[#58a6ff] text-white font-semibold text-[13px] px-6 py-2.5 rounded-lg transition-all duration-200 shadow-lg shadow-[#1f6feb]/20">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
                  <path d="M12.78 5.22a.749.749 0 0 1 0 1.06l-4.25 4.25a.749.749 0 0 1-1.06 0L5.22 8.28a.749.749 0 1 1 1.06-1.06L8 8.94l3.72-3.72a.749.749 0 0 1 1.06 0Z" />
                </svg>
                {{ formEtudiant.id ? 'Sauvegarder les modifications' : "Enregistrer l'étudiant" }}
              </button>
            </div>
          </div>

          <!-- ══ Détails ══ -->
          <div v-else-if="activeTab === 'details'" key="details" class="space-y-5">

            <!-- Search -->
            <div class="relative max-w-md">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
                class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7d8590] pointer-events-none">
                <path fill-rule="evenodd" d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" clip-rule="evenodd" />
              </svg>
              <input class="field-input pl-9" type="text"
                placeholder="Rechercher un étudiant..."
                v-model="searhStudent" @keyup="fetchStudent" />
            </div>

            <div v-if="studentDetails" class="grid grid-cols-1 md:grid-cols-2 gap-5">

              <!-- Infos perso -->
              <div class="bg-[#161b22] border border-[#21262d] rounded-xl overflow-hidden">
                <div class="flex items-center gap-2 px-4 py-3 bg-[#0d1117] border-b border-[#21262d]">
                  <span>🪪</span>
                  <span class="text-[13px] font-semibold text-[#e6edf3]">Informations personnelles</span>
                </div>
                <div class="p-4 space-y-0.5">
                  <InfoRow label="Identifiant"       :value="studentDetails.identifiant"                             :mono="true" />
                  <InfoRow label="Nom complet"        :value="`${studentDetails.nom} ${studentDetails.prenom}`" />
                  <InfoRow label="Sexe"               :value="studentDetails.sexe" />
                  <InfoRow label="Date de naissance"  :value="studentDetails.date_de_naissance" />
                  <InfoRow label="Lieu de naissance"  :value="studentDetails.lieu_de_naissance" />
                  <InfoRow label="Adresse"            :value="studentDetails.adresse" />
                  <InfoRow label="Téléphone"          :value="studentDetails.telephone" />
                  <InfoRow label="Courriel"           :value="studentDetails.email" />
                  <InfoRow label="Classe actuelle"    :value="classe_actuelle_"                                     :accent="true" />
                </div>
              </div>

              <div class="space-y-4">
                <!-- Responsable -->
                <div v-if="studentDetails.responsable" class="bg-[#161b22] border border-[#21262d] rounded-xl overflow-hidden">
                  <div class="flex items-center gap-2 px-4 py-3 bg-[#0d1117] border-b border-[#21262d]">
                    <span>👤</span>
                    <span class="text-[13px] font-semibold text-[#e6edf3]">Responsable</span>
                  </div>
                  <div class="p-4 space-y-0.5">
                    <InfoRow label="Nom" :value="`${studentDetails.responsable.nom_responsable} ${studentDetails.responsable.prenom_responsable}`" />
                    <InfoRow label="Sexe"      :value="studentDetails.responsable.sexe_responsable" />
                    <InfoRow label="Relation"  :value="studentDetails.responsable.relation_responsable" :accent="true" />
                    <InfoRow label="Métier"    :value="studentDetails.responsable.metier_responsable" />
                    <InfoRow label="Téléphone" :value="studentDetails.responsable.telephone_responsable" />
                    <InfoRow label="Courriel"  :value="studentDetails.responsable.email_responsable" />
                    <InfoRow label="Adresse"   :value="studentDetails.responsable.adresse_responsable" />
                  </div>
                </div>

                <!-- Documents -->
                <div v-if="studentDetails.pieces_soumise?.length" class="bg-[#161b22] border border-[#21262d] rounded-xl overflow-hidden">
                  <div class="flex items-center gap-2 px-4 py-3 bg-[#0d1117] border-b border-[#21262d]">
                    <span>📎</span>
                    <span class="text-[13px] font-semibold text-[#e6edf3]">Documents soumis</span>
                    <span class="ml-auto bg-[#21262d] text-[#7d8590] text-[10px] px-2 py-0.5 rounded-full">
                      {{ studentDetails.pieces_soumise.length }}
                    </span>
                  </div>
                  <div class="divide-y divide-[#21262d]">
                    <div v-for="(piece, i) in studentDetails.pieces_soumise" :key="piece.id">
                      <button type="button" @click="togglePieces(i)"
                        class="w-full flex items-center justify-between px-4 py-2.5 hover:bg-[#1c2129] transition-colors">
                        <span class="text-[13px] text-[#c9d1d9]">{{ piece.type_de_document }}</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
                          class="w-3.5 h-3.5 text-[#7d8590] transition-transform duration-200"
                          :class="openAccordionIndexPieces === i ? 'rotate-180' : ''">
                          <path fill-rule="evenodd" d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
                        </svg>
                      </button>
                      <Transition name="accordion">
                        <div v-if="openAccordionIndexPieces === i" class="px-4 pb-3 flex gap-3">
                          <a :href="piece.document_image_url" target="_blank" rel="noopener">
                            <img :src="piece.document_image_url" alt="" class="h-16 w-12 object-cover rounded-lg border border-[#30363d]" />
                          </a>
                          <div class="space-y-0.5 text-[12px]">
                            <InfoRow label="Numéro"    :value="piece.document_numero" />
                            <InfoRow label="Expiration":value="piece.document_date_dexpiration" />
                            <InfoRow label="Statut"    :value="piece.document_status" />
                          </div>
                        </div>
                      </Transition>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Parcours -->
            <div v-if="studentDetails && (studentDetails.classes_etudiant?.length || studentDetails.etudiant_facultes?.length)"
              class="bg-[#161b22] border border-[#21262d] rounded-xl overflow-hidden">
              <div class="flex items-center gap-2 px-4 py-3 bg-[#0d1117] border-b border-[#21262d]">
                <span>📈</span>
                <span class="text-[13px] font-semibold text-[#e6edf3]">Parcours académique</span>
              </div>
              <div class="divide-y divide-[#21262d]">
                <!-- Classique -->
                <template v-if="studentDetails.classes_etudiant">
                  <div v-for="(p, i) in studentDetails.classes_etudiant" :key="`cl-${i}`">
                    <button type="button"
                      @click="toggleParcours(i, p.classes_id, p.niveau_id, p.annee_academique_id, studentDetails.id)"
                      class="w-full flex items-center justify-between px-4 py-3 hover:bg-[#1c2129] transition-colors">
                      <div class="flex items-center gap-3">
                        <span class="w-2 h-2 rounded-full bg-[#3fb950]"></span>
                        <span class="text-[13px] text-[#c9d1d9] font-medium">{{ p.annee_academiques?.annee_academique }}</span>
                        <span class="text-[11px] text-[#7d8590] bg-[#21262d] px-2 py-0.5 rounded-full">{{ p.classes?.nom_classe }}</span>
                      </div>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
                        class="w-3.5 h-3.5 text-[#7d8590] transition-transform duration-200"
                        :class="openAccordionIndex === i ? 'rotate-180' : ''">
                        <path fill-rule="evenodd" d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
                      </svg>
                    </button>
                    <Transition name="accordion">
                      <div v-if="openAccordionIndex === i" class="border-t border-[#21262d]">

                        <!-- Infos classe -->
                        <div class="px-5 py-3 flex items-center justify-between bg-[#0d1117]/60 border-b border-[#21262d]">
                          <span class="text-[12px] text-[#7d8590]">Classe fréquentée</span>
                          <span class="text-[12px] text-[#e6edf3] font-medium">{{ p.classes?.nom_classe }}</span>
                        </div>

                        <div class="p-5 space-y-5">

                          <!-- 📚 Cours suivis -->
                          <div>
                            <p class="text-[11px] uppercase tracking-widest text-[#7d8590] mb-2 flex items-center gap-1">
                              <span>📚</span> Cours suivis
                            </p>
                            <div v-if="parcours_cours.length" class="flex flex-wrap gap-2">
                              <span v-for="c in parcours_cours" :key="c.id"
                                class="text-[11px] bg-[#1f6feb]/10 border border-[#1f6feb]/20 text-[#58a6ff] px-2.5 py-1 rounded-md font-medium">
                                {{ c.cours_nom }}
                              </span>
                            </div>
                            <p v-else class="text-[12px] text-[#484f58] italic">Aucun cours enregistré</p>
                          </div>

                          <!-- 📊 Notes et moyennes -->
                          <div>
                            <p class="text-[11px] uppercase tracking-widest text-[#7d8590] mb-2 flex items-center gap-1">
                              <span>📊</span> Notes et moyennes
                            </p>
                            <div v-if="parcours_paiement?.length" class="bg-[#0d1117] border border-[#21262d] rounded-lg overflow-hidden">
                              <table class="w-full text-[12px]">
                                <thead>
                                  <tr class="border-b border-[#21262d]">
                                    <th class="text-left text-[10px] uppercase tracking-wider text-[#7d8590] px-3 py-2">Cours</th>
                                    <th class="text-center text-[10px] uppercase tracking-wider text-[#7d8590] px-3 py-2">Note</th>
                                    <th class="text-center text-[10px] uppercase tracking-wider text-[#7d8590] px-3 py-2">Mention</th>
                                  </tr>
                                </thead>
                                <tbody class="divide-y divide-[#21262d]">
                                  <tr v-for="note in parcours_paiement" :key="note.id"
                                    class="hover:bg-[#161b22] transition-colors">
                                    <td class="px-3 py-2 text-[#c9d1d9]">{{ note.cours?.cours_nom ?? note.cours_nom ?? '—' }}</td>
                                    <td class="px-3 py-2 text-center">
                                      <span :class="[
                                        'font-mono font-semibold',
                                        (note.note ?? note.valeur) >= 10 ? 'text-[#3fb950]' : 'text-[#f85149]'
                                      ]">{{ note.note ?? note.valeur ?? '—' }}</span>
                                    </td>
                                    <td class="px-3 py-2 text-center text-[#7d8590]">{{ note.mention ?? '—' }}</td>
                                  </tr>
                                </tbody>
                              </table>
                            </div>
                            <p v-else class="text-[12px] text-[#484f58] italic">Aucune note enregistrée</p>
                          </div>

                          <!-- 💰 Suivi financier -->
                          <div>
                            <p class="text-[11px] uppercase tracking-widest text-[#7d8590] mb-2 flex items-center gap-1">
                              <span>💰</span> Suivi financier
                            </p>
                            <div v-if="parcours_notes?.length" class="bg-[#0d1117] border border-[#21262d] rounded-lg overflow-hidden">
                              <table class="w-full text-[12px]">
                                <thead>
                                  <tr class="border-b border-[#21262d]">
                                    <th class="text-left text-[10px] uppercase tracking-wider text-[#7d8590] px-3 py-2">Description</th>
                                    <th class="text-center text-[10px] uppercase tracking-wider text-[#7d8590] px-3 py-2">Montant</th>
                                    <th class="text-center text-[10px] uppercase tracking-wider text-[#7d8590] px-3 py-2">Statut</th>
                                    <th class="text-right text-[10px] uppercase tracking-wider text-[#7d8590] px-3 py-2">Date</th>
                                  </tr>
                                </thead>
                                <tbody class="divide-y divide-[#21262d]">
                                  <tr v-for="paiement in parcours_notes" :key="paiement.id"
                                    class="hover:bg-[#161b22] transition-colors">
                                    <td class="px-3 py-2 text-[#c9d1d9]">{{ paiement.description ?? paiement.motif ?? '—' }}</td>
                                    <td class="px-3 py-2 text-center font-mono text-[#3fb950] font-medium">
                                      {{ paiement.montant ? `${paiement.montant} HTG` : '—' }}
                                    </td>
                                    <td class="px-3 py-2 text-center">
                                      <span :class="[
                                        'text-[10px] px-2 py-0.5 rounded-full border',
                                        paiement.statut === 'Payé'
                                          ? 'bg-[#1a4731] border-[#2ea043]/30 text-[#3fb950]'
                                          : 'bg-[#3d1a1a] border-[#f85149]/30 text-[#f85149]'
                                      ]">{{ paiement.statut ?? '—' }}</span>
                                    </td>
                                    <td class="px-3 py-2 text-right text-[#7d8590]">{{ paiement.date ?? paiement.created_at?.split(' ')[0] ?? '—' }}</td>
                                  </tr>
                                </tbody>
                              </table>
                            </div>
                            <p v-else class="text-[12px] text-[#484f58] italic">Aucun paiement enregistré</p>
                          </div>

                          <!-- 🧾 Vie scolaire -->
                          <div>
                            <p class="text-[11px] uppercase tracking-widest text-[#7d8590] mb-2 flex items-center gap-1">
                              <span>🧾</span> Vie scolaire
                            </p>
                            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                              <div v-for="stat in [
                                { label: 'Absences',   value: p.absences   ?? '—', color: 'text-[#f85149]' },
                                { label: 'Retards',    value: p.retards    ?? '—', color: 'text-[#d29922]' },
                                { label: 'Sanctions',  value: p.sanctions  ?? '—', color: 'text-[#d29922]' },
                                { label: 'Appréciations', value: p.appreciation ?? '—', color: 'text-[#3fb950]' },
                              ]" :key="stat.label"
                                class="bg-[#0d1117] border border-[#21262d] rounded-lg p-3 text-center">
                                <p class="text-[11px] text-[#7d8590] mb-1">{{ stat.label }}</p>
                                <p :class="['text-[18px] font-bold', stat.color]">{{ stat.value }}</p>
                              </div>
                            </div>
                          </div>

                        </div>
                      </div>
                    </Transition>
                  </div>
                </template>
                <!-- Universitaire -->
                <template v-if="studentDetails.etudiant_facultes">
                  <div v-for="(p, i) in studentDetails.etudiant_facultes" :key="`fac-${i}`">
                    <button type="button"
                      @click="toggleParcours(100+i, p.classes_id, p.niveau_id, p.annee_academique_id, studentDetails.id)"
                      class="w-full flex items-center justify-between px-4 py-3 hover:bg-[#1c2129] transition-colors">
                      <div class="flex items-center gap-3">
                        <span class="w-2 h-2 rounded-full bg-[#d2a8ff]"></span>
                        <span class="text-[13px] text-[#c9d1d9] font-medium">{{ p.annee_academiques?.annee_academique }}</span>
                        <span class="text-[11px] text-[#7d8590] bg-[#21262d] px-2 py-0.5 rounded-full">{{ p.classes?.nom_classe }}</span>
                        <span class="text-[10px] bg-[#3d1a6e]/40 border border-[#6e40c9]/20 text-[#d2a8ff] px-1.5 py-0.5 rounded">Univ.</span>
                      </div>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
                        class="w-3.5 h-3.5 text-[#7d8590] transition-transform duration-200"
                        :class="openAccordionIndex === 100+i ? 'rotate-180' : ''">
                        <path fill-rule="evenodd" d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
                      </svg>
                    </button>
                    <Transition name="accordion">
                      <div v-if="openAccordionIndex === 100+i" class="px-6 pb-4">
                        <p class="text-[12px] text-[#7d8590]">Classe : {{ p.classes?.nom_classe }}</p>
                      </div>
                    </Transition>
                  </div>
                </template>
              </div>
            </div>

            <!-- Empty state -->
            <div v-else-if="!studentDetails" class="flex flex-col items-center justify-center py-20 text-center">
              <span class="text-4xl mb-4">🔍</span>
              <p class="text-[#7d8590] text-[14px]">Recherchez un étudiant pour afficher ses détails</p>
              <p class="text-[#484f58] text-[12px] mt-1">Utilisez la barre de recherche ci-dessus</p>
            </div>
          </div>

        </Transition>
      </form>
    </div>

    <!-- ── Search Modal ── -->
    <DialogModal :show="searchForDetails" @close="searchForDetails = false">
      <template #title>
        <div class="flex items-center justify-between">
          <span class="text-[#e6edf3] font-semibold text-[15px]">Recherche étudiant</span>
          <button type="button" @click="searchForDetails = false" class="text-[#7d8590] hover:text-[#e6edf3] transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
              <path d="M5.28 4.22a.75.75 0 0 0-1.06 1.06L6.94 8l-2.72 2.72a.75.75 0 1 0 1.06 1.06L8 9.06l2.72 2.72a.75.75 0 1 0 1.06-1.06L9.06 8l2.72-2.72a.75.75 0 0 0-1.06-1.06L8 6.94 5.28 4.22Z" />
            </svg>
          </button>
        </div>
      </template>
      <template #content>
        <div class="p-4 space-y-3">
          <input class="field-input w-full" type="text"
            placeholder="Identifiant de l'étudiant..."
            v-model="searhStudent" @keyup="fetchStudent" autofocus />
          <div v-if="showPayment" class="border border-[#21262d] rounded-xl overflow-hidden">
            <div v-for="s in studentData" :key="s.id"
              class="flex items-center justify-between px-4 py-2.5 hover:bg-[#1c2129] transition-colors border-b border-[#21262d] last:border-0">
              <div class="flex items-center gap-3">
                <span class="text-[11px] text-[#7d8590] font-mono">{{ s.identifiant }}</span>
                <span class="text-[13px] text-[#c9d1d9]">{{ s.nom }} {{ s.prenom }}</span>
              </div>
              <button type="button" @click="navigateToStudentDetails(s.id)"
                class="text-[12px] text-[#58a6ff] hover:text-[#79c0ff] transition-colors">
                Voir détails →
              </button>
            </div>
          </div>
        </div>
      </template>
    </DialogModal>
  </div>
</template>

<style scoped>
.field-input {
  width: 100%;
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 8px 12px;
  color: #e6edf3;
  font-size: 13px;
  outline: none;
  transition: border-color .15s, box-shadow .15s;
}
.field-input::placeholder { color: #484f58; }
.field-input:focus {
  border-color: #58a6ff;
  box-shadow: 0 0 0 3px rgba(88,166,255,.1);
}
.field-input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(.5); }

.field-select {
  width: 100%;
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 8px 12px;
  color: #e6edf3;
  font-size: 13px;
  outline: none;
  cursor: pointer;
  transition: border-color .15s;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%237d8590'%3E%3Cpath fill-rule='evenodd' d='M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z' clip-rule='evenodd'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 14px;
  padding-right: 32px;
}
.field-select:focus { border-color: #58a6ff; }
.field-select option { background: #161b22; color: #e6edf3; }

/* Tab slide */
.tab-slide-enter-active, .tab-slide-leave-active {
  transition: opacity .2s ease, transform .2s ease;
}
.tab-slide-enter-from { opacity: 0; transform: translateY(8px); }
.tab-slide-leave-to   { opacity: 0; transform: translateY(-6px); }

/* Accordion */
.accordion-enter-active, .accordion-leave-active {
  transition: all .25s ease;
  overflow: hidden;
}
.accordion-enter-from, .accordion-leave-to {
  opacity: 0; max-height: 0; padding-top: 0; padding-bottom: 0;
}
.accordion-enter-to, .accordion-leave-from {
  opacity: 1; max-height: 600px;
}

/* Doc list */
.doc-list-enter-active { transition: all .25s ease; }
.doc-list-leave-active { transition: all .2s ease; position: absolute; }
.doc-list-enter-from   { opacity: 0; transform: translateX(-10px); }
.doc-list-leave-to     { opacity: 0; transform: translateX(10px); }
</style>
