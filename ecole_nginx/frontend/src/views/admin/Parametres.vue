<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Swal from 'sweetalert2';
import AdminLayout from '@/layouts/AdminLayout.vue';
import Checkbox from '@/components/Checkbox.vue';
import InputError from '@/components/InputError.vue';
import InputLabel from '@/components/InputLabel.vue';
import Paginated from '@/components/Paginated.vue';
import TextInput from '@/components/TextInput.vue';
import PrimaryButton from '@/components/PrimaryButton.vue';
import StyleModal from '@/components/StyleModal.vue';
import DangerButton from '@/components/DangerButton.vue';
import Pagination from '@/components/Pagination.vue';

import { useSchoolStore } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';

const router = useRouter();
const url = import.meta.env.VITE_APP_BASE_URL;

const schoolStore = useSchoolStore();
const { niveau, professeur, annee, classes, faculte, cours, loading } = storeToRefs(schoolStore);

onMounted(() => {
  schoolStore.fetchAllDependencies();
});

// ── Tab System ─────────────────────────────────────────────────
const tabs = [
  { id: 'exams',     label: 'Examens',   icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.7" width="15" height="15"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2M9 12l2 2 4-4"/></svg>` },
  { id: 'facultes',  label: 'Facultés',  icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.7" width="15" height="15"><path d="M12 3L2 9l10 6 10-6-10-6zM2 17l10 6 10-6M2 13l10 6 10-6"/></svg>` },
  { id: 'annees',    label: 'Années',    icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.7" width="15" height="15"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>` },
  { id: 'classes',   label: 'Classes',   icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.7" width="15" height="15"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>` },
  { id: 'paiements', label: 'Paiements', icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.7" width="15" height="15"><rect x="1" y="4" width="22" height="16" rx="2"/><path d="M1 10h22"/></svg>` },
  { id: 'frais',     label: 'Frais',     icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.7" width="15" height="15"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>` },
];

const activeTab = ref('exams');
const isTransitioning = ref(false);

const setTab = (tabId) => {
  if (activeTab.value === tabId) return;
  isTransitioning.value = true;
  setTimeout(() => {
    activeTab.value = tabId;
    isTransitioning.value = false;
  }, 160);
};

// ── Helpers ────────────────────────────────────────────────────
const getClassesByNiveau = (niveauId) => {
  if (!niveauId || !classes.value) return [];
  return classes.value.filter(c => c.niveau_id === niveauId);
};

// ── Modal refs ─────────────────────────────────────────────────
const grade_etude = ref(false);
const faculte_profession = ref(false);
const anneeAcademique = ref(false);
const niveau_detude_modal_classe = ref(false);
const exam_params = ref(false);
const Payment_params_show = ref(false);
const fraisModal = ref(false);
const changeButton = ref(false);

// ── Data refs ──────────────────────────────────────────────────
const nbControleOrVersementOrtrimestre = ref([]);
const versementEntriesForm = ref([]);
const editMontantPar = ref(false);
const annee_niveau_detude_classique = ref([]);
const niveauUniver = ref(false);
const anneeFac_forPayment = ref([]);
const echeance = ref('');
const choseNiveau = ref([]);
const niveau_et = ref([]);
const classeParams = ref({ data: [], meta: {} });
const paimentParams = ref({ data: [], meta: {} });
const facultePaginate = ref({ data: [], meta: {} });
const anneeAcademiquePaginate = ref({ data: [], meta: {} });
const annee_paginate = ref({ data: [], meta: {} });
const examPaginate = ref({ data: [], meta: {} });
const frais_paginate = ref([]);
const faculte_niv = ref([]);

const accessoireTypes = ref(['Maillot', 'Badge', 'Tenue de Sport', 'Initiale']);
const accessoires = ref([{ type_daccessoire: '', prix: '' }]);

// ── Forms ──────────────────────────────────────────────────────
const form = ref({ id: '', nom: '', nb_annee: '', errors: {} });
const formyear = ref({ id: '', date_debut: '', date_fin: '', niveau_detude: '', errors: {} });
const formNiveau = ref({ id: '', niveau_id: '', faculte_id: '', nom_classe: '', errors: {} });
const formExamParam = ref({ id: '', niveau_id: '', annee_academique_id: '', evaluation_par: '', errors: {} });
const formgrade = ref({ id: '', name: '', errors: {} });
const paymentFormParams = ref({
  id: '', niveau_id: '', faculte_id: '', classe: '', echeance: '', devise: '',
  anneeAcademique: '', nb_echeance: '', montant: '', montant_par: {}, accessoires: [], errors: {}
});
const formFrais = ref({ id: '', niveau_id: '', prix: '', anneeAc: '', errors: {} });

// ── Lifecycle ──────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([
    getParamForExam(), getClasses(), getPaymentParams(),
    getYear(), getFraisDinscription(), getNiveaux(), getFacultes()
  ]);
});

// ── API ────────────────────────────────────────────────────────
const getNiveaux = async () => {
  try { const res = await axios.get(`${url}/niveau`); niveau.value = res.data.data || res.data; }
  catch (e) { console.error(e); }
};
const getFacultes = async () => {
  try {
    const res = await axios.get(`${url}/get-all-faculte`);
    faculte_niv.value = res.data.data || res.data;
    facultePaginate.value = res.data;
  } catch (e) { console.error(e); }
};
const actionOnRadionButton = async (event) => {
  formNiveau.value.faculte_id = '';
  formNiveau.value.nom_classe = '';
  try {
    const res = await axios.get(`${url}/niveau-with-class/${event.target.value}`);
    choseNiveau.value = res.data.niveau;
    annee_niveau_detude_classique.value = res.data.annee;
    faculte.value = res.data.facultes;
    anneeFac_forPayment.value = res.data.classe_actuelle;
    if (paymentFormParams.value.id === '') {
      paymentFormParams.value.faculte_id = '';
      paymentFormParams.value.classe = '';
      paymentFormParams.value.devise = '';
      paymentFormParams.value.montant = '';
    }
    niveauUniver.value = res.data.niveau.name === 'Universitaire';
  } catch (e) { console.error(e); }
};
const actionFillRadionNiveauButton = async () => {
  try { const res = await axios.get(`${url}/niveau`); niveau_et.value = res.data.data; }
  catch (e) { console.error(e); }
};
const actionFillMenuButton = async (n) => {
  try { const res = await axios.get(`${url}/niveau-with-class/${n}`); anneeFac_forPayment.value = res.data.classe_actuelle; }
  catch (e) { console.error(e); }
};

// FACULTE
const facModalShow = () => { faculte_profession.value = true; };
const facModalClose = () => { faculte_profession.value = false; changeButton.value = false; form.value = { id: '', nom: '', nb_annee: '', errors: {} }; };
const submitFac = async () => {
  try {
    const res = await axios.post(`${url}/post-faculte`, form.value);
    if (res.status === 200) { showSwalSuccess('Faculté ajoutée avec succès'); await getFacultes(); facModalClose(); }
  } catch (e) {
    if (e.response?.data?.errors) form.value.errors = e.response.data.errors;
    showSwalError("Erreur lors de l'ajout de la faculté");
  }
};

