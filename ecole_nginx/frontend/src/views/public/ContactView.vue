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
              <div v-if="i==0" class="text-gray-400 text-sm mb-1">{{useSchoolInfo.school_info?.ligne1 || '+509 4354 26 32'}} <br> {{useSchoolInfo.school_info?.ligne2 || '+509 4354 26 32'}}</div>
              <div v-if="i==1" class="font-bold text-lg mb-1.5">{{useSchoolInfo.school_info?.email || 'Lekol 360'}}</div>
              <div v-if="i==2" class="font-bold text-lg mb-1.5">{{useSchoolInfo.school_info?.adresse || 'Lekol 360'}}</div>
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
                <div v-for="h in HOURS" :key="h.j" class="hours-row">
                  <span class="text-sm">{{ h.j }}</span>
                  <span class="font-semibold text-teal text-sm">{{ h.t }}</span>
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
              <p class="text-gray-400 text-sm mb-1.5">📍 {{useSchoolInfo.school_info?.adresse || 'Lekol 360'}}</p>
              <!-- <p class="text-gray-400 text-sm mb-1.5">🚇 Métro : Champs-Élysées — Clemenceau</p>
              <p class="text-gray-400 text-sm">🅿️ Parking gratuit disponible le week-end</p> -->
            </div>

            <!-- Réseaux sociaux -->
            <div class="bg-white rounded-2xl shadow-md p-7">
              <h3 class="font-serif text-lg mb-4">Réseaux sociaux</h3>
              <div class="flex gap-3 flex-wrap">
                <a
                  v-for="s in SOCIAL"
                  :key="s.l"
                  href="#"
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
    <section class="py-16" style="background:#FAF7F2">
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
              <div v-if="openFaq === i" class="px-6 pb-5 text-sm text-gray-400 leading-relaxed">
                {{ q.r }}
              </div>
            </transition>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { initReveal } from '@/composables/useReveal.js'
import { useSchoolStore, useSchoolStoreInfo } from '@/stores/schoolStore';
const useSchoolInfo = useSchoolStoreInfo();

const CONTACT_CARDS = [
  { i: '📞', t: 'Téléphone',  l1: 'Lun–Ven : 8h–18h',  l2: '+33 1 23 45 67 89',   bg: 'linear-gradient(135deg,#EFF6FF,#BFDBFE)' },
  { i: '📧', t: 'Email',      l1: 'Réponse sous 24h',    l2: 'contact@edusphere.fr', bg: 'linear-gradient(135deg,#FEF3C7,#FDE68A)' },
  { i: '📍', t: 'Adresse',    l1: "12 Av. de l'Éducation", l2: '75008 Paris, France', bg: 'linear-gradient(135deg,#ECFDF5,#A7F3D0)' },
]

const HOURS = [
  { j: 'Lundi – Vendredi', t: '8h00 – 18h00' },
  { j: 'Samedi',           t: '9h00 – 13h00' },
  { j: 'Dimanche',         t: 'Fermé' },
]

const SOCIAL = [
  { i: '📘', l: 'Facebook',  bg: '#EFF6FF', c: '#1d4ed8' },
  { i: '📸', l: 'Instagram', bg: '#FDF4FF', c: '#7c3aed' },
  { i: '🔗', l: 'LinkedIn',  bg: '#EFF6FF', c: '#0369a1' },
]

const FAQ = [
  { q: 'Quand ouvrent les inscriptions ?',             r: 'Les inscriptions pour 2025–2026 sont ouvertes du 1er février au 30 avril 2025. Passé ce délai, les candidatures sont examinées selon les places disponibles.' },
  { q: 'Quels documents sont requis pour le dossier ?', r: "Acte de naissance, photo d'identité, pièce d'identité élève et tuteur, derniers bulletins scolaires et justificatif de domicile. Le formulaire en ligne vous guidera étape par étape." },
  { q: 'Y a-t-il des bourses disponibles ?',           r: "Oui,on propose des bourses sur critères sociaux et d'excellence. La demande doit être formulée lors de l'inscription accompagnée des justificatifs requis." },
  { q: 'Comment se déroule la visite de l\'établissement ?', r: 'Des journées portes ouvertes sont organisées chaque trimestre. Vous pouvez également prendre rendez-vous individuellement via ce formulaire ou par téléphone.' },
]

// ── State ─────────────────────────────────────
const form = reactive({ prenom: '', nom: '', email: '', objet: "Demande d'information", tel: '', msg: '' })
const err  = reactive({ email: false, msg: false })
const sent    = ref(false)
const loading = ref(false)
const openFaq = ref(null)

// ── Envoi formulaire ──────────────────────────
function send() {
  err.email = !form.email.includes('@')
  err.msg   = !form.msg.trim()
  if (err.email || err.msg) return

  loading.value = true
  setTimeout(() => {
    loading.value = false
    sent.value    = true
    Object.keys(form).forEach(k => { form[k] = '' })
    form.objet = "Demande d'information"
    setTimeout(() => { sent.value = false }, 5000)
  }, 1200)
}

onMounted(() => { window.scrollTo(0, 0); initReveal() })
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
