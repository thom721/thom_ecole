<template>
  <div>
    <!-- ══ HERO ══════════════════════════════════════════ -->
    <div class="relative overflow-hidden" style="height:58vh;min-height:380px">
      <img
        src="https://images.unsplash.com/photo-1497366216548-37526070297c?w=1800&q=80"
        alt="Contact"
        class="hero-img w-full h-full object-cover block"
      />
      <div class="absolute inset-0" style="background:linear-gradient(135deg,rgba(11,31,58,.9),rgba(212,168,83,.3),rgba(26,122,110,.5))"></div>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <p class="text-xs font-bold mb-3" style="color:#fde68a;letter-spacing:.3em;text-transform:uppercase">Parlons-nous</p>
        <h1 class="font-serif text-white mb-4" style="font-size:clamp(2.2rem,5vw,4.2rem)">
          Contactez-<span class="text-gold">Nous</span>
        </h1>
        <p style="color:rgba(255,255,255,.8)" class="max-w-lg leading-relaxed">
          Notre équipe est disponible pour répondre à toutes vos questions, du lundi au samedi.
        </p>
      </div>
    </div>

    <GenericSection v-for="gs in genericSectionsInZone(5)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="contact"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <!-- ══ CARDS CONTACT ══════════════════════════════════ -->
    <section class="py-16">
      <div class="max-w-6xl mx-auto px-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-14">
          <div
            v-for="(ct, i) in CONTACT_CARDS"
            :key="ct.t"
            class="bg-white rounded-2xl shadow-md card-hover text-center reveal"
            :class="i ? 'd' + i : ''"
          >
            <div class="p-7">
              <div
                class="rounded-2xl flex items-center justify-center text-3xl mx-auto mb-5"
                :style="{ background: ct.bg, width: '64px', height: '64px' }"
              >{{ ct.i }}</div>
              <div v-if="i==0" class="text-gray-500 text-sm mb-1">{{useSchoolInfo.school_info?.ligne1 || '+509 3755-9811'}} <br> {{useSchoolInfo.school_info?.ligne2 || '+509 3247-1571'}}</div>
              <div v-if="i==1" class="font-bold text-lg mb-1.5">{{useSchoolInfo.school_info?.email || 'contact@iusth.edu.ht'}}</div>
              <div v-if="i==2" class="font-bold text-lg mb-1.5">{{useSchoolInfo.school_info?.adresse || '#5, Impasse Cantave, Delmas 75'}}</div>
              <!-- <div class="font-semibold text-sm text-gold">{{ ct.l2 }}</div> -->
            </div>
          </div>
        </div>

        <!-- ══ FORMULAIRE + INFOS ══════════════════════════ -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">

          <!-- Formulaire -->
          <div class="bg-white rounded-2xl shadow-md reveal-l">
            <div class="p-8">
              <p class="text-xs tracking-widest uppercase font-bold text-gold">Formulaire</p>
              <div class="gold-line mt-3.5 mb-3"></div>
              <h2 class="font-serif text-2xl mb-6">Envoyez un message</h2>

              <!-- Message de succès -->
              <transition name="fade">
                <div v-if="sent" class="mb-5 p-4 rounded-2xl text-sm font-semibold text-teal" style="background:rgba(26,122,110,.08);border:1.5px solid rgba(26,122,110,.2)">
                  ✅ Message envoyé ! Nous vous répondrons sous 24h.
                </div>
              </transition>
              <!-- Message d'erreur -->
              <transition name="fade">
                <div v-if="sendError" class="mb-5 p-4 rounded-2xl text-sm font-semibold text-red-500" style="background:rgba(239,68,68,.08);border:1.5px solid rgba(239,68,68,.2)">
                  ⚠️ {{ sendError }}
                </div>
              </transition>

              <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label class="field-label">Prénom</label>
                  <input class="ifield" type="text" placeholder="Marie" v-model="form.prenom" />
                </div>
                <div>
                  <label class="field-label">Nom</label>
                  <input class="ifield" type="text" placeholder="Dupont" v-model="form.nom" />
                </div>
              </div>
              <div class="mb-4">
                <label class="field-label">Email *</label>
                <input class="ifield" :class="{ 'input-err': err.email }" type="email" placeholder="marie@exemple.fr" v-model="form.email" @input="err.email = false" />
                <p v-if="err.email" class="text-red-400 text-xs mt-1">Veuillez saisir un email valide.</p>
              </div>
              <div class="mb-4">
                <label class="field-label">Objet</label>
                <select class="ifield" v-model="form.objet">
                  <option>Demande d'information</option>
                  <option>Inscription</option>
                  <option>Partenariat</option>
                  <option>Support technique</option>
                  <option>Autre</option>
                </select>
              </div>
              <div class="mb-4">
                <label class="field-label">Téléphone</label>
                <input class="ifield" type="tel" placeholder="+33 6 00 00 00 00" v-model="form.tel" />
              </div>
              <div class="mb-6">
                <label class="field-label">Message *</label>
                <textarea class="ifield" rows="5" placeholder="Votre message…" v-model="form.msg" :class="{ 'input-err': err.msg }" @input="err.msg = false"></textarea>
                <p v-if="err.msg" class="text-red-400 text-xs mt-1">Le message ne peut pas être vide.</p>
              </div>
              <button
                class="btn-gold w-full py-3.5 rounded-full font-semibold"
                :disabled="loading"
                @click="send"
              >
                <span v-if="loading" class="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full spin"></span>
                <span v-else>Envoyer le message →</span>
              </button>
            </div>
          </div>

          <!-- Infos + Carte -->
          <div class="flex flex-col gap-5 reveal-r">
            <!-- Horaires -->
            <div class="bg-white rounded-2xl shadow-md overflow-hidden">
              <div class="px-7 py-6" style="background:linear-gradient(135deg,#0B1F3A,#1A7A6E)">
                <h3 class="text-white font-serif text-lg mb-1">Horaires d'accueil</h3>
                <p class="text-xs" style="color:rgba(255,255,255,.6)">Disponible aux horaires suivants</p>
              </div>
              <div class="px-7 py-2">
                <div v-for="(h, i) in HOURS" :key="i" class="hours-row">
                  <span class="text-sm">{{ h.jour }}</span>
                  <span class="font-semibold text-teal text-sm">{{ h.horaire }}</span>
                </div>
              </div>
            </div>

            <!-- Localisation -->
            <div class="bg-white rounded-2xl shadow-md p-7">
              <h3 class="font-serif text-lg mb-4">Localisation</h3>
              <div
                class="h-44 rounded-2xl flex items-center justify-center text-6xl mb-4"
                style="background:linear-gradient(135deg,#dbeafe,#d1fae5)"
              >🗺️</div>
              <p class="text-gray-500 text-sm mb-1.5">📍 {{useSchoolInfo.school_info?.adresse || 'IUSTH'}}</p>
              <!-- <p class="text-gray-500 text-sm mb-1.5">🚇 Métro : Champs-Élysées — Clemenceau</p>
              <p class="text-gray-500 text-sm">🅿️ Parking gratuit disponible le week-end</p> -->
            </div>

            <!-- Réseaux sociaux -->
            <div class="bg-white rounded-2xl shadow-md p-7">
              <h3 class="font-serif text-lg mb-4">Réseaux sociaux</h3>
              <div class="flex gap-3 flex-wrap">
                <a
                  v-for="s in SOCIAL"
                  :key="s.l"
                  :href="s.href"
                  target="_blank"
                  rel="noopener"
                  class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold no-underline transition-all"
                  :style="{ background: s.bg, color: s.c }"
                >{{ s.i }} {{ s.l }}</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ FAQ ════════════════════════════════════════════ -->
    <section class="py-16" style="background:#EFECE5">
      <div class="max-w-2xl mx-auto px-6">
        <div class="text-center reveal mb-10">
          <p class="text-xs tracking-widest uppercase font-bold text-gold">Questions fréquentes</p>
          <div class="gold-line mx mt-3.5 mb-3"></div>
          <h2 class="font-serif text-3xl mt-1">FAQ</h2>
        </div>
        <div class="space-y-3">
          <div
            v-for="(q, i) in FAQ"
            :key="i"
            class="bg-white rounded-2xl overflow-hidden reveal"
            :class="i ? 'd' + Math.min(i, 4) : ''"
            style="box-shadow:0 2px 12px rgba(11,31,58,.07)"
          >
            <button
              class="w-full flex justify-between items-center px-6 py-4 text-left bg-transparent border-none cursor-pointer font-semibold text-sm"
              @click="openFaq = openFaq === i ? null : i"
            >
              {{ q.q }}
              <span class="text-gold ml-3 transition-transform" :class="openFaq === i ? 'rotate-45' : ''">+</span>
            </button>
            <transition name="fade">
              <div v-if="openFaq === i" class="px-6 pb-5 text-sm text-gray-500 leading-relaxed whitespace-pre-line">
                {{ q.r }}
              </div>
            </transition>
          </div>
        </div>
      </div>
    </section>

    <GenericSection v-for="gs in genericSectionsInZone(95)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="contact"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <div v-if="authStore.isAdmin" class="bg-gray-50 py-3 text-center">
      <button @click="showAddBlockModal = true" class="px-4 py-1.5 rounded-full bg-blue-500/10 text-blue-600 text-xs font-semibold hover:bg-blue-500/20">
        + Ajouter un bloc (n'importe où sur la page)
      </button>
    </div>

    <!-- Modal : ajouter un bloc générique -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showAddBlockModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="closeAddBlockModal">
        <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl">
          <div class="flex items-center gap-2 justify-between px-6 py-4 border-b">
            <h2 class="text-sm font-semibold text-gray-800 flex items-center gap-2">
              <button v-if="pendingZone" @click="pendingZone = null" class="text-gray-500 hover:text-gray-600">←</button>
              {{ pendingZone ? 'Choisir un modèle' : 'Où ajouter le bloc ?' }}
            </h2>
            <button @click="closeAddBlockModal" class="text-gray-500 hover:text-gray-600">✕</button>
          </div>
          <div class="px-6 py-5 space-y-3 max-h-[60vh] overflow-y-auto">
            <template v-if="!pendingZone">
              <button
                v-for="z in zones" :key="z.ordre"
                @click="pendingZone = z"
                class="w-full text-left border border-gray-200 rounded-xl px-4 py-3 hover:border-blue-400 hover:bg-blue-50/50 transition-colors"
              >
                <div class="font-semibold text-sm text-gray-800">{{ z.label }}</div>
              </button>
            </template>
            <template v-else>
              <button
                v-for="tpl in LAYOUT_TEMPLATES" :key="tpl.layout"
                @click="pickBlockTemplate(tpl)"
                class="w-full text-left border border-gray-200 rounded-xl px-4 py-3 hover:border-blue-400 hover:bg-blue-50/50 transition-colors"
              >
                <div class="font-semibold text-sm text-gray-800">{{ tpl.label }}</div>
                <div class="text-xs text-gray-500 mt-0.5">{{ tpl.desc }}</div>
              </button>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { initReveal } from '@/composables/useReveal.js'
import { useSchoolStore, useSchoolStoreInfo } from '@/stores/schoolStore';
import { useAuthStore } from '@/stores/auth'
import GenericSection from '@/components/GenericSection.vue'
import { usePageSections, LAYOUT_TEMPLATES } from '@/composables/usePageSections.js'
const useSchoolInfo = useSchoolStoreInfo();
const authStore = useAuthStore()
const url = import.meta.env.VITE_APP_BASE_URL

// ── Blocs génériques ajoutés librement (voir HomeView.vue pour le détail) ──
const {
  genericSections, genericSectionsInZone, createGenericSection, fetchSections: fetchGenericSections,
  toggleSection: toggleGenericSection, deleteSection: deleteGenericSection, zones,
} = usePageSections('contact')
const showAddBlockModal = ref(false)
const pendingZone = ref(null)
const closeAddBlockModal = () => { showAddBlockModal.value = false; pendingZone.value = null }
const pickBlockTemplate = async (tpl) => {
  const ok = await createGenericSection(tpl, pendingZone.value.ordre)
  if (ok) closeAddBlockModal()
}

// Coordonnées réelles IUSTH (voir Audit_site_IUSTH_2026-08-27.pdf, point 2.3 :
// l'ancien site affichait un Gmail non institutionnel — ici contact@iusth.edu.ht).
const CONTACT_CARDS = [
  { i: '📞', t: 'Téléphone',  l1: 'Ven–Sam : 8h–17h',  l2: '+509 3755-9811 / +509 3247-1571', bg: 'linear-gradient(135deg,#EFF6FF,#BFDBFE)' },
  { i: '📧', t: 'Email',      l1: 'Réponse sous 24h',    l2: 'contact@iusth.edu.ht', bg: 'linear-gradient(135deg,#FEF3C7,#FDE68A)' },
  { i: '📍', t: 'Adresse',    l1: '#5, Impasse Cantave', l2: 'Delmas 75, Haïti', bg: 'linear-gradient(135deg,#ECFDF5,#A7F3D0)' },
]

// Horaires lus depuis Profile.horaires (voir RProfile.py) plutôt que codés en
// dur — éditable dans l'admin ("Profil de l'école"). Fallback vers les
// horaires réels IUSTH tant qu'aucune ligne n'a encore été enregistrée
// (point 3.2 de l'audit : l'ancien site mélangeait format 12h/24h sur
// "Vendredi-Samedi : 8h – 5h", corrigé ici en format 24h sans ambiguïté).
const HOURS = computed(() => {
  const h = useSchoolInfo.school_info?.horaires
  return (h && h.length) ? h : [
    { jour: 'Vendredi – Samedi', horaire: '8h00 – 17h00' },
    { jour: 'Dimanche – Jeudi',  horaire: 'Fermé' },
  ]
})

// Lues depuis Profile (voir Contact/RProfile.py) plutôt que codées en dur —
// chaque réseau n'apparaît que s'il est réellement renseigné, jamais de lien
// mort "#" (voir Audit_site_IUSTH_2026-08-27.pdf, point 2.2 : lien WhatsApp
// cassé sur tout l'ancien site). Fallback WhatsApp vers le vrai numéro de
// contact tant que le champ profiles.whatsapp_url n'est pas encore rempli.
const SOCIAL = computed(() => {
  const info = useSchoolInfo.school_info || {}
  const all = [
    { i: '💬', l: 'WhatsApp',  bg: '#ECFDF5', c: '#15803d', href: info.whatsapp_url || 'https://wa.me/50937559811' },
    { i: '📘', l: 'Facebook',  bg: '#EFF6FF', c: '#1d4ed8', href: info.facebook_url },
    { i: '🎵', l: 'TikTok',    bg: '#F5F3FF', c: '#6d28d9', href: info.tiktok_url },
    { i: '▶️', l: 'YouTube',   bg: '#FEF2F2', c: '#b91c1c', href: info.youtube_url },
  ]
  return all.filter(s => !!s.href)
})

const FAQ = [
  {
    q: 'Comment puis-je postuler ?',
    r: "Le postulant devra se rendre au secrétariat de la Direction des affaires académiques et soumettre toutes les pièces suivantes : formulaire de demande d'admission (rempli en ligne ou en présentiel puis imprimé) ; une expédition de l'acte de naissance (original et une copie) ; le certificat de fin d'études secondaires classiques (Bac II ou équivalent) ; les relevés de notes obtenues aux examens du baccalauréat II ; deux photos d'identité récentes (maximum 3 mois).\n\n" +
       "Ré-admission : en cas d'absence pendant la première session, l'étudiant pourra rouvrir son dossier sans frais ; en cas d'absence pendant au moins 2 sessions, l'étudiant devra payer des frais de réouverture de dossier.\n\n" +
       "Admission sur dossier : le transfert d'une autre université est traité sur dossier.",
  },
  {
    q: 'Quels sont les frais de scolarité ?',
    r: "L'éducation a un prix. À l'IUSTH, les frais et autres coûts sont gérés par le service de paiement. Les frais varient en fonction des taux de coût de la vie et sont calculés selon le choix de faculté. Pour connaître les frais de scolarité, veuillez communiquer avec le service financier au contact@iusth.edu.ht.\n\n" +
       "Paiement de votre facture électronique à partir de votre portail étudiant — vous recevez un email de confirmation de dépôt à votre nom @iusth.edu.ht. Date limite de paiement : vous devez payer votre facture au plus tard le 5 de chaque mois.",
  },
  {
    q: 'Y a-t-il des bourses disponibles ?',
    r: "À chaque session, le Secrétariat de la Direction académique de l'Institut Universitaire des Sciences et des Technologies d'Haïti (IUSTH) reçoit les demandes d'admission pour les programmes de premier cycle et de certificat (cycle court) proposés par les différentes facultés. Les demandes d'admission se font d'abord en présentiel, puis en ligne (voir le volet Admission).",
  },
]

// ── State ─────────────────────────────────────
const form = reactive({ prenom: '', nom: '', email: '', objet: "Demande d'information", tel: '', msg: '' })
const err  = reactive({ email: false, msg: false })
const sent    = ref(false)
const sendError = ref('')
const loading = ref(false)
const openFaq = ref(null)

// ── Envoi formulaire ── vers /contact (voir app/Routes/RContact.py), qui
// transmet le message par email à contact@iusth.edu.ht avec Reply-To sur
// l'expéditeur (le formulaire ne faisait auparavant que simuler un envoi).
async function send() {
  err.email = !form.email.includes('@')
  err.msg   = !form.msg.trim()
  sendError.value = ''
  if (err.email || err.msg) return

  loading.value = true
  try {
    await axios.post(`${url}/contact/`, form)
    sent.value = true
    Object.keys(form).forEach(k => { form[k] = '' })
    form.objet = "Demande d'information"
    setTimeout(() => { sent.value = false }, 5000)
  } catch (e) {
    sendError.value = e.response?.data?.detail || "L'envoi a échoué. Réessayez ou contactez-nous directement par email."
  } finally {
    loading.value = false
  }
}

onMounted(() => { window.scrollTo(0, 0); initReveal(); fetchGenericSections() })
</script>

<style scoped>
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