// YEAR
const yearModalShow = () => { anneeAcademique.value = true; };
const yearModalClose = () => { anneeAcademique.value = false; changeButton.value = false; formyear.value = { id: '', date_debut: '', date_fin: '', niveau_detude: '', errors: {} }; };
const submitYear = async () => {
  try {
    const res = await axios.post(`${url}/anneeAcademique`, formyear.value);
    if (res.status === 200) { showSwalSuccess('Année académique ajoutée avec succès'); await getYear(); yearModalClose(); }
  } catch (e) {
    if (e.response?.data?.errors) formyear.value.errors = e.response.data.errors;
    showSwalError("Erreur lors de l'ajout de l'année");
  }
};
const getYear = async () => {
  try {
    const res = await axios.get(`${url}/anneeAcademique`);
    if (res.status === 200) { anneeAcademiquePaginate.value = res.data; annee_paginate.value = res.data; }
  } catch (e) { console.error(e); }
};

// NIVEAU/CLASSE
const niveauModalShow = () => { actionFillRadionNiveauButton(); niveau_detude_modal_classe.value = true; };
const niveauModalClose = () => { niveau_detude_modal_classe.value = false; choseNiveau.value = ''; changeButton.value = false; formNiveau.value = { id: '', niveau_id: '', faculte_id: '', nom_classe: '', errors: {} }; };
const submitNiveau = async () => {
  try {
    const res = await axios.post(`${url}/classes`, formNiveau.value);
    if (res.status === 200) { showSwalSuccess('Classe ajoutée avec succès'); await getClasses(); niveauModalClose(); }
  } catch (e) {
    if (e.response?.data?.errors) formNiveau.value.errors = e.response.data.errors;
    showSwalError("Erreur lors de l'ajout de la classe");
  }
};
const getClasses = async (page = 1) => {
  try {
    const res = await axios.get(`${url}/classes`, { params: { page } });
    if (res.status === 200) classeParams.value = res.data;
  } catch (e) { console.error(e); }
};

// FRAIS
const fraisModalShow = () => { fraisModal.value = true; };
const fraisModalClose = () => { fraisModal.value = false; changeButton.value = false; formFrais.value = { id: '', niveau_id: '', prix: '', anneeAc: '', errors: {} }; };
const storeFraisDinscription = async () => {
  try {
    const res = await axios.post(`${url}/fraisDinscription`, formFrais.value);
    if (res.status === 200) { showSwalSuccess("Frais d'inscription ajoutés avec succès"); await getFraisDinscription(); fraisModalClose(); }
  } catch (e) {
    if (e.response?.data?.errors) formFrais.value.errors = e.response.data.errors;
    showSwalError("Erreur lors de l'ajout des frais");
  }
};
const getFraisDinscription = async () => {
  try {
    const res = await axios.get(`${url}/fraisDinscription`);
    if (res.status === 200) frais_paginate.value = res.data.data;
  } catch (e) { console.error(e); }
};
const editFrais = (f) => {
  formFrais.value = { id: f.id, niveau_id: f.niveau_id, prix: f.prix, anneeAc: f.anneeAc, errors: {} };
  changeButton.value = true;
  fraisModalShow();
};

// EXAM
const examParamsModalShow = () => { exam_params.value = true; };
const examParamsModalClose = () => { formExamParam.value = { id: '', niveau_id: '', annee_academique_id: '', evaluation_par: '', errors: {} }; exam_params.value = false; changeButton.value = false; };
const getParamForExam = async (page = 1) => {
  try {
    const res = await axios.get(`${url}/paramsExam`, { params: { page } });
    if (res.status === 200) examPaginate.value = res.data;
  } catch (e) { console.error(e); }
};
const submitParamForExam = async () => {
  try {
    const res = await axios.post(`${url}/paramsExam`, formExamParam.value);
    if (res.status === 200) { showSwalSuccess("Paramètres d'examen ajoutés avec succès"); await getParamForExam(); examParamsModalClose(); }
  } catch (e) {
    if (e.response?.data?.errors) formExamParam.value.errors = e.response.data.errors;
    showSwalError("Erreur lors de l'ajout des paramètres");
  }
};

// PAYMENT
const paymentParamsModalShow = () => { actionFillRadionNiveauButton(); Payment_params_show.value = true; };
const paymentParamsModalClose = () => {
  Payment_params_show.value = false; changeButton.value = false;
  paymentFormParams.value = { id: '', niveau_id: '', faculte_id: '', classe: '', echeance: '', devise: '', anneeAcademique: '', nb_echeance: '', montant: '', montant_par: {}, accessoires: [], errors: {} };
  accessoires.value = [{ type_daccessoire: '', prix: '' }];
};
const submitPaymentParams = async () => {
  paymentFormParams.value.accessoires = accessoires.value;
  try {
    const res = await axios.post(`${url}/parametrePaiement`, paymentFormParams.value);
    if (res.status === 200) { showSwalSuccess('Paramètres de paiement ajoutés avec succès'); await getPaymentParams(); paymentParamsModalClose(); }
  } catch (e) {
    if (e.response?.data) paymentFormParams.value.errors = e.response.data;
    showSwalError("Erreur lors de l'ajout des paramètres");
  }
};
const getPaymentParams = async (page = 1) => {
  try {
    const res = await axios.get(`${url}/parametrePaiement`, { params: { page } });
    if (res.status === 200) paimentParams.value = res.data;
  } catch (e) { console.error(e); }
};
const GenereVersementInput = (e) => {
  editMontantPar.value = false;
  nbControleOrVersementOrtrimestre.value = Array.from({ length: parseInt(e.target.value, 10) || 0 }, () => '');
  paymentFormParams.value.montant_par = {};
};
const changeEcheance = (e) => {
  echeance.value = e.target.value;
  editMontantPar.value = false;
  paymentFormParams.value.montant_par = {};
  paymentFormParams.value.nb_echeance = '';
  nbControleOrVersementOrtrimestre.value = [];
};

// ACCESSOIRES
const addAccessoire = () => { accessoires.value.push({ type_daccessoire: '', prix: '' }); };
const removeAccessoire = (i) => { accessoires.value.splice(i, 1); };

