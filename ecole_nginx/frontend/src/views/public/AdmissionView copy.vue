<template>
  <div>
    <!-- ══ HERO ══════════════════════════════════════════ -->
    <div class="relative overflow-hidden" style="height:58vh;min-height:280px">
      <img
        src="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1800&q=80"
        alt="Admission"
        class="hero-img w-full h-full object-cover block"
      />
      <div class="absolute inset-0" style="background:linear-gradient(135deg,rgba(26,122,110,.92),rgba(11,31,58,.75),rgba(212,168,83,.25))"></div>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <p class="text-xs font-bold mb-3" style="color:#fde68a;letter-spacing:.3em;text-transform:uppercase">Inscriptions {{ annee_global?.find(x=>x.status==1)?.annee_academique }}</p>
        <h1 class="font-serif text-white mb-4" style="font-size:clamp(2rem,4.5vw,3.8rem)">
          Demande d'<span class="text-gold">Admission</span>
        </h1>
        <p style="color:rgba(255,255,255,.8)" class="max-w-md leading-relaxed">
          Complétez votre dossier en ligne en quelques étapes. Traitement garanti sous 24h.
        </p>
      </div>
    </div>
<!-- {{ niveau_global }} -->
    <!-- ══ BARRE DE PROGRESSION ══════════════════════════ -->
    <div class="bg-white sticky top-16 z-40" style="box-shadow:0 2px 12px rgba(11,31,58,.07)">
      <div class="max-w-5xl mx-auto px-6 pt-5">
        <div class="flex items-center">
          <template v-for="(s, i) in ADM_STEPS" :key="i">
            <div class="flex flex-col items-center gap-1">
              <div class="step-circle" :class="step > i ? 'done' : step === i ? 'current' : 'todo'">
                <template v-if="step > i">
                  <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </template>
                <template v-else>{{ i + 1 }}</template>
              </div>
              <span
                class="text-xs font-semibold hidden sm:block"
                :class="step > i ? 'text-teal' : step === i ? 'text-gold' : 'text-gray-300'"
              >{{ s.l }}</span>
            </div>
            <div v-if="i < ADM_STEPS.length - 1" class="step-line" :class="step > i ? 'done' : 'todo'" style="margin-bottom:20px"></div>
          </template>
        </div>
        <div class="prog-bar mt-3">
          <div class="prog-fill" :style="{ width: (step / (ADM_STEPS.length - 1) * 100) + '%' }"></div>
        </div>
      </div>
      <div class="flex justify-around border-b-2 border-gray-50 px-6 max-w-4xl mx-auto mt-2 overflow-x-auto">
        <button
          v-for="(s, i) in ADM_STEPS"
          :key="i"
          class="tab-btn"
          :class="{ active: step === i }"
          @click="step = i"
        >{{ s.icon }} {{ s.l }}</button>
      </div>
    </div>

    <!-- ══ PANELS ═════════════════════════════════════════ -->
    <div class="max-w-5xl mx-auto px-6 pb-16">

      <!-- Succès -->
      <div v-if="done" class="mt-8 rounded-3xl py-16 px-10 text-center" style="background:linear-gradient(135deg,#1A7A6E,#0f5e54)">
        <div style="font-size:5rem" class="mb-4">🎉</div>
        <h2 class="font-serif text-white text-4xl mb-3">Dossier envoyé avec succès !</h2>
        <p class="mb-2 max-w-sm mx-auto" style="color:rgba(255,255,255,.8)">
          Notre équipe examinera votre candidature sous 24h et vous contactera par email.
        </p>
        <p class="mb-8 text-sm" style="color:rgba(255,255,255,.65)">
          Référence : <strong class="text-white">ADM-{{ admRef }}</strong>
        </p>
        <button class="btn-gold px-8 py-3.5 rounded-full font-semibold" @click="reset">Nouvelle candidature</button>
      </div>

      <!-- Étape 0 — Élève -->
      <div v-else-if="step === 0" class="bg-white rounded-3xl p-10 mt-8" style="box-shadow:0 16px 48px rgba(11,31,58,.12)">
        <div class="text-xs font-bold uppercase tracking-widest text-gold flex items-center gap-2.5 mb-5">
          <span class="w-5 h-0.5 bg-gold inline-block"></span> Informations sur l'élève
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div><label class="field-label">Nom *</label><input class="ifield" type="text" placeholder="Dupont" v-model="f.nom" /></div>
          <div><label class="field-label">Prénom *</label><input class="ifield" type="text" placeholder="Marie" v-model="f.prenom" /></div>
          <div><label class="field-label">Date de naissance *</label><input class="ifield" type="date" v-model="f.date_de_naissance" /></div>
          <div>
            <label class="field-label">Sexe *</label>
            <select class="ifield" v-model="f.sexe">
              <option value="">Choisir…</option>
              <option>Féminin</option><option>Masculin</option><option>Autre</option>
            </select>
          </div>
          <div><label class="field-label">Email *</label><input class="ifield" type="email" placeholder="marie@exemple.fr" v-model="f.email" /></div>
          <div><label class="field-label">Téléphone</label><input class="ifield" type="tel" placeholder="+33 6 00 00 00 00" v-model="f.telephone" /></div>
          <div class="sm:col-span-2"><label class="field-label">Adresse *</label><input class="ifield" type="text" placeholder="12 rue de la Paix, 75001 Paris" v-model="f.adresse" /></div>
        </div>

        <div class="text-xs font-bold uppercase tracking-widest text-gold flex items-center gap-2.5 mb-4 mt-7">
          <span class="w-5 h-0.5 bg-gold inline-block"></span> Formation souhaitée
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="field-label">Niveau visé *</label>
            <select class="ifield" v-model="f.niveau_id">
              <option value="">Choisir…</option>
              <option v-for="niveau in niveau_global" :value="niveau.id" :key="niveau.id">{{niveau.name}}</option> 
            </select>
          </div>
            <div>
            <label class="field-label">Classe *</label>
            <select class="ifield" v-model="f.classe_actuelle_id">
              <option value="">Choisir…</option>
              <option v-for="classe in classes_global" :value="classe.id" :key="classe.id">{{classe.nom_classe}}</option> 
            </select>
          </div>
