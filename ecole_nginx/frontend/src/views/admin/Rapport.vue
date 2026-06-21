<template>
  <div
    class="min-h-screen animate-[fadeUp_0.4s_ease_both]"
    style="background: #0f1117; font-family: 'DM Sans', 'Segoe UI', sans-serif;"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

      <!-- ── Page Header ── -->
      <div class="mb-6">
        <h1 class="text-[22px] font-bold text-[#e8eaf0] tracking-tight">Rapports</h1>
        <p class="text-[13px] text-[#7c83a0] mt-0.5">Générez et imprimez vos rapports académiques</p>
      </div>

      <!-- ── Row 1: Global + Financier ── -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">

        <!-- Rapport Global -->
        <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden">
          <div class="flex items-center gap-3 px-5 py-4 border-b border-white/[0.07]">
            <span class="flex items-center justify-center w-8 h-8 rounded-xl bg-[#4f8ef7]/10 text-[#7aaeff] text-[16px]">📊</span>
            <div>
              <h2 class="text-[14px] font-semibold text-[#e8eaf0]">Rapport Global</h2>
              <p class="text-[11px] text-[#7c83a0]">Vue d'ensemble des données</p>
            </div>
          </div>
          <div class="px-5 py-4 space-y-3">
            <div>
              <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Type de rapport</label>
              <select v-model="forms.global.type" class="dark-select">
                <option value="" disabled>Choisir le type</option>
                <option value="Global">Global</option>
                <option value="Livres">Livres</option>
                <option value="Tissus">Tissus</option>
                <option value="Fournitures">Fournitures</option>
                <option value="Arriéré">Arriéré</option>
                <option value="Dépense">Dépense</option>
              </select>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Début</label>
                <input type="date" v-model="forms.global.date_debut" class="dark-input" />
              </div>
              <div>
                <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Fin</label>
                <input type="date" v-model="forms.global.date_fin" class="dark-input" />
              </div>
            </div>
            <div class="flex justify-end gap-2 pt-1">
              <button @click="submitExcel('/export-excel-global', forms.global, 'rapport_global.xlsx')" class="excel-btn" :disabled="excel_loading['/export-excel-global']">
                <svg v-if="excel_loading['/export-excel-global']" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8"><path d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/></svg>
                Excel
              </button>
              <button @click="submitPdf('/print-global-repport', forms.global)" class="print-btn" :disabled="error_loading['/print-global-repport'] == true">
                <span v-if="error_loading['/print-global-repport']">Waiting…</span>
                <span v-else class="inline-flex items-center gap-1.5">
                  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5"><path d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm1-4h4v4H10v-4z"/></svg>
                  Imprimer
                </span>
              </button>
            </div>
          </div>
        </div>

        <!-- Rapport Financier -->
        <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden">
          <div class="flex items-center gap-3 px-5 py-4 border-b border-white/[0.07]">
            <span class="flex items-center justify-center w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-400 text-[16px]">💰</span>
            <div>
              <h2 class="text-[14px] font-semibold text-[#e8eaf0]">Rapports Financiers</h2>
              <p class="text-[11px] text-[#7c83a0]">Paiements et versements des élèves</p>
            </div>
          </div>
          <div class="px-5 py-4 space-y-3">
            <div>
              <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Classe</label>
              <select v-model="forms.payment.classe" class="dark-select">
                <option value="All">Toutes les classes</option>
                <option v-for="c in classes" :key="c.id" :value="c.nom_classe">{{ c.nom_classe }}</option>
              </select>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Année Académique</label>
              <select v-model="forms.payment.date_debut" class="dark-select">
                <option value="" disabled>Choisir une Année</option>
                <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
              </select>
            </div>
            <input type="date" v-model="forms.payment.date_fin" class="dark-input hidden" />
            <div>
              <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Versement</label>
              <select v-model="forms.payment.versement" class="dark-select">
                <option value="tous les Versements">Tous les Versements</option>
                <option v-for="v in versements" :key="v" :value="v">{{ v }}</option>
              </select>
            </div>
            <div class="flex justify-end gap-2 pt-1">
              <button @click="submitExcel('/export-excel-paiement', forms.payment, 'rapport_paiement.xlsx')" class="excel-btn" :disabled="excel_loading['/export-excel-paiement']">
                <svg v-if="excel_loading['/export-excel-paiement']" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8"><path d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/></svg>
                Excel
              </button>
              <button @click="submitPdf('/print-rapport-paiement', forms.payment)" class="print-btn" :disabled="error_loading['/print-rapport-paiement'] == true">
                <span v-if="error_loading['/print-rapport-paiement']">Waiting…</span>
                <span v-else class="inline-flex items-center gap-1.5">
                  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5"><path d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm1-4h4v4H10v-4z"/></svg>
                  Imprimer
                </span>
              </button>
            </div>
          </div>
        </div>

      </div>

      <!-- ── Row 2: Pédagogique ── -->
      <div class="grid grid-cols-1 gap-4 mb-4">
        <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden">
          <div class="flex items-center gap-3 px-5 py-4 border-b border-white/[0.07]">
            <span class="flex items-center justify-center w-8 h-8 rounded-xl bg-violet-500/10 text-violet-400 text-[16px]">🎓</span>
            <div>
              <h2 class="text-[14px] font-semibold text-[#e8eaf0]">Rapports Pédagogiques</h2>
              <p class="text-[11px] text-[#7c83a0]">Évaluations mensuelles et annuelles</p>
            </div>
          </div>
          <div class="px-5 py-4">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
              <div>
                <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Cycle</label>
                <select v-model="forms.pedago.cycle" class="dark-select">
                  <option value="All">Tous les Cycles</option>
                  <option v-for="n in niveau" :key="n.id" :value="n.id">{{ n.name }}</option>
                </select>
              </div>
              <div>
                <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Classe</label>
                <select v-model="forms.pedago.classe" class="dark-select">
                  <option value="" disabled>Choisir Classe</option>
                  <option value="Toutes les classes">Toutes les classes</option>
                  <option v-for="cls in getClassesByNiveau(forms.pedago.cycle)" :key="cls.id" :value="cls.id">
                    {{ cls.nom_classe }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Année Académique</label>
                <select v-model="forms.pedago.annee_ac" class="dark-select">
                  <option value="" disabled>Choisir une Année</option>
                  <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
                </select>
              </div>
              <div>
                <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Mois</label>
                <select v-model="forms.pedago.mois" class="dark-select">
                  <option value="" disabled>Choisir le mois</option>
                  <option value="Tous les mois">Tous les mois</option>
                  <option v-for="m in mois_" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>
            </div>
            <div class="flex items-center justify-between mt-4 pt-3 border-t border-white/[0.05]">
              <label class="flex items-center gap-2.5 cursor-pointer group">
                <div class="relative">
                  <input type="checkbox" v-model="forms.pedago.identifiant" class="sr-only peer" />
                  <div class="w-9 h-5 bg-white/[0.07] peer-checked:bg-[#4f8ef7]/70 rounded-full transition-colors duration-200 border border-white/[0.1] peer-checked:border-[#4f8ef7]/40"></div>
                  <div class="absolute top-0.5 left-0.5 w-4 h-4 bg-[#7c83a0] peer-checked:bg-white rounded-full transition-all duration-200 peer-checked:translate-x-4"></div>
                </div>
                <span class="text-[12px] text-[#7c83a0] group-hover:text-[#c0c7d8] transition-colors">Avec Identifiant</span>
              </label>
              <div class="flex items-center gap-2">
                <button @click="submitExcel('/export-excel-pedagogique', forms.pedago, 'rapport_pedagogique.xlsx')" class="excel-btn" :disabled="excel_loading['/export-excel-pedagogique']">
                  <svg v-if="excel_loading['/export-excel-pedagogique']" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                  <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8"><path d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/></svg>
                  Excel
                </button>
                <button @click="submitPdf('/print-repport-pedagogique', forms.pedago)" class="print-btn">
                  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5"><path d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm1-4h4v4H10v-4z"/></svg>
                  Imprimer
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Row 3: Administratif + Disciplinaire ── -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

        <!-- Rapport Administratif -->
        <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden">
          <div class="flex items-center gap-3 px-5 py-4 border-b border-white/[0.07]">
            <span class="flex items-center justify-center w-8 h-8 rounded-xl bg-amber-500/10 text-amber-400 text-[16px]">📂</span>
            <div>
              <h2 class="text-[14px] font-semibold text-[#e8eaf0]">Rapports Administratifs</h2>
              <p class="text-[11px] text-[#7c83a0]">Registres et présences</p>
            </div>
          </div>
          <div class="px-5 py-4 space-y-4">

            <!-- Inscription -->
            <div>
              <p class="text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider mb-2.5 flex items-center gap-2">
                <span class="w-1 h-3 rounded-full bg-amber-400/60 inline-block"></span>
                Inscription des élèves
              </p>
              <div class="space-y-2.5">
                <div class="grid grid-cols-2 gap-2">
                  <div>
                    <label class="block text-[10px] text-[#7c83a0] mb-1">Cycle</label>
                    <select v-model="forms.admin.cycle" class="dark-select text-[12px]">
                      <option value="All">Tous Cycles</option>
                      <option v-for="n in niveau" :key="n.id" :value="n.id">{{ n.name }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-[10px] text-[#7c83a0] mb-1">Classe</label>
                    <select v-model="forms.admin.classe" class="dark-select text-[12px]">
                      <option value="All">Toutes classes</option>
                      <option v-for="cls in getClassesByNiveau(forms.admin.cycle)" :key="cls.id" :value="cls.id">
                        {{ cls.nom_classe }}
                      </option>
                    </select>
                  </div>
                </div>
                <div>
                  <label class="block text-[10px] text-[#7c83a0] mb-1">Année Académique</label>
                  <select v-model="forms.admin.annee_ac" class="dark-select">
                    <option value="" disabled>Choisir une Année</option>
                    <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
                  </select>
                </div>
                <div class="flex gap-2">
                  <button @click="submitExcel('/export-excel-register', forms.admin, 'registre_inscription.xlsx')" class="flex-1 flex items-center justify-center gap-2 py-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-xl text-[12px] font-medium hover:bg-emerald-500/20 transition-colors" :disabled="excel_loading['/export-excel-register']">
                    <svg v-if="excel_loading['/export-excel-register']" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                    <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8"><path d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/></svg>
                    Excel
                  </button>
                  <button @click="submitPdf('/print-repport-register', forms.admin)" class="flex-1 flex items-center justify-center gap-2 py-2 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-xl text-[12px] font-medium hover:bg-amber-500/20 transition-colors">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5"><path d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm1-4h4v4H10v-4z"/></svg>
                    Imprimer Registre
                  </button>
                </div>
              </div>
            </div>

            <!-- Divider -->
            <div class="h-px bg-white/[0.05]"></div>

            <!-- Présence -->
            <div>
              <p class="text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider mb-2.5 flex items-center gap-2">
                <span class="w-1 h-3 rounded-full bg-sky-400/60 inline-block"></span>
                Présence des élèves
              </p>
              <div class="space-y-2.5">
                <div class="grid grid-cols-2 gap-2">
                  <div>
                    <label class="block text-[10px] text-[#7c83a0] mb-1">Début</label>
                    <input type="date" v-model="forms.presence.date_debut" class="dark-input text-[12px]" />
                  </div>
                  <div>
                    <label class="block text-[10px] text-[#7c83a0] mb-1">Fin</label>
                    <input type="date" v-model="forms.presence.date_fin" class="dark-input text-[12px]" />
                  </div>
                </div>
                <button @click="submitPdf('/print-present-repport', forms.presence)" class="w-full flex items-center justify-center gap-2 py-2 bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded-xl text-[12px] font-medium hover:bg-sky-500/20 transition-colors">
                  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5"><path d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm1-4h4v4H10v-4z"/></svg>
                  Imprimer Présences
                </button>
              </div>
            </div>

          </div>
        </div>

        <!-- Rapport Disciplinaire -->
        <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden">
          <div class="flex items-center gap-3 px-5 py-4 border-b border-white/[0.07]">
            <span class="flex items-center justify-center w-8 h-8 rounded-xl bg-red-500/10 text-red-400 text-[16px]">🚨</span>
            <div>
              <h2 class="text-[14px] font-semibold text-[#e8eaf0]">Rapports Disciplinaires</h2>
              <p class="text-[11px] text-[#7c83a0]">Incidents, sanctions et comportements</p>
            </div>
          </div>
          <div class="px-5 py-4 flex flex-col gap-3">
            <!-- Items coming soon -->
            <div class="flex items-center gap-3 py-3 px-4 rounded-xl bg-white/[0.02] border border-white/[0.05]">
              <span class="w-1.5 h-1.5 rounded-full bg-[#3d4d62] flex-shrink-0"></span>
              <span class="text-[13px] text-[#7c83a0]">Rapport des incidents et sanctions</span>
              <span class="ml-auto text-[10px] font-medium px-2 py-0.5 rounded-full bg-white/[0.05] text-[#3d4d62] border border-white/[0.06]">Bientôt</span>
            </div>
            <div class="flex items-center gap-3 py-3 px-4 rounded-xl bg-white/[0.02] border border-white/[0.05]">
              <span class="w-1.5 h-1.5 rounded-full bg-[#3d4d62] flex-shrink-0"></span>
              <span class="text-[13px] text-[#7c83a0]">Rapport du comportement des élèves</span>
              <span class="ml-auto text-[10px] font-medium px-2 py-0.5 rounded-full bg-white/[0.05] text-[#3d4d62] border border-white/[0.06]">Bientôt</span>
            </div>
            <!-- Notice -->
            <div class="mt-2 flex items-start gap-3 p-4 bg-amber-500/5 border border-amber-500/15 rounded-xl">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-4 h-4 text-amber-400/70 flex-shrink-0 mt-0.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/></svg>
              <p class="text-[11px] text-amber-400/60 leading-relaxed">Ces modules sont en attente de données disciplinaires.</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  <AppToast :show="toast.show" :message="toast.message" :ok="toast.ok" />
  </div>
</template>

<script setup>
import { onMounted, reactive,ref } from 'vue';
import axios from 'axios';
import AppToast from '@/components/AppToast.vue';
import { useToast } from '@/composables/useToast';
const { toast, error } = useToast();

const baseUrl = import.meta.env.VITE_APP_BASE_URL || '';

const forms = reactive({
  global:   { type: '', date_debut: '', date_fin: '' },
  payment:  { classe: 'All', date_debut: '', date_fin: '', versement: 'tous les Versements' },
  pedago:   { cycle: 'All', classe: 'Toutes les classes', annee_ac: '', mois: '', identifiant: false },
  admin:    { cycle: 'All', classe: 'All', annee_ac: '', identifiant: false },
  presence: { date_debut: '', date_fin: '', classe: 'All' }
});

const versements = ["1er Versement", "2ème Versement", "3ème Versement", "4ème Versement"];
const mois_ = ["Septembre","Octobre","Novembre","Décembre","Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août"];

import { useSchoolStore } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';

const schoolStore = useSchoolStore();
const { niveau, annee, classes } = storeToRefs(schoolStore);

onMounted(() => {
  schoolStore.fetchAllDependencies();
});

const getClassesByNiveau = (niveauId) => {
  if (!niveauId || !classes.value) return [];
  return classes.value.filter(c => c.niveau_id === niveauId);
};

const error_loading    = ref({})
const excel_loading    = ref({})

const submitExcel = async (endpoint, data, filename) => {
  excel_loading.value[endpoint] = true
  try {
    const token = localStorage.getItem("auth-token")
    const response = await axios.post(`${baseUrl}${endpoint}`, data, {
      headers: {
        "Authorization": `Bearer ${token}`,
        "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      },
      responseType: 'blob'
    })
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || 'export.xlsx'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    setTimeout(() => window.URL.revokeObjectURL(url), 100)
  } catch (e) {
    error('Erreur lors de l\'export Excel', false)
  } finally {
    excel_loading.value[endpoint] = false
  }
}

const submitPdf = async (endpoint, data) => {
  try {
    error_loading.value[endpoint] = true
    const token = localStorage.getItem("auth-token");
    const response = await axios.post(`${baseUrl}${endpoint}`, data, {
      headers: {
        "Authorization": `Bearer ${token}`,
        "Accept": "application/pdf"
      },
      responseType: 'blob'
    });
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    error_loading.value[endpoint] = null
    window.open(url, '_blank');
    setTimeout(() => window.URL.revokeObjectURL(url), 100);
  } catch (e) {
    error_loading.value[endpoint] = null
    if (e.response?.data instanceof Blob) {
  const text = await e.response.data.text()
  const json = JSON.parse(text)

  if (json.errors) {
    // Boucle sur les erreurs et affiche chacune
    const messages = Object.values(json.errors).flat().join("\n")
    error(messages,false) // ton toast/notification d'erreur
  } else {
    error(json.message ?? 'Une erreur est survenue.',false)
  }
}
  //   if (error.response?.data instanceof Blob) {
  //     const text = await error.response.data.text()
  //     const json = JSON.parse(text)

  //     // if (error.response?.data?.detail) {
  //     //   throw error(response?.data?.detail ?? 'Email ou mot de passe incorrect.')
  //     // }
        
    
    
  //   console.log('Erreur détails:', json)
  //   console.log('Erreur validation:', json.errors.errors)
  // }
  }
};
</script>

<style scoped>
.dark-select {
  width: 100%;
  background: #0d1117;
  border: 1px solid rgba(255,255,255,0.08);
  color: #c9d1d9;
  border-radius: 7px;
  padding: 10px 10px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%237c83a0' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19.5 8.25l-7.5 7.5-7.5-7.5'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 14px;
  padding-right: 30px;
}
.dark-select:focus {
  border-color: rgba(79,142,247,0.35);
}
.dark-select option {
  background: #161b26;
  color: #c9d1d9;
}

.dark-input {
  width: 100%;
  background: #0d1117;
  border: 1px solid rgba(255,255,255,0.08);
  color: #c9d1d9;
  border-radius: 7px;
  padding: 10px 10px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}
.dark-input:focus {
  border-color: rgba(79,142,247,0.35);
}
.dark-input::-webkit-calendar-picker-indicator {
  filter: invert(0.5);
  cursor: pointer;
}

.excel-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  background: rgba(16,185,129,0.12);
  color: #34d399;
  border: 1px solid rgba(16,185,129,0.22);
  border-radius: 7px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.excel-btn:hover {
  background: rgba(16,185,129,0.22);
  border-color: rgba(16,185,129,0.35);
}
.excel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.print-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  background: rgba(79,142,247,0.12);
  color: #7aaeff;
  border: 1px solid rgba(79,142,247,0.22);
  border-radius: 7px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.print-btn:hover {
  background: rgba(79,142,247,0.22);
  border-color: rgba(79,142,247,0.35);
}
</style>