// ROW ACTIONS
const actionsOnClasse = async (event) => {
  const classeId = event.target.closest('td').dataset.set;
  const id = event.target.id;
  switch (id) {
    case 'edit_classe':
      try { const res = await axios.get(`${url}/classes/${classeId}`); formNiveau.value = { ...res.data.data, errors: {} }; changeButton.value = true; niveauModalShow(); }
      catch (e) { console.error(e); }
      break;
    case 'edit_year':
      try { const res = await axios.get(`${url}/anneeAcademique/${classeId}`); formyear.value = { ...res.data.data, errors: {} }; changeButton.value = true; yearModalShow(); }
      catch (e) { console.error(e); }
      break;
    case 'edit_paiement':
      try {
        const res = await axios.get(`${url}/parametrePaiement/${classeId}`);
        const d = res.data?.data;
        paymentFormParams.value = { id: d.id, niveau_id: d.niveau_id, faculte_id: d.faculte_id, classe: d.classe, echeance: d.echeance, devise: d.devise, anneeAcademique: d.anneeAcademique, nb_echeance: d.nb_echeance, montant: d.montant, montant_par: d.montant_par, accessoires: [], errors: {} };
        echeance.value = d.echeance;
        await actionFillMenuButton(d.niveau_id);
        if (d.montant_par?.Versement) { versementEntriesForm.value = Object.entries(d.montant_par.Versement); editMontantPar.value = true; paymentFormParams.value.montant_par = Object.fromEntries(versementEntriesForm.value); }
        changeButton.value = true; paymentParamsModalShow();
      } catch (e) { console.error(e); }
      break;
    case 'edit_exam':
      try {
        const res = await axios.get(`${url}/paramsExam/${classeId}`);
        if (res.status === 200) { formExamParam.value = { ...res.data.data, errors: {} }; changeButton.value = true; examParamsModalShow(); }
      } catch (e) { console.error(e); }
      break;
  }
};

const goToPage = async (page, urlSearch, receiveData) => {
  try { const res = await axios.get(urlSearch, { params: { page } }); receiveData.value = res.data.data; }
  catch (e) { console.error(e); }
};
const changePageForFac = (link) => {
  if (link.url) { const page = parseInt(new URLSearchParams(link.url.split('?')[1]).get('page')) || 1; goToPage(page, `${url}/faculte-paginate-search`, facultePaginate); }
};
const changePageForYear = (link) => {
  if (link.url) { const page = parseInt(new URLSearchParams(link.url.split('?')[1]).get('page')) || 1; goToPage(page, `${url}/anneeAcademique`, annee_paginate); }
};

const showSwalSuccess = (text) => Swal.fire({ position: 'top-end', text, showConfirmButton: false, timer: 2000, color: '#34a853' });
const showSwalError = (text) => Swal.fire({ position: 'top-end', text, showConfirmButton: false, timer: 2000, color: '#e94335' });
const gradeModalClose = () => {};
</script>