<!-- niveau_global {{ niveau_global }} -->
           <div v-if="is_university">
            <label class="field-label">Faculté *</label>
            <select class="ifield" v-model="f.faculte_id">
              <option value="">Choisir…</option>
              <option v-for="faculte in faculte" :value="faculte.id" :key="faculte.id">{{faculte.nom}}</option> 
            </select>
          </div>
          <div>
            <label class="field-label">Année scolaire</label>
            <select class="ifield" v-model="f.annee_academique_id">
              <option value="" disabled="">Année Académique</option>
              <option v-for="value in annee_global" :key="value" value="value.id">{{ value.annee_academique }}</option>
            </select>
          </div>
          <div class="sm:col-span-2">
            <label class="field-label">Motif de candidature</label>
            <textarea class="ifield" rows="3" placeholder="Expliquez votre motivation…" v-model="f.motif"></textarea>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-6 mb-7">
          <div class="radio-card" :class="{ on: f.bourse }" @click="f.bourse = !f.bourse">
            <div class="rounded-full border-2 flex items-center justify-center flex-shrink-0" :class="f.bourse ? 'border-gold' : 'border-gray-300'" style="width:18px;height:18px">
              <div v-if="f.bourse" class="rounded-full bg-gold" style="width:9px;height:9px"></div>
            </div>
            <div>
              <div class="font-semibold text-sm">🎓 Demande de bourse</div>
              <div class="text-gray-400 text-xs mt-0.5">Joindre attestation dans les documents</div>
            </div>
          </div>
          <div class="radio-card" :class="{ on: f.handicap }" @click="f.handicap = !f.handicap">
            <div class="rounded-full border-2 flex items-center justify-center flex-shrink-0" :class="f.handicap ? 'border-gold' : 'border-gray-300'" style="width:18px;height:18px">
              <div v-if="f.handicap" class="rounded-full bg-gold" style="width:9px;height:9px"></div>
            </div>
            <div>
              <div class="font-semibold text-sm">♿ Besoin particulier</div>
              <div class="text-gray-400 text-xs mt-0.5">Aménagement pédagogique requis</div>
            </div>
          </div>
        </div>
        <div class="flex justify-end">
          <button class="btn-gold px-7 py-3 rounded-full font-semibold" @click="step = 1">Tuteur / Responsable →</button>
        </div>
      </div>

      <!-- Étape 1 — Tuteur -->
      <div v-else-if="step === 1" class="bg-white rounded-3xl p-10 mt-8" style="box-shadow:0 16px 48px rgba(11,31,58,.12)">
        <div class="text-xs font-bold uppercase tracking-widest text-gold flex items-center gap-2.5 mb-5">
          <span class="w-5 h-0.5 bg-gold inline-block"></span> Responsable légal
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="field-label">Lien de parenté *</label>
            <select class="ifield" v-model="f.relation_responsable">
              <option value="">Choisir…</option>
              <option>Père</option><option>Mère</option><option>Tuteur légal</option><option>Grand-parent</option><option>Autre</option>
            </select>
          </div>
          <div>
            <label class="field-label">Civilité</label>
            <select class="ifield" v-model="f.tCiv"><option>Madame</option><option>Monsieur</option></select>
          </div>
          <div><label class="field-label">Nom *</label><input class="ifield" type="text" placeholder="Dupont" v-model="f.nom_responsable" /></div>
          <div><label class="field-label">Prénom *</label><input class="ifield" type="text" placeholder="Jean" v-model="f.prenom_responsable" /></div>
          <div><label class="field-label">Téléphone *</label><input class="ifield" type="tel" v-model="f.tTel" /></div>
          <div><label class="field-label">Email *</label><input class="ifield" type="email" v-model="f.email_responsable" /></div>
          <div class="sm:col-span-2"><label class="field-label">Profession</label><input class="ifield" type="text" placeholder="Ingénieur" v-model="f.metier_responsable" /></div>
        </div>

        <div class="flex gap-3.5 items-start p-4 rounded-2xl mt-6 mb-4" style="background:rgba(212,168,83,.07);border:1.5px solid rgba(212,168,83,.25)">
          <div class="text-2xl">🚨</div>
          <div>
            <h4 class="text-sm font-bold text-gold mb-1">Contact d'urgence</h4>
            <p class="text-xs text-gray-400">Personne à contacter en cas d'urgence, autre que le responsable légal</p>
          </div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div><label class="field-label">Nom complet</label><input class="ifield" type="text" placeholder="Marie Martin" v-model="f.nom_responsable" /></div>
          <div><label class="field-label">Téléphone</label><input class="ifield" type="tel" v-model="f.telephone_responsable" /></div>
          <div><label class="field-label">Relation</label><input class="ifield" type="text" placeholder="Tante" v-model="f.relation_responsable" /></div>
        </div>

        <div class="flex justify-between mt-7">
          <button class="btn-outline px-7 py-3 rounded-full font-semibold" @click="step = 0">← Retour</button>
          <button class="btn-gold px-7 py-3 rounded-full font-semibold" @click="step = 2">Documents →</button>
        </div>
      </div>

      <!-- Étape 2 — Documents -->
      <div v-else-if="step === 2" class="bg-white rounded-3xl p-10 mt-8" style="box-shadow:0 16px 48px rgba(11,31,58,.12)">
        <div class="flex gap-3.5 items-start p-4 rounded-2xl mb-6" style="background:rgba(26,122,110,.07);border:1.5px solid rgba(26,122,110,.2)">
          <div class="text-2xl">ℹ️</div>
          <div>
            <h4 class="text-sm font-bold text-teal mb-1">Formats acceptés : PDF, JPG, PNG — Max 5 Mo</h4>
            <p class="text-xs text-gray-400">Documents lisibles et à jour. Les originaux pourront être demandés lors de l'entretien.</p>
          </div>
        </div>

        <div class="text-xs font-bold uppercase tracking-widest text-gold flex items-center gap-2.5 mb-4">
          <span class="w-5 h-0.5 bg-gold inline-block"></span> Documents obligatoires
        </div>
        <div v-for="(doc, i) in docs" :key="'o' + i" class="doc-row" :class="{ ok: doc.document_image }">
          <div
            class="rounded-xl flex items-center justify-center text-lg flex-shrink-0"
            :style="{ background: doc.document_image ? 'rgba(26,122,110,.1)' : 'rgba(11,31,58,.05)', width: '40px', height: '40px' }"
          >{{ doc.i }}</div>
          <div class="flex-1">
            <div class="font-semibold text-sm">{{ doc.type_de_document }} <span class="text-red-400 text-xs">*</span></div>
            <div class="text-gray-400 text-xs mt-0.5">{{ doc.h }}</div>
          </div>
          <div class="flex-shrink-0">
            <div v-if="doc.document_image" class="flex items-center gap-1.5 text-xs font-semibold text-teal py-1.5 px-3 rounded-xl" style="background:rgba(26,122,110,.08)">
              <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              <span class="max-w-[80px] overflow-hidden text-ellipsis whitespace-nowrap">{{ doc.document_image }}</span>
              <button @click="doc.f = null" class="bg-transparent border-none text-gray-300 cursor-pointer text-base leading-none ml-1 hover:text-red-400">×</button>
            </div>
            <label v-else class="upload-label">
              Choisir
              <input type="file" accept=".pdf,.jpg,.jpeg,.png" class="hidden" @change="e => { if (e.target.files[0]) doc.document_image = e.target.files[0].name }" />
            </label>
          </div>
        </div>

        <!-- Récap -->
        <div class="rounded-2xl p-5 mt-4 mb-4" style="background:#FAF7F2">
          <div class="font-bold text-sm mb-3">
            Récapitulatif —
            <span :class="docs.filter(d => d.document_image).length === docs.length ? 'text-teal' : 'text-gold'">
              {{ docs.filter(d => d.document_image).length }}/{{ docs.length }}
            </span> obligatoires fournis
          </div>
          <div class="grid grid-cols-2 gap-1.5">
            <div v-for="d in docs" :key="d.type_de_document" class="text-sm">
              {{ d.document_image ? '✅' : '⬜' }}
              <span :class="d.document_image ? 'text-navy' : 'text-gray-400'">{{ d.type_de_document }}</span>
            </div>
          </div>
        </div>

        <div class="flex justify-between">
          <button class="btn-outline px-7 py-3 rounded-full font-semibold" @click="step = 1">← Retour</button>
          <button class="btn-gold px-7 py-3 rounded-full font-semibold" @click="step = 3">Vérifier & Soumettre →</button>
        </div>
      </div>

      <!-- Étape 3 — Vérification -->
      <div v-else-if="step === 3" class="bg-white rounded-3xl p-10 mt-8" style="box-shadow:0 16px 48px rgba(11,31,58,.12)">
        <div class="text-center mb-8">
          <div class="text-6xl mb-3">📋</div>
          <h2 class="font-serif text-3xl mb-2">Vérification finale</h2>
          <p class="text-gray-400 text-sm">Relisez votre dossier avant la soumission définitive.</p>
        </div>

        <!-- Récap élève -->
        <div class="rounded-2xl p-5 mb-4" style="background:#FAF7F2">
          <div class="flex justify-between items-center mb-3.5">
            <h3 class="font-bold text-sm">👤 Élève</h3>
            <button class="text-gold text-xs font-semibold bg-transparent border-none cursor-pointer" @click="step = 0">Modifier</button>
          </div>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div><span class="text-gray-400">Nom : </span><span class="font-semibold">{{ f.prenom }} {{ f.nom }}</span></div>
            <div><span class="text-gray-400">Email : </span><span class="font-semibold">{{ f.email || '—' }}</span></div>
            <div><span class="text-gray-400">Niveau : </span><span class="font-semibold">{{ f.niveau || '—' }}</span></div>
            <div><span class="text-gray-400">Naissance : </span><span class="font-semibold">{{ f.dob || '—' }}</span></div>
          </div>
        </div>

        <!-- Récap tuteur -->
        <div class="rounded-2xl p-5 mb-4" style="background:#FAF7F2">
          <div class="flex justify-between items-center mb-3.5">
            <h3 class="font-bold text-sm">👨‍👩‍👧 Responsable</h3>
            <button class="text-gold text-xs font-semibold bg-transparent border-none cursor-pointer" @click="step = 1">Modifier</button>
          </div>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div><span class="text-gray-400">Nom : </span><span class="font-semibold">{{ f.tPrenom }} {{ f.tNom }}</span></div>
            <div><span class="text-gray-400">Lien : </span><span class="font-semibold">{{ f.tLien || '—' }}</span></div>
            <div><span class="text-gray-400">Tél : </span><span class="font-semibold">{{ f.tTel || '—' }}</span></div>
            <div><span class="text-gray-400">Email : </span><span class="font-semibold">{{ f.tEmail || '—' }}</span></div>
          </div>
        </div>

        <!-- Récap docs -->
        <div class="rounded-2xl p-5 mb-5" style="background:#FAF7F2">
          <div class="flex justify-between items-center mb-3.5">
            <h3 class="font-bold text-sm">📁 Documents ({{ docs.filter(d => d.f).length }}/{{ docs.length }})</h3>
            <button class="text-gold text-xs font-semibold bg-transparent border-none cursor-pointer" @click="step = 2">Modifier</button>
          </div>
          <div class="grid grid-cols-2 gap-1.5 text-sm">
            <div v-for="d in docs" :key="d.n">
              {{ d.f ? '✅' : '❌' }} <span :class="d.f ? 'text-navy' : 'text-red-400'">{{ d.n }}</span>
            </div>
          </div>
        </div>

        <!-- Consentements -->
        <div class="consent-row" :class="{ on: f.cgv }" @click="f.cgv = !f.cgv">
          <input type="checkbox" :checked="f.cgv" @change="f.cgv = !f.cgv" style="width:16px;height:16px;accent-color:#D4A853;flex-shrink:0;margin-top:2px" />
          <p class="text-sm text-gray-500 leading-relaxed">J'accepte les <strong class="text-gold">conditions générales</strong> et la politique de protection des données. *</p>
        </div>
        <div class="consent-row" :class="{ on: f.conf }" @click="f.conf = !f.conf">
          <input type="checkbox" :checked="f.conf" @change="f.conf = !f.conf" style="width:16px;height:16px;accent-color:#D4A853;flex-shrink:0;margin-top:2px" />
          <p class="text-sm text-gray-500 leading-relaxed">Je certifie que toutes les informations fournies sont exactes et sincères. *</p>
        </div>

        <div class="flex justify-between items-center mt-7">
          <button class="btn-outline px-7 py-3 rounded-full font-semibold" @click="step = 2">← Retour</button>
          <button
            class="btn-gold px-8 py-3.5 rounded-full font-semibold"
            :disabled="!f.cgv || !f.conf"
            :class="{ 'opacity-40 cursor-not-allowed': !f.cgv || !f.conf }"
            @click="submit"
          >🚀 Soumettre ma candidature</button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, computed } from 'vue'
