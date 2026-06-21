<!-- src/views/ParametresView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div>
      <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Paramètres</h1>
      <p class="text-[#7c83a0] text-sm">Gérez votre profil et vos préférences</p>
    </div>

    <div class="grid md:grid-cols-[400px_1fr] gap-5 items-start">

      <!-- Profile -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6 flex flex-col gap-5">
        <p class="text-base font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">Profil Enseignant</p>
        <div class="flex items-center gap-4 pb-5 border-b border-white/[0.07]">
          <div class="w-14 h-14 rounded-full flex items-center justify-center text-[18px] font-bold text-[#0f1117] flex-shrink-0" :style="{ background: `linear-gradient(135deg, var(--accent,#4f8ef7), #6ee7b7)` }">MS</div>
          <div>
            <p class="text-[16px] font-semibold text-[#e8eaf0]">{{professerDetails?.prenom}} {{professerDetails?.nom}}</p>
            <p class="text-[12px] text-[#7c83a0]">Professeur(e) {{professerDetails?.matiere}}</p>
          </div>
        </div>
        <div class="flex flex-col gap-3">
          <div v-for="f in profileFields" :key="f.label" class="flex flex-col gap-1.5">
            <label class="text-[11px] uppercase tracking-widest text-[#7c83a0] font-medium">{{ f.label }}</label>
            <input
              :type="f.type||'text'" v-model="f.value"
              class="bg-[#1e2335] border border-white/10 rounded-md px-4 py-2.5 text-[#e8eaf0] text-sm outline-none focus:border-white/20 transition-colors w-full"
            />
          </div>
        </div>
        <button class="px-5 py-2.5 text-white rounded-md text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0 self-start" :style="{ background: 'var(--accent,#4f8ef7)' }">Enregistrer</button>
      </div>

      <div class="flex flex-col gap-5">
        <!-- Notifications -->
        <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
          <p class="text-base font-semibold text-[#e8eaf0] mb-4" style="font-family:'Playfair Display',serif">Notifications</p>
          <div class="flex flex-col gap-3.5">
            <div v-for="n in notifications" :key="n.label" class="flex items-center justify-between gap-3">
              <div>
                <p class="text-[13px] font-medium text-[#e8eaf0]">{{ n.label }}</p>
                <p class="text-[11px] text-[#7c83a0]">{{ n.sub }}</p>
              </div>
              <!-- Toggle -->
              <div
                @click="n.on = !n.on"
                class="relative w-10 h-6 rounded-full border border-white/10 cursor-pointer transition-all duration-250 flex-shrink-0"
                :style="n.on ? { background: 'var(--accent,#4f8ef7)', borderColor: 'transparent' } : { background: '#1e2335' }"
              >
                <span
                  class="absolute top-[3px] w-[18px] h-[18px] rounded-full bg-white transition-all duration-250"
                  :class="n.on ? 'left-[18px]' : 'left-[3px]'"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- School settings -->
        <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
          
              <!-- <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-2 md:p-6 my-8"> -->
      <h2 class="font-bold text-[#e8eaf0] mb-5 flex items-center gap-2 text-[#e8eaf0] mb-4 text-base" style="font-family:'Playfair Display',serif">
        <span class="w-6 h-6 rounded-md bg-slate-100 text-slate-500 flex items-center justify-center text-xs">🔑</span>
        Changer le mot de passe
      </h2>
      <form @submit.prevent="updatePassword">
        <div class="grid grid-cols-1 gap-5 px-8">
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Mot de passe actuel</label>
            <input v-model="passwordForm.current" type="password" placeholder="••••••••"
              class="bg-[#1e2335] border border-white/10 rounded-md px-4 py-2.5 text-[#e8eaf0] text-sm outline-none focus:border-white/20 transition-colors w-full" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Nouveau mot de passe</label>
            <input v-model="passwordForm.newPw" type="password" placeholder="••••••••"
              class="bg-[#1e2335] border border-white/10 rounded-md px-4 py-2.5 text-[#e8eaf0] text-sm outline-none focus:border-white/20 transition-colors w-full" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Confirmer</label>
            <input v-model="passwordForm.confirm" type="password" placeholder="••••••••"
              class="bg-[#1e2335] border border-white/10 rounded-md px-4 py-2.5 text-[#e8eaf0] text-sm outline-none focus:border-white/20 transition-colors w-full"
              :class="pwMismatch
                ? 'border-red-400 focus:border-red-400 focus:ring-1 focus:ring-red-100 text-red-700'
                : 'border-slate-200 focus:border-sky-500 focus:ring-1 focus:ring-sky-100 text-slate-800'" />
            <span v-if="pwMismatch" class="text-xs text-red-500">⚠ Les mots de passe ne correspondent pas.</span>
          </div>
        </div>
        <div class="flex justify-end mt-5 pt-4 border-t border-slate-100">
          <button type="submit"
            class="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-slate-800 hover:bg-slate-900 active:scale-95 text-white text-sm font-semibold shadow-sm transition-all cursor-pointer" :disabled="passwordForm.processing">
            <svg v-if="passwordForm.processing" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg> 
            <span>{{ passwordForm.processing ? 'Changement...' : '🔒 Changer le mot de passe' }}</span>
            
          </button>
        </div>
      </form>
    <!-- </div> -->
          <!-- <div class="flex flex-col gap-3 mb-3">
            <div v-for="f in schoolFields" :key="f.label" class="flex flex-col gap-1.5">
              <label class="text-[11px] uppercase tracking-widest text-[#7c83a0] font-medium">{{ f.label }}</label>
              <input :value="f.value" class="bg-[#1e2335] border border-white/10 rounded-md px-4 py-2.5 text-[#e8eaf0] text-sm outline-none focus:border-white/20 transition-colors w-full" />
            </div>
          </div>
                 <button class="px-5 py-2.5 text-white rounded-md text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0 self-start" :style="{ background: 'var(--accent,#4f8ef7)' }">Enregistrer</button> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { reactive,ref,computed,onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const url = import.meta.env.VITE_APP_BASE_URL ?? ''

const professerDetails = ref({})

const profileFields = reactive([
  { label:'Prénom',            value:professerDetails.value?.prenom,                  type:'text'  },
  { label:'Nom',               value:professerDetails.value?.nom,                 type:'text'  },
  { label:'Nom d\'utilisateur',               value:professerDetails.value?.user?.username,                 type:'text'  },
  { label:'Email',             value:professerDetails.value?.user?.email,  type:'email' },
  { label:'Matière principale',value:'Mathématiques',          type:'text'  },
  { label:'Niveaux enseignés', value:'Seconde, Première, Terminale', type:'text' },
])
const schoolFields = reactive([
  { label:'Nom de l\'établissement', value:'EduPilot'            },
  { label:'Sous-titre sidebar',      value:'Espace Enseignant'   },
  { label:'Initiales (logo)',        value:'E'                   },
])
const notifications = reactive([
  { label:'Nouveaux messages',        sub:'Alerte lors d\'un nouveau message', on:true  },
  { label:'Devoirs rendus',           sub:'Notification quand un élève remet', on:true  },
  { label:'Absences',                 sub:'Alerte sur les absences répétées',  on:true  },
  { label:'Bulletins disponibles',    sub:'Rappel lors de l\'édition',         on:false },
  { label:'Réunions à venir',         sub:'48h avant chaque événement',        on:true  },
])

const passwordForm = ref({ current: '', newPw: '', confirm: '',processing:false })
const pwMismatch   = computed(() =>
  passwordForm.value.confirm && passwordForm.value.newPw !== passwordForm.value.confirm
)

const updatePassword = async () => {
  if (pwMismatch.value || !passwordForm.value.current || !passwordForm.value.newPw) {
    notify('Vérifiez les champs mot de passe.', false)
    return
  }
  passwordForm.value.processing = true
  try {
    await axios.put('/password-change-user-global', {
      current_password: passwordForm.value.current,
      password: passwordForm.value.newPw,
      password_confirmation: passwordForm.value.confirm,
    })
    notify('Mot de passe changé !')
    passwordForm.value.current = ''
    passwordForm.value.newPw = ''
    passwordForm.value.confirm = ''
    passwordForm.value.processing = false
    
  } catch (error) {
    notify(error.response?.data?.message, false)
  } finally {
    passwordForm.value.processing = false
  }
}


onMounted( async () => {
  const { data } = await axios.get(`/professeur/${authStore?.user.user?.userable_id}`)
  professerDetails.value=data?.data
  
  console.log(professerDetails.value.nom);
})


</script>