<template>
  <div
    class="min-h-screen pb-12  animate-[fadeUp_0.4s_ease_both]"
    style="background: #0f1117; font-family: 'DM Sans', 'Segoe UI', sans-serif;"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

      <!-- ── Page Header ── -->
      <div class="mb-6">
        <h1 class="text-[22px] font-bold text-[#e8eaf0] tracking-tight">Paramètres Académiques</h1>
        <p class="text-[13px] text-[#7c83a0] mt-0.5">Gérez les configurations de votre établissement</p>
      </div>

      <!-- ── Tab Bar ── -->
      <div class="mb-5">
        <div class="flex items-center gap-1 bg-[#171b26] rounded-2xl p-1.5 border border-white/[0.07] overflow-x-auto">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="setTab(tab.id)"
            class="relative flex items-center gap-2 px-4 py-2 rounded-xl text-[13px] font-medium whitespace-nowrap transition-all duration-200 flex-shrink-0"
            :class="{
              'bg-white/[0.1] text-[#e8eaf0] shadow-sm border border-white/[0.1]': activeTab === tab.id,
              'text-[#7c83a0] hover:text-[#c0c7d8] hover:bg-white/[0.04]': activeTab !== tab.id,
            }"
          >
            <span
              class="flex-shrink-0 transition-colors duration-200"
              :class="activeTab === tab.id ? 'text-[#7aaeff]' : 'text-[#7c83a0]'"
              v-html="tab.icon"
            />
            {{ tab.label }}
            <span
              v-if="activeTab === tab.id"
              class="w-1.5 h-1.5 rounded-full bg-[#4f8ef7] ml-0.5"
            />
          </button>
        </div>
      </div>

      <!-- ── Tab Content ── -->
      <div
        :class="{ 'opacity-0 translate-y-2 pointer-events-none': isTransitioning, 'opacity-100 translate-y-0': !isTransitioning }"
        style="transition: opacity 0.16s ease, transform 0.16s ease"
      >

        <!-- ── Shared card wrapper macro ─────────────────────── -->

        <!-- TAB: Examens -->
        <div v-show="activeTab === 'exams'">
          <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden">
            <div class="flex items-center justify-between px-6 py-4 border-b border-white/[0.07]">
              <div>
                <h2 class="text-[14px] font-semibold text-[#e8eaf0]">Paramètres des Examens</h2>
                <p class="text-[12px] text-[#7c83a0] mt-0.5">Configurez les méthodes d'évaluation par cycle et année</p>
              </div>
              <button @click="examParamsModalShow" class="inline-flex items-center gap-2 px-3.5 py-2 bg-[#4f8ef7]/15 text-[#7aaeff] border border-[#4f8ef7]/25 rounded-xl text-[12px] font-medium hover:bg-[#4f8ef7]/25 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5"><path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"/></svg>
                Ajouter
              </button>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-[13px]">
                <thead>
                  <tr class="border-b border-white/[0.05] bg-[#0d1117]/60">
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Cycle</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Évaluation</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Année Académique</th>
                    <th class="px-6 py-3 text-right text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-white/[0.04]">
                  <tr v-if="!examPaginate.data || examPaginate.data.length === 0">
                    <td colspan="4" class="px-6 py-12 text-center">
                      <div class="flex flex-col items-center gap-2 text-[#3d4d62]">
                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.3" class="w-10 h-10 opacity-30"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
                        <span class="text-[12px]">Aucun paramètre configuré</span>
                      </div>
                    </td>
                  </tr>
                  <tr v-else v-for="exam in examPaginate.data" :key="exam.id" class="hover:bg-white/[0.02] transition-colors">
                    <td class="px-6 py-3 font-medium text-[#c9d1d9]">{{ exam.niveau_name }}</td>
                    <td class="px-6 py-3">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-sky-500/10 text-sky-400 border border-sky-500/20">{{ exam.evaluation_par }}</span>
                    </td>
                    <td class="px-6 py-3 text-[#7c83a0]">{{ exam.annee_academique }}</td>
                    <td class="px-6 py-3 text-right" :data-set="exam.id" @click="actionsOnClasse">
                      <button id="delete_exam" class="inline-flex items-center justify-center w-7 h-7 rounded-lg hover:bg-red-500/10 text-[#3d4d62] hover:text-red-400 transition-colors mr-1">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 pointer-events-none"><path fill-rule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Z" clip-rule="evenodd"/></svg>
                      </button>
                      <button id="edit_exam" class="inline-flex items-center justify-center w-7 h-7 rounded-lg hover:bg-amber-500/10 text-[#3d4d62] hover:text-amber-400 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 pointer-events-none"><path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.848 2.047a.75.75 0 0 0 .98.98l2.047-.848a2.75 2.75 0 0 0 .892-.596l4.261-4.262a1.75 1.75 0 0 0 0-2.474Z"/><path d="M4.75 3.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V9A.75.75 0 0 1 14 9v2.25A2.75 2.75 0 0 1 11.25 14h-6.5A2.75 2.75 0 0 1 2 11.25v-6.5A2.75 2.75 0 0 1 4.75 2H7a.75.75 0 0 1 0 1.5H4.75Z"/></svg>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="px-6 py-3 border-t border-white/[0.05]">
              <Pagination :meta="examPaginate.meta" @change-page="(page) => getParamForExam(page)" />
            </div>
          </div>
        </div>

        <!-- TAB: Facultés -->
        <div v-show="activeTab === 'facultes'">
          <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden">
            <div class="flex items-center justify-between px-6 py-4 border-b border-white/[0.07]">
              <div>
                <h2 class="text-[14px] font-semibold text-[#e8eaf0]">Facultés / Professions</h2>
                <p class="text-[12px] text-[#7c83a0] mt-0.5">Gérez les domaines d'étude disponibles</p>
              </div>
              <button @click="facModalShow" class="inline-flex items-center gap-2 px-3.5 py-2 bg-[#4f8ef7]/15 text-[#7aaeff] border border-[#4f8ef7]/25 rounded-xl text-[12px] font-medium hover:bg-[#4f8ef7]/25 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5"><path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"/></svg>
                Ajouter
              </button>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-[13px]">
                <thead>
                  <tr class="border-b border-white/[0.05] bg-[#0d1117]/60">
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Nom</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Nbre sessions</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Statut</th>
                    <th class="px-6 py-3 text-right text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-white/[0.04]">
                  <tr v-if="!facultePaginate.data || facultePaginate.data.length === 0">
                    <td colspan="4" class="px-6 py-12 text-center">
                      <div class="flex flex-col items-center gap-2 text-[#3d4d62]">
                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.3" class="w-10 h-10 opacity-30"><path d="M12 3L2 9l10 6 10-6-10-6zM2 17l10 6 10-6M2 13l10 6 10-6"/></svg>
                        <span class="text-[12px]">Aucune faculté enregistrée</span>
                      </div>
                    </td>
                  </tr>
                  <tr v-else v-for="fac in facultePaginate.data" :key="fac.id" class="hover:bg-white/[0.02] transition-colors">
                    <td class="px-6 py-3 font-medium text-[#c9d1d9]">{{ fac.nom }}</td>
                    <td class="px-6 py-3 text-[#7c83a0]">{{ fac.nb_annee }}</td>
                    <td class="px-6 py-3">
                      <span v-if="fac.status == 1" class="inline-flex items-center gap-1.5 text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Actif
                      </span>
                      <span v-else class="inline-flex items-center gap-1.5 text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
                        <span class="w-1.5 h-1.5 rounded-full bg-red-400"></span> Inactif
                      </span>
                    </td>
                    <td class="px-6 py-3 text-right">
                      <button class="inline-flex items-center justify-center w-7 h-7 rounded-lg hover:bg-red-500/10 text-[#3d4d62] hover:text-red-400 transition-colors mr-1">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5"><path fill-rule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Z" clip-rule="evenodd"/></svg>
                      </button>
                      <button class="inline-flex items-center justify-center w-7 h-7 rounded-lg hover:bg-amber-500/10 text-[#3d4d62] hover:text-amber-400 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5"><path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.848 2.047a.75.75 0 0 0 .98.98l2.047-.848a2.75 2.75 0 0 0 .892-.596l4.261-4.262a1.75 1.75 0 0 0 0-2.474Z"/><path d="M4.75 3.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V9A.75.75 0 0 1 14 9v2.25A2.75 2.75 0 0 1 11.25 14h-6.5A2.75 2.75 0 0 1 2 11.25v-6.5A2.75 2.75 0 0 1 4.75 2H7a.75.75 0 0 1 0 1.5H4.75Z"/></svg>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-if="facultePaginate?.meta?.links" class="flex justify-end gap-1 px-6 py-3 border-t border-white/[0.05]">
              <span v-for="link in facultePaginate.meta.links" :key="link.label" @click="changePageForFac(link)" v-html="link.label"
                class="inline-flex items-center justify-center min-w-[28px] h-7 px-2 rounded-lg text-[12px] cursor-pointer transition-colors"
                :class="{ 'bg-[#4f8ef7]/20 text-[#7aaeff] border border-[#4f8ef7]/25': link.active, 'text-[#3d4d62] pointer-events-none': !link.url, 'text-[#7c83a0] hover:bg-white/[0.05]': link.url && !link.active }"
              />
            </div>
          </div>
        </div>

        <!-- TAB: Années -->
        <div v-show="activeTab === 'annees'">
          <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden">
            <div class="flex items-center justify-between px-6 py-4 border-b border-white/[0.07]">
              <div>
                <h2 class="text-[14px] font-semibold text-[#e8eaf0]">Années Académiques</h2>
                <p class="text-[12px] text-[#7c83a0] mt-0.5">Définissez les périodes scolaires actives</p>
              </div>
              <button @click="yearModalShow" class="inline-flex items-center gap-2 px-3.5 py-2 bg-[#4f8ef7]/15 text-[#7aaeff] border border-[#4f8ef7]/25 rounded-xl text-[12px] font-medium hover:bg-[#4f8ef7]/25 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5"><path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"/></svg>
                Ajouter
              </button>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-[13px]">
                <thead>
                  <tr class="border-b border-white/[0.05] bg-[#0d1117]/60">
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Début</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Fin</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Année Académique</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Statut</th>
                    <th class="px-6 py-3 text-right text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-white/[0.04]">
                  <tr v-if="!annee_paginate.data || annee_paginate.data.length === 0">
                    <td colspan="5" class="px-6 py-12 text-center">
                      <div class="flex flex-col items-center gap-2 text-[#3d4d62]">
                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.3" class="w-10 h-10 opacity-30"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
                        <span class="text-[12px]">Aucune année académique</span>
                      </div>
                    </td>
                  </tr>
                  <tr v-else v-for="anne in annee_paginate.data" :key="anne.id" class="hover:bg-white/[0.02] transition-colors">
                    <td class="px-6 py-3 text-[#7c83a0]">{{ anne.date_debut }}</td>
                    <td class="px-6 py-3 text-[#7c83a0]">{{ anne.date_fin }}</td>
                    <td class="px-6 py-3 font-medium text-[#c9d1d9]">{{ anne.annee_academique }}</td>
                    <td class="px-6 py-3">
                      <span v-if="anne.status == 1" class="inline-flex items-center gap-1.5 text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Actif
                      </span>
                      <span v-else class="inline-flex items-center gap-1.5 text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-white/[0.05] text-[#7c83a0] border border-white/[0.08]">
                        <span class="w-1.5 h-1.5 rounded-full bg-[#7c83a0]"></span> Inactif
                      </span>
                    </td>
                    <td class="px-6 py-3 text-right" :data-set="anne.id" @click="actionsOnClasse">
                      <button id="delete_year" class="inline-flex items-center justify-center w-7 h-7 rounded-lg hover:bg-red-500/10 text-[#3d4d62] hover:text-red-400 transition-colors mr-1">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 pointer-events-none"><path fill-rule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Z" clip-rule="evenodd"/></svg>
                      </button>
                      <button id="edit_year" class="inline-flex items-center justify-center w-7 h-7 rounded-lg hover:bg-amber-500/10 text-[#3d4d62] hover:text-amber-400 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 pointer-events-none"><path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.848 2.047a.75.75 0 0 0 .98.98l2.047-.848a2.75 2.75 0 0 0 .892-.596l4.261-4.262a1.75 1.75 0 0 0 0-2.474Z"/><path d="M4.75 3.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V9A.75.75 0 0 1 14 9v2.25A2.75 2.75 0 0 1 11.25 14h-6.5A2.75 2.75 0 0 1 2 11.25v-6.5A2.75 2.75 0 0 1 4.75 2H7a.75.75 0 0 1 0 1.5H4.75Z"/></svg>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-if="annee_paginate?.meta?.links" class="flex justify-end gap-1 px-6 py-3 border-t border-white/[0.05]">
              <span v-for="link in annee_paginate.meta.links" :key="link.label" @click="changePageForYear(link)" v-html="link.label"
                class="inline-flex items-center justify-center min-w-[28px] h-7 px-2 rounded-lg text-[12px] cursor-pointer transition-colors"
                :class="{ 'bg-[#4f8ef7]/20 text-[#7aaeff] border border-[#4f8ef7]/25': link.active, 'text-[#3d4d62] pointer-events-none': !link.url, 'text-[#7c83a0] hover:bg-white/[0.05]': link.url && !link.active }"
              />
            </div>
          </div>
        </div>

        <!-- TAB: Classes -->
        <div v-show="activeTab === 'classes'">
          <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden">
            <div class="flex items-center justify-between px-6 py-4 border-b border-white/[0.07]">
              <div>
                <h2 class="text-[14px] font-semibold text-[#e8eaf0]">Classes</h2>
                <p class="text-[12px] text-[#7c83a0] mt-0.5">Organisez les classes par cycle</p>
              </div>
              <button @click="niveauModalShow" class="inline-flex items-center gap-2 px-3.5 py-2 bg-[#4f8ef7]/15 text-[#7aaeff] border border-[#4f8ef7]/25 rounded-xl text-[12px] font-medium hover:bg-[#4f8ef7]/25 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5"><path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"/></svg>
                Ajouter
              </button>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-[13px]">
                <thead>
                  <tr class="border-b border-white/[0.05] bg-[#0d1117]/60">
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Cycle / Niveau</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Classe</th>
                    <th class="px-6 py-3 text-right text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-white/[0.04]">
                  <tr v-if="!classeParams.data || classeParams.data.length === 0">
                    <td colspan="3" class="px-6 py-12 text-center">
                      <div class="flex flex-col items-center gap-2 text-[#3d4d62]">
                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.3" class="w-10 h-10 opacity-30"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                        <span class="text-[12px]">Aucune classe enregistrée</span>
                      </div>
                    </td>
                  </tr>
                  <tr v-else v-for="cls in classeParams.data" :key="cls.id" class="hover:bg-white/[0.02] transition-colors">
                    <td class="px-6 py-3">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-violet-500/10 text-violet-400 border border-violet-500/20">{{ cls.niveau }}</span>
                    </td>
                    <td class="px-6 py-3 font-medium text-[#c9d1d9]">{{ cls.nom_classe }}</td>
                    <td class="px-6 py-3 text-right" :data-set="cls.id" @click="actionsOnClasse">
                      <button id="delete_classe" class="inline-flex items-center justify-center w-7 h-7 rounded-lg hover:bg-red-500/10 text-[#3d4d62] hover:text-red-400 transition-colors mr-1">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 pointer-events-none"><path fill-rule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Z" clip-rule="evenodd"/></svg>
                      </button>
                      <button id="edit_classe" class="inline-flex items-center justify-center w-7 h-7 rounded-lg hover:bg-amber-500/10 text-[#3d4d62] hover:text-amber-400 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 pointer-events-none"><path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.848 2.047a.75.75 0 0 0 .98.98l2.047-.848a2.75 2.75 0 0 0 .892-.596l4.261-4.262a1.75 1.75 0 0 0 0-2.474Z"/><path d="M4.75 3.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V9A.75.75 0 0 1 14 9v2.25A2.75 2.75 0 0 1 11.25 14h-6.5A2.75 2.75 0 0 1 2 11.25v-6.5A2.75 2.75 0 0 1 4.75 2H7a.75.75 0 0 1 0 1.5H4.75Z"/></svg>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="px-6 py-3 border-t border-white/[0.05]">
              <Pagination :meta="classeParams.meta" @change-page="getClasses" />
            </div>
          </div>
        </div>

        <!-- TAB: Paiements -->
        <div v-show="activeTab === 'paiements'">
          <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden">
            <div class="flex items-center justify-between px-6 py-4 border-b border-white/[0.07]">
              <div>
                <h2 class="text-[14px] font-semibold text-[#e8eaf0]">Paramètres des Paiements</h2>
                <p class="text-[12px] text-[#7c83a0] mt-0.5">Montants, échéances et devises par classe</p>
              </div>
              <button @click="paymentParamsModalShow" class="inline-flex items-center gap-2 px-3.5 py-2 bg-[#4f8ef7]/15 text-[#7aaeff] border border-[#4f8ef7]/25 rounded-xl text-[12px] font-medium hover:bg-[#4f8ef7]/25 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5"><path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"/></svg>
                Ajouter
              </button>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-[13px]">
                <thead>
                  <tr class="border-b border-white/[0.05] bg-[#0d1117]/60">
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Montant</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Cycle</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Classe</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Paiement par</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Année A.</th>
                    <th class="px-6 py-3 text-right text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-white/[0.04]">
                  <tr v-if="!paimentParams.data || paimentParams.data.length === 0">
                    <td colspan="6" class="px-6 py-12 text-center">
                      <div class="flex flex-col items-center gap-2 text-[#3d4d62]">
                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.3" class="w-10 h-10 opacity-30"><rect x="1" y="4" width="22" height="16" rx="2"/><path d="M1 10h22"/></svg>
                        <span class="text-[12px]">Aucun paramètre de paiement</span>
                      </div>
                    </td>
                  </tr>
                  <tr v-else v-for="pp in paimentParams.data" :key="pp.id" class="hover:bg-white/[0.02] transition-colors">
                    <td class="px-6 py-3">
                      <span v-if="pp.echeance == 'mois'" class="font-semibold text-[#c9d1d9] font-mono">
                        {{ pp.montant }} <span class="text-[11px] font-normal text-[#7c83a0]">{{ pp.devise }}</span>
                      </span>
                      <span v-else class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Versements</span>
                    </td>
                    <td class="px-6 py-3">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-violet-500/10 text-violet-400 border border-violet-500/20">{{ pp.niveau_name }}</span>
                    </td>
                    <td class="px-6 py-3 font-medium text-[#c9d1d9]">{{ pp.classe }}</td>
                    <td class="px-6 py-3">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-sky-500/10 text-sky-400 border border-sky-500/20">{{ pp.echeance }}</span>
                    </td>
                    <td class="px-6 py-3 text-[#7c83a0]">{{ pp.anneeAc }}</td>
                    <td class="px-6 py-3 text-right" :data-set="pp.id" @click="actionsOnClasse">
                      <button id="delete_paiement" class="inline-flex items-center justify-center w-7 h-7 rounded-lg hover:bg-red-500/10 text-[#3d4d62] hover:text-red-400 transition-colors mr-1">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 pointer-events-none"><path fill-rule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Z" clip-rule="evenodd"/></svg>
                      </button>
                      <button id="edit_paiement" class="inline-flex items-center justify-center w-7 h-7 rounded-lg hover:bg-amber-500/10 text-[#3d4d62] hover:text-amber-400 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 pointer-events-none"><path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.848 2.047a.75.75 0 0 0 .98.98l2.047-.848a2.75 2.75 0 0 0 .892-.596l4.261-4.262a1.75 1.75 0 0 0 0-2.474Z"/><path d="M4.75 3.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V9A.75.75 0 0 1 14 9v2.25A2.75 2.75 0 0 1 11.25 14h-6.5A2.75 2.75 0 0 1 2 11.25v-6.5A2.75 2.75 0 0 1 4.75 2H7a.75.75 0 0 1 0 1.5H4.75Z"/></svg>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="px-6 py-3 border-t border-white/[0.05]">
              <Pagination :meta="paimentParams.meta" @change-page="getPaymentParams" />
            </div>
          </div>
        </div>

        <!-- TAB: Frais -->
        <div v-show="activeTab === 'frais'">
          <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden">
            <div class="flex items-center justify-between px-6 py-4 border-b border-white/[0.07]">
              <div>
                <h2 class="text-[14px] font-semibold text-[#e8eaf0]">Frais d'inscription</h2>
                <p class="text-[12px] text-[#7c83a0] mt-0.5">Tarifs d'inscription par cycle et année</p>
              </div>
              <button @click="fraisModalShow" class="inline-flex items-center gap-2 px-3.5 py-2 bg-[#4f8ef7]/15 text-[#7aaeff] border border-[#4f8ef7]/25 rounded-xl text-[12px] font-medium hover:bg-[#4f8ef7]/25 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5"><path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"/></svg>
                Ajouter
              </button>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-[13px]">
                <thead>
                  <tr class="border-b border-white/[0.05] bg-[#0d1117]/60">
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Cycle</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Année Académique</th>
                    <th class="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Prix</th>
                    <th class="px-6 py-3 text-right text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-white/[0.04]">
                  <tr v-if="!frais_paginate || frais_paginate.length === 0">
                    <td colspan="4" class="px-6 py-12 text-center">
                      <div class="flex flex-col items-center gap-2 text-[#3d4d62]">
                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.3" class="w-10 h-10 opacity-30"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                        <span class="text-[12px]">Aucun frais d'inscription</span>
                      </div>
                    </td>
                  </tr>
                  <tr v-else v-for="f in frais_paginate" :key="f.id" class="hover:bg-white/[0.02] transition-colors">
                    <td class="px-6 py-3">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-violet-500/10 text-violet-400 border border-violet-500/20">{{ f.niveau }}</span>
                    </td>
                    <td class="px-6 py-3 text-[#7c83a0]">{{ f.annee_academique }}</td>
                    <td class="px-6 py-3 font-semibold text-[#c9d1d9] font-mono">{{ f.prix }}</td>
                    <td class="px-6 py-3 text-right">
                      <button class="inline-flex items-center justify-center w-7 h-7 rounded-lg hover:bg-red-500/10 text-[#3d4d62] hover:text-red-400 transition-colors mr-1">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5"><path fill-rule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Z" clip-rule="evenodd"/></svg>
                      </button>
                      <button @click="editFrais(f)" class="inline-flex items-center justify-center w-7 h-7 rounded-lg hover:bg-amber-500/10 text-[#3d4d62] hover:text-amber-400 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5"><path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.848 2.047a.75.75 0 0 0 .98.98l2.047-.848a2.75 2.75 0 0 0 .892-.596l4.261-4.262a1.75 1.75 0 0 0 0-2.474Z"/><path d="M4.75 3.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V9A.75.75 0 0 1 14 9v2.25A2.75 2.75 0 0 1 11.25 14h-6.5A2.75 2.75 0 0 1 2 11.25v-6.5A2.75 2.75 0 0 1 4.75 2H7a.75.75 0 0 1 0 1.5H4.75Z"/></svg>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- ══════════════════════ MODALS ══════════════════════ -->

    <!-- Modal: Faculté -->
    <StyleModal :show="faculte_profession" @close="facModalClose">
      <template #title>
        <h5 class="text-[#e8eaf0] font-semibold">Facultés / Profession</h5>
        <button type="button" class="btn-close" @click="facModalClose"></button>
      </template>
      <template #content>
        <form @submit.prevent="submitFac" class="space-y-4">
          <div>
            <InputLabel for="nom" value="Domaine d'étude" class="text-[#7c83a0]" />
            <TextInput id="nom" v-model="form.nom" type="text" class="mt-1 block w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" autofocus />
            <InputError class="mt-1" :message="form.errors.nom" />
          </div>
          <div>
            <InputLabel for="nb_annee" value="Nbre de sessions" class="text-[#7c83a0]" />
            <TextInput id="nb_annee" v-model="form.nb_annee" type="text" class="mt-1 block w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" />
            <InputError class="mt-1" :message="form.errors.nb_annee" />
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <DangerButton type="button" @click="facModalClose">Fermer</DangerButton>
            <PrimaryButton type="submit">{{ changeButton ? 'Modifier' : 'Enregistrer' }}</PrimaryButton>
          </div>
        </form>
      </template>
    </StyleModal>

    <!-- Modal: Année Académique -->
    <StyleModal :show="anneeAcademique" @close="yearModalClose">
      <template #title>
        <h5 class="text-[#e8eaf0] font-semibold">Année Académique</h5>
        <button type="button" class="btn-close" @click="yearModalClose"></button>
      </template>
      <template #content>
        <form @submit.prevent="submitYear" class="space-y-4">
          <div>
            <InputLabel for="date_debut" value="Début" class="text-[#7c83a0]" />
            <TextInput id="date_debut" v-model="formyear.date_debut" type="date" class="mt-1 block w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" autofocus />
            <InputError class="mt-1" :message="formyear.errors.date_debut" />
          </div>
          <div>
            <InputLabel for="date_fin" value="Fin" class="text-[#7c83a0]" />
            <TextInput id="date_fin" v-model="formyear.date_fin" type="date" class="mt-1 block w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" />
            <InputError class="mt-1" :message="formyear.errors.date_fin" />
          </div>
          <div>
            <InputLabel for="status" value="Statut" class="text-[#7c83a0]" />
            <select class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" v-model="formyear.status" id="status">
              <option value="" disabled>Choisir un statut</option>
              <option value="1">Actif</option>
              <option value="0">Inactif</option>
            </select>
            <InputError class="mt-1" :message="formyear.errors.status" />
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <DangerButton type="button" @click="yearModalClose">Fermer</DangerButton>
            <PrimaryButton type="submit">{{ changeButton ? 'Modifier' : 'Enregistrer' }}</PrimaryButton>
          </div>
        </form>
      </template>
    </StyleModal>

    <!-- Modal: Classe -->
    <StyleModal :show="niveau_detude_modal_classe" @close="niveauModalClose">
      <template #title>
        <h5 class="text-[#e8eaf0] font-semibold">Classe</h5>
        <button type="button" class="btn-close" @click="niveauModalClose"></button>
      </template>
      <template #content>
        <form @submit.prevent="submitNiveau" class="space-y-4">
          <div>
            <InputLabel for="Niveau" value="Cycle" class="text-[#7c83a0]" />
            <select class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" id="Niveau" v-model="formNiveau.niveau_id" @change="actionOnRadionButton($event)">
              <option value="" disabled selected>Cycle</option>
              <option v-for="niv in niveau" :value="niv.id" :key="niv.id">{{ niv.name }}</option>
            </select>
          </div>
          <div v-if="choseNiveau && choseNiveau.name == 'Universitaire'">
            <InputLabel for="faculte_id" value="Domaine d'étude" class="text-[#7c83a0]" />
            <select class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" v-model="formNiveau.faculte_id">
              <option value="" disabled selected>Domaine d'étude</option>
              <option v-for="fac in faculte" :key="fac.id" :value="fac.id">{{ fac.nom }}</option>
            </select>
          </div>
          <div>
            <InputLabel for="nom_classe" value="Classe" class="text-[#7c83a0]" />
            <TextInput id="nom_classe" v-model="formNiveau.nom_classe" type="text" class="mt-1 block w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" />
            <InputError class="mt-1" :message="formNiveau.errors.nom_classe" />
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <DangerButton type="button" @click="niveauModalClose">Fermer</DangerButton>
            <PrimaryButton type="submit">{{ changeButton ? 'Modifier' : 'Enregistrer' }}</PrimaryButton>
          </div>
        </form>
      </template>
    </StyleModal>

    <!-- Modal: Frais d'inscription -->
    <StyleModal :show="fraisModal" @close="fraisModalClose">
      <template #title>
        <h5 class="text-[#e8eaf0] font-semibold">Frais d'inscription</h5>
        <button type="button" class="btn-close" @click="fraisModalClose"></button>
      </template>
      <template #content>
        <form @submit.prevent="storeFraisDinscription" class="space-y-4">
          <div>
            <InputLabel for="niveau_id" value="Cycle" class="text-[#7c83a0]" />
            <select class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" v-model="formFrais.niveau_id" id="niveau_id">
              <option value="" disabled>Choisir un Cycle</option>
              <option v-for="niv in niveau" :key="niv.id" :value="niv.id">{{ niv.name }}</option>
            </select>
            <InputError class="mt-1" :message="formFrais.errors.niveau_id" />
          </div>
          <div>
            <InputLabel for="anneea_academique" value="Année Académique" class="text-[#7c83a0]" />
            <select class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" v-model="formFrais.anneeAc" id="anneea_academique">
              <option value="" disabled>Choisir l'année académique</option>
              <option v-for="a in anneeAcademiquePaginate.data" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
            </select>
            <InputError class="mt-1" :message="formFrais.errors.anneeAc" />
          </div>
          <div>
            <InputLabel for="Prix" value="Prix" class="text-[#7c83a0]" />
            <TextInput id="Prix" v-model="formFrais.prix" type="text" class="mt-1 block w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" autofocus />
            <InputError class="mt-1" :message="formFrais.errors.prix" />
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <DangerButton type="button" @click="fraisModalClose">Fermer</DangerButton>
            <PrimaryButton type="submit">{{ changeButton ? 'Modifier' : 'Enregistrer' }}</PrimaryButton>
          </div>
        </form>
      </template>
    </StyleModal>

    <!-- Modal: Paramètres des Examens -->
    <StyleModal :show="exam_params" @close="examParamsModalClose">
      <template #title>
        <h5 class="text-[#e8eaf0] font-semibold">Paramètres des Examens</h5>
        <button type="button" class="btn-close" @click="examParamsModalClose"></button>
      </template>
      <template #content>
        <form @submit.prevent="submitParamForExam" class="space-y-4">
          <div>
            <InputLabel for="evaluation" value="Évaluation / Examen par" class="text-[#7c83a0]" />
            <select class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" v-model="formExamParam.evaluation_par" id="evaluation">
              <option value="" disabled>Méthode d'évaluation</option>
              <option value="mois">Mois</option>
              <option value="session">Session</option>
              <option value="semestre">Semestre</option>
              <option value="Trimestre">Trimestre</option>
              <option value="Controle">Contrôle</option>
            </select>
            <InputError class="mt-1" :message="formExamParam.errors.evaluation_par" />
          </div>
          <div>
            <InputLabel for="anneea_academique" value="Année Académique" class="text-[#7c83a0]" />
            <select class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" v-model="formExamParam.annee_academique_id" id="anneea_academique">
              <option value="" disabled>Choisir l'année académique</option>
              <option v-for="a in anneeAcademiquePaginate.data" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
            </select>
            <InputError class="mt-1" :message="formExamParam.errors.annee_academique_id" />
          </div>
          <div>
            <InputLabel for="niveau_id" value="Cycle" class="text-[#7c83a0]" />
            <select class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" v-model="formExamParam.niveau_id" id="niveau_id">
              <option value="" disabled>Cycle</option>
              <option v-for="niv in niveau" :key="niv.id" :value="niv.id">{{ niv.name }}</option>
            </select>
            <InputError class="mt-1" :message="formExamParam.errors.niveau_id" />
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <DangerButton type="button" @click="examParamsModalClose">Fermer</DangerButton>
            <PrimaryButton type="submit">{{ changeButton ? 'Modifier' : 'Enregistrer' }}</PrimaryButton>
          </div>
        </form>
      </template>
    </StyleModal>

    <!-- Modal: Paramètres des Paiements -->
    <StyleModal :show="Payment_params_show" @close="paymentParamsModalClose">
      <template #title>
        <h5 class="text-[#e8eaf0] font-semibold">Paramètres des paiements</h5>
        <button type="button" class="btn-close" @click="paymentParamsModalClose"></button>
      </template>
      <template #content>
        <p v-if="Object.keys(paymentFormParams.errors).length > 0"
          class="mb-3 text-[12px] text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
          {{ paymentFormParams.errors }}
        </p>
        <form @submit.prevent="submitPaymentParams" class="space-y-4">
          <div>
            <InputLabel for="niveau" value="Cycle" class="text-[#7c83a0]" />
            <select @change="actionOnRadionButton($event)" v-model="paymentFormParams.niveau_id" class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" id="niveau">
              <option value="" disabled>Choisir un cycle</option>
              <option v-for="niv in niveau" :key="niv.id" :value="niv.id">{{ niv.name }}</option>
            </select>
            <InputError class="mt-1" :message="paymentFormParams.errors.niveau_id" />
          </div>
          <div v-if="niveauUniver">
            <InputLabel for="faculte" value="Domaine d'étude" class="text-[#7c83a0]" />
            <select v-if="faculte.length > 0" v-model="paymentFormParams.faculte_id" class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" id="faculte">
              <option value="" disabled>Choisir une faculté</option>
              <option v-for="fac in faculte" :key="fac.id" :value="fac.id">{{ fac.nom }}</option>
            </select>
            <InputError class="mt-1" :message="paymentFormParams.errors.faculte_id" />
          </div>
          <div>
            <InputLabel for="classe" value="Classe" class="text-[#7c83a0]" />
            <select class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" id="classe" v-model="paymentFormParams.classe">
              <option value="">Choisir une classe</option>
              <option v-for="c in getClassesByNiveau(paymentFormParams.niveau_id)" :key="c.id" :value="c.id">{{ c.nom_classe }}</option>
            </select>
            <InputError class="mt-1" :message="paymentFormParams.errors.classe" />
          </div>
          <div>
            <InputLabel for="anneea_academique" value="Année Académique" class="text-[#7c83a0]" />
            <select class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" v-model="paymentFormParams.anneeAcademique" id="anneea_academique">
              <option value="" disabled>Choisir l'année académique</option>
              <option v-for="a in anneeAcademiquePaginate.data" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
            </select>
            <InputError class="mt-1" :message="paymentFormParams.errors.anneeAcademique" />
          </div>
          <div class="flex gap-4">
            <div class="flex-1">
              <InputLabel for="echeance" value="Payer par:" class="text-[#7c83a0]" />
              <select class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" v-model="paymentFormParams.echeance" @change="changeEcheance" id="echeance">
                <option value="" disabled>Choisir</option>
                <option value="mois">Mois</option>
                <option value="Controle">Contrôle</option>
                <option value="Trimestre">Trimestre</option>
                <option value="Versement">Versement</option>
                <option value="Session">Session</option>
              </select>
              <InputError class="mt-1" :message="paymentFormParams.errors.echeance" />
            </div>
            <div class="flex-1">
              <InputLabel for="nb_echeance" :value="'Nbres de ' + echeance" class="text-[#7c83a0]" />
              <select @change="GenereVersementInput" :disabled="echeance === 'mois'" class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" v-model="paymentFormParams.nb_echeance" id="nb_echeance">
                <option v-if="echeance == 'mois'" selected value="9">9 mois</option>
                <option v-for="n in [1,2,3,4,5]" :key="n" :value="n">{{ n }}</option>
              </select>
              <InputError class="mt-1" :message="paymentFormParams.errors.nb_echeance" />
            </div>
          </div>
          <div v-if="echeance !== 'mois'">
            <div class="flex flex-wrap gap-3">
              <template v-if="editMontantPar">
                <div v-for="(value, key, index) in paymentFormParams.montant_par" :key="index" class="flex-1 min-w-[100px]">
                  <InputLabel :for="echeance + (index + 1)" :value="echeance + ' ' + (index + 1)" class="text-[#7c83a0]" />
                  <TextInput :id="echeance + (index + 1)" type="text" v-model="paymentFormParams.montant_par[key]" class="mt-1 block w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" />
                </div>
              </template>
              <template v-else>
                <div v-for="(_, index) in nbControleOrVersementOrtrimestre" :key="index" class="flex-1 min-w-[100px]">
                  <InputLabel :for="echeance + (index + 1)" :value="echeance + ' ' + (index + 1)" class="text-[#7c83a0]" />
                  <TextInput :id="echeance + (index + 1)" type="text" v-model="paymentFormParams.montant_par[`${echeance}_${index + 1}_${paymentFormParams.anneeAcademique}`]" class="mt-1 block w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" />
                </div>
              </template>
            </div>
            <InputError class="mt-1" :message="paymentFormParams.errors.montant_par" />
          </div>
          <!-- Accessoires -->
          <div>
            <h3 class="text-[13px] font-semibold text-[#c9d1d9] mb-2">Accessoires</h3>
            <div v-for="(acc, index) in accessoires" :key="index" class="flex gap-3 items-center mb-2">
              <select v-model="acc.type_daccessoire" class="select flex-1 bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]">
                <option value="" disabled>Type</option>
                <option v-for="type in accessoireTypes" :key="type" :value="type">{{ type }}</option>
              </select>
              <input v-model="acc.prix" type="text" placeholder="Prix" class="input-normal flex-1 bg-[#0d1117] border border-white/[0.1] text-[#e8eaf0] rounded-lg px-3 py-2 text-[13px] focus:outline-none focus:border-[#4f8ef7]/40" />
              <button type="button" @click="removeAccessoire(index)" class="text-[#3d4d62] hover:text-red-400 transition-colors text-[12px] whitespace-nowrap">Retirer</button>
            </div>
            <button type="button" @click="addAccessoire" class="inline-flex items-center gap-1.5 text-[12px] text-[#7aaeff] hover:text-[#4f8ef7] font-medium transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5"><path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"/></svg>
              Ajouter un accessoire
            </button>
          </div>
          <div class="flex gap-4">
            <div class="flex-1">
              <InputLabel for="devise" value="Devise" class="text-[#7c83a0]" />
              <select class="select mt-1 w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" id="devise" v-model="paymentFormParams.devise">
                <option value="" disabled>Choisir</option>
                <option value="GDES">GDES</option>
                <option value="$HT">$HT</option>
                <option value="USD">USD</option>
              </select>
              <InputError class="mt-1" :message="paymentFormParams.errors.devise" />
            </div>
            <div v-if="echeance == 'mois'" class="flex-1">
              <InputLabel for="montant" value="Montant" class="text-[#7c83a0]" />
              <TextInput id="montant" v-model="paymentFormParams.montant" type="text" class="mt-1 block w-full bg-[#0d1117] border-white/[0.1] text-[#e8eaf0]" />
              <InputError class="mt-1" :message="paymentFormParams.errors.montant" />
            </div>
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <DangerButton type="button" @click="paymentParamsModalClose">Fermer</DangerButton>
            <PrimaryButton type="submit">{{ changeButton ? 'Modifier' : 'Enregistrer' }}</PrimaryButton>
          </div>
        </form>
      </template>
    </StyleModal>

  </div>
</template>