import { DOCS_BASE } from '@/data/index.js'
import { initReveal } from '@/composables/useReveal.js'
import { storeToRefs } from 'pinia';
import { useSchoolStoreInfo } from '@/stores/schoolStore';

const schoolStore = useSchoolStoreInfo();
const { classes_global, annee_global, niveau_global,faculte } = storeToRefs(schoolStore);
 
// ── Données statiques ─────────────────────────
const ADM_STEPS = [
  { l: 'Informations', icon: '👤' },
  { l: 'Tuteur',       icon: '👨‍👩‍👧' },
  { l: 'Documents',    icon: '📁' },
  { l: 'Vérification', icon: '✅' },
]

// ── State ─────────────────────────────────────
const step   = ref(0)
const done   = ref(false)
const admRef = ref('')
const docs   = ref(DOCS_BASE.map(d => ({ ...d })))

const f1 = reactive({
  nom: '', prenom: '', dob: '', sexe: '', email: '', tel: '', adresse: '',
  niveau: '', annee: '2025 – 2026', motif: '', bourse: false, handicap: false,
  tLien: '', tCiv: 'Madame', tNom: '', tPrenom: '', tTel: '', tEmail: '', tPro: '',
  urgNom: '', urgTel: '', urgRel: '',
  cgv: false, conf: false,
})

const f = reactive({
  documentss: [], id: '', dernier_etablissement: '', nisu: '',
  aide_financiere: 'Aucune', nom: '', prenom: '', telephone: '',
  sexe: '', date_de_naissance: '', adresse: '', lieu_de_naissance: '',
  religion: '', niveau_id: '', classe_actuelle_id: '', annee_academique_id: '',
  faculte_id: '', email: '',
  nom_responsable: '', prenom_responsable: '', email_responsable: '',
  relation_responsable: '', sexe_responsable: '', telephone_responsable: '',
  metier_responsable: '', adresse_responsable: '',bourse: false,handicap: false,
  errors: {},processing:false
});

// ── Méthodes ──────────────────────────────────
function submit() {
  if (!f.cgv || !f.conf) return
  admRef.value = Math.random().toString(36).substring(2, 8).toUpperCase()
  done.value = true
}

// const is_university = computed(() => 
//   niveau_global.value.some(x => x.id === f.value.niveau_id)
// )
const is_university = computed(() => {
  const niveau = niveau_global.value?.find(x => x.id === f.value?.niveau_id)
  return niveau?.name === 'Universitaire' // adapte selon ta structure
})

function reset() {
  done.value = false
  step.value = 0
  docs.value = DOCS_BASE.map(d => ({ ...d }))
  Object.keys(f).forEach(k => { f[k] = typeof f[k] === 'boolean' ? false : '' })
  f.tCiv  = 'Madame'
  f.annee = '2025 – 2026'
}

onMounted(() => { schoolStore.fetchAllDependencies();window.scrollTo(0, 0); initReveal() })
watch(step, () => { window.scrollTo({ top: 340, behavior: 'smooth' }); initReveal() })
</script>

<style scoped>
/* Label helper local à ce composant */
.field-label {
  display: block;
  font-size: .7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: #64748b;
  margin-bottom: 6px;
}
</style>
