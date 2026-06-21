<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'; 

const authStore = useAuthStore(); 
const { user, isAdmin, isTeacher, roleNames } = storeToRefs(authStore);

const dataStudent   = computed(() => bulletinData.value?.data_student   || {})
const dataEtudiant  = computed(() => dataStudent.value?.data_etudiant    || {})
const bulletinData = ref(null)
const month_payes = ref(null)
const mois_demande_ = ref('')
/* ══════════════════════════════════════════════
   DONNÉES DE TEST — remplacer par vos appels API
   ══════════════════════════════════════════════ */
const student = ref({
  prenom:     'Jean-Marc',
  nom:        'Dorélien',
  identifiant:'STU-2024-0892',
  classe:     'CMI A',
  niveau:     'Primaire',
  photo:      null,
  annee:      '2024-2025',
})

const statsCards = ref([
  { label: 'Moyenne Générale', value: '0.8', unit: '/20', icon: '📊', color: 'emerald', trend: '+1.2 ce trimestre' },
  { label: 'Absences',         value: '3',    unit: 'jours', icon: '📅', color: 'amber',   trend: '0 ce mois-ci' },
  { label: 'Cours validés',    value: '0',    unit: '/11',   icon: '✅', color: 'sky',     trend: '2 en cours' },
  { label: 'Rang de classe',   value: '4',    unit: 'ème',   icon: '🏅', color: 'violet',  trend: 'sur 28 élèves' },
])

const notes = ref([
  { matiere: 'Mathématiques',    note: 16.5, coef: 4, prof: 'M. Pierre',    icon: '🔢', color: '#10b981' },
  { matiere: 'Français',         note: 13.0, coef: 4, prof: 'Mme. Marie',   icon: '📝', color: '#6366f1' },
  { matiere: 'Sciences',         note: 15.5, coef: 3, prof: 'M. André',     icon: '🔬', color: '#0ea5e9' },
  { matiere: 'Histoire-Géo',     note: 14.0, coef: 2, prof: 'Mme. Sophie',  icon: '🌍', color: '#f59e0b' },
  { matiere: 'Éducation Physique', note: 18.0, coef: 1, prof: 'M. Lubin',   icon: '⚽', color: '#ef4444' },
  { matiere: 'Anglais',          note: 12.5, coef: 2, prof: 'Mme. Claire',  icon: '🌐', color: '#8b5cf6' },
  { matiere: 'Arts Plastiques',  note: 17.0, coef: 1, prof: 'M. Robert',    icon: '🎨', color: '#ec4899' },
])

const coursAujourdhui = ref([
  { heure: '07h30', matiere: 'Mathématiques',  salle: 'A12', prof: 'M. Pierre',   statut: 'terminé' },
  { heure: '09h00', matiere: 'Français',        salle: 'B04', prof: 'Mme. Marie',  statut: 'terminé' },
  { heure: '10h30', matiere: 'Sciences',        salle: 'Labo', prof: 'M. André',   statut: 'en cours' },
  { heure: '13h00', matiere: 'Histoire-Géo',    salle: 'A08', prof: 'Mme. Sophie', statut: 'à venir' },
  { heure: '14h30', matiere: 'Anglais',         salle: 'B12', prof: 'Mme. Claire', statut: 'à venir' },
])

const paiements = ref([
  { mois: 'Septembre 2024', montant: 3500,  statut: 'payé',    date: '02/09/2024' },
  { mois: 'Octobre 2024',   montant: 3500,  statut: 'payé',    date: '01/10/2024' },
  { mois: 'Novembre 2024',  montant: 3500,  statut: 'payé',    date: '04/11/2024' },
  { mois: 'Décembre 2024',  montant: 3500,  statut: 'payé',    date: '02/12/2024' },
  { mois: 'Janvier 2025',   montant: 3500,  statut: 'payé',    date: '06/01/2025' },
  { mois: 'Février 2025',   montant: 3500,  statut: 'en attente', date: '—' },
])

const annonces = ref([
  // { titre: 'Examen de Mathématiques',  date: '20 Fév 2025', type: 'examen',   desc: 'Chapitres 5 à 8 — fractions et géométrie' },
  // { titre: 'Sortie pédagogique',        date: '25 Fév 2025', type: 'sortie',   desc: 'Visite du musée national — apporter autorisation signée' },
  // { titre: 'Réunion parents-professeurs', date: '28 Fév 2025', type: 'reunion', desc: 'De 16h à 19h en salle polyvalente' },
  // { titre: 'Fête de l\'école',           date: '15 Mar 2025', type: 'evenement', desc: 'Programme culturel et sportif — entrée libre' },
  { titre: 'Aucune annonce',           date: `${new Date().toLocaleDateString('fr-FR', { weekday:'long', day:'numeric', month:'long', year:'numeric' })}`, type: 'aucune', desc: 'Aucune annonce' },
])

/* ── Graphique barres (notes) — dessiné en SVG natif ── */
const svgWidth  = 560
const svgHeight = 160
const barWidth  = 44
const gap       = 20


const bars = computed(() => {
  return notes.value.map((n, i) => {
    const x = i * (barWidth + gap) + gap
    const pourcentage = (n.note / n.noteMax) * 100
    const barH = (pourcentage / 100) * (svgHeight - 30)
    const y = svgHeight - barH - 20
    
    return {
      x, y, barH,
      noteDisplay: `${n.note}/${n.noteMax}`,  // "8.5/10" ou "15/20"
      color: n.color,
      label: n.matiere.substring(0, 4)
    }
  })
})

/* ── Graphique linéaire — évolution de la moyenne ── */


// const linePoints = computed(() => {
//   if (!evolutionData.value || evolutionData.value.length === 0) return [] // 👈
//   const w = 500, h = 100, pad = 20
//   return evolutionData.value.map((d, i) => {
//     const x = pad + (i / (evolutionData.value.length - 1)) * (w - pad * 2)
//     const y = h - pad - ((d.moy - 10) / 10) * (h - pad * 2)
//     return { x, y, ...d }
//   })
// })

const linePoints = computed(() => {
  if (!evolutionData.value || evolutionData.value.length === 0) return []
  const w = 500, pad = 20
  const moys = evolutionData.value.map(d => d.moy)
  const minY = Math.max(0, Math.min(...moys) - 1)  // min - 1 pour marge
  const maxY = Math.min(10, Math.max(...moys) + 1)  // max + 1 pour marge

  return evolutionData.value.map((d, i) => {
    const x = pad + (i / (evolutionData.value.length - 1)) * (w - pad * 2)
    const y = 120 - ((d.moy - minY) / (maxY - minY)) * 80
    return { x, y, ...d }
  })
})

const gridLines = computed(() => {
  if (!evolutionData.value || evolutionData.value.length === 0) return []
  const moys = evolutionData.value.map(d => d.moy)
  const minY = Math.max(0, Math.min(...moys) - 1)
  const maxY = Math.min(10, Math.max(...moys) + 1)

  // Génère 4 lignes entre min et max
  return Array.from({ length: 4 }, (_, i) => {
    const val = parseFloat((minY + (i / 3) * (maxY - minY)).toFixed(1))
    const y = 120 - ((val - minY) / (maxY - minY)) * 80
    return { val, y }
  })
})

const polyline = computed(() => {
  if (linePoints.value.length === 0) return '' // 👈
  return linePoints.value.map(p => `${p.x},${p.y}`).join(' ')
})

// const polygonFill = computed(() => {
//   if (linePoints.value.length === 0) return '' // 👈
//   const pts = linePoints.value
//   const last = pts[pts.length - 1]
//   const first = pts[0]
//   return `${polyline.value} ${last.x},120 ${first.x},120`
// })

const polygonFill = computed(() => {
  if (linePoints.value.length === 0) return ''
  const pts = linePoints.value
  const last = pts[pts.length - 1]
  const first = pts[0]
  return `${polyline.value} ${last.x},120 ${first.x},120`
})



const evolutionTitre = computed(() => {
  if (!notess.value || notess.value.length === 0) return ''
  const premier = notess.value[0].mois
  const dernier = notess.value[notess.value.length - 1].mois
  return `${premier} → ${dernier}`
})

const evolutionDiff = computed(() => {
  const data = evolutionData.value
  if (data.length < 2) return null
  const diff = (data[data.length - 1].moy - data[0].moy).toFixed(1)
  return diff > 0 ? `+${diff} pts ↑` : `${diff} pts ↓`
})



const moyennePonderee = computed(() => {
  if (!notes.value.length) return '0.0'
  
  // Ramener chaque note sur 20, puis pondérer
  const total = notes.value.reduce((sum, n) => {
    const noteSur20 = n.noteMax ? (n.note / n.noteMax) * 10 : n.note
    return sum + (noteSur20 * n.coef)
  }, 0)
  
  const totalCoefs = notes.value.reduce((sum, n) => sum + n.coef, 0)
  
  return (total / totalCoefs).toFixed(1)
})

/* ── Jauge circulaire ── */
const gaugePercent = computed(() => (parseFloat(moyennePonderee.value) / 10) * 100)
const gaugeDash    = computed(() => {
  const circumference = 2 * Math.PI * 54
  return `${(gaugePercent.value / 100) * circumference} ${circumference}`
})

/* ── Onglet actif ── */
const activeTab = ref('apercu')
const tabs = [
  { id: 'apercu',   label: 'Aperçu',   icon: '🏠' },
  { id: 'notes',    label: 'Notes',    icon: '📊' },
  { id: 'emploi',   label: 'Emploi',   icon: '🕐' },
  // { id: 'paiements',label: 'Paiements',icon: '💳' },
  { id: 'annonces', label: 'Annonces', icon: '📢' },
]

/* ── Animation compteurs ── */
const animated = ref(false)

const getIconForMatiere = (matiere) =>{
  const icons = {
    'Grammaire': '📝',
    'Orthographe': '✍️',
    'Lecture': '📚',
    'Histoire': '🏛️',
    'Géographie': '🌍',
    'Sciences': '🔬',
    'Problème': '🧮',
    'Opération / Numération': '🔢',
    'Ecriture': '🖋️',
    'Travaux Manuels': '🎨',
    'Géometrie': '📐',
    'Civisme': '🤝',
    'Poésie': '📜',
    'Bible': '⛪',
    'Calcul Mental': '🧠',
    'Sport': '⚽',
    'Anglais': '🌐'
  };
  return icons[matiere] || '📘';
}

const getColorForMatiere=(matiere, type_matiere) =>{
  const baseColors = ['#10b981', '#6366f1', '#0ea5e9', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
  const oraleColors = ['#f97316', '#06b6d4', '#d946ef', '#14b8a6', '#f43f5e', '#84cc16', '#a855f7'];
  
  const colors = type_matiere === 'base' ? baseColors : oraleColors;
  const index = matiere.length % colors.length;
  return colors[index];
}
const allHeaders = ref(null)
  const MOIS_FR = {
  '01': 'Janvier', '02': 'Février', '03': 'Mars',
  '04': 'Avril', '05': 'Mai', '06': 'Juin',
  '07': 'Juillet', '08': 'Août', '09': 'Septembre',
  '10': 'Octobre', '11': 'Novembre', '12': 'Décembre'
}
onMounted(async () => {
  const now = new Date()
  const mois_numero = String(now.getMonth() + 1).padStart(2, '0')  // "03"
  mois_demande_.value = MOIS_FR[mois_numero]  // "Mars"
   console.log(mois_demande_);
    if (!authStore.user) await authStore.initializeAuth();
  setTimeout(() => { animated.value = true }, 100)


   
  const { data } = await axios.get(`/etudiant/${authStore.user.user.userable_id}`)
  console.log(data);
  const etudiant = data.data

  const dernierClasseEtudiant = etudiant.classes_etudiant?.at(-1);     
  const dernierEtudiantFaculte = etudiant.etudiant_facultes?.at(-1);
  const last_year = dernierClasseEtudiant?.annee_academiques?.annee_academique || "Non definie"
  student.value      = {
  prenom:     etudiant.prenom,
  nom:        etudiant.nom,
  identifiant:etudiant.identifiant,
  classe:     dernierClasseEtudiant?.classes?.nom_classe || "Non definie",
  niveau:     dernierClasseEtudiant?.niveaux?.name || "Non definie",
  photo:      null,
  annee:      last_year,
  }

  reload_data('all',last_year)

  reload_data_paie(last_year)
 

})

 

const reload_data = async (e,last_year)=>  {
  var mois = e
  // if(e.target != undefined){
  //   mois=e.target.value
  // }else{
  //   mois='all'
  // }
    try {      
  const response = await axios.post('/student-notes', {
    etudiant_id: authStore.user.user.userable_id,
    annee_academique: last_year ?? student.value?.annee,
    mois: mois
  });
  bulletinData.value = response.data
  const data = response.data.data_student;
  
  console.log('Données reçues response:', response.data);

  allHeaders.value =response.data?.allHeaders
  statsCards.value=[
  { label: 'Moyenne Générale', value: response.data?.result.moyenne, unit: '/10', icon: '📊', color: 'emerald', trend: '' },
  { label: 'Absences',         value: '-',    unit: 'jours', icon: '📅', color: 'amber',   trend: '0 ce mois-ci' },
  { label: 'Cours validés',    value: '-',    unit: '/11',   icon: '✅', color: 'sky',     trend: '- en cours' },
  { label: 'Rang de classe',   value: response.data?.result.rang,    unit: 'ème',   icon: '🏅', color: 'violet',  trend: `sur ${response.data?.student_value} élèves` },
]

  // const note_octobre = details.notes["Octobre"];  // 11

  // // Ou avec une variable
  // const mois = "Octobre";
  // const note_mois = details.notes[mois];  // 11

  // // Dans votre transformation
  // return {
  //   matiere: matiere,
  //   note: details.notes["Octobre"],  // Note d'Octobre seulement
  //   coef: parseInt(details.coefficients),
  //   // ...
  // };
  

  const mois_demande = 'all'; 

  notes.value = 
    Object.entries(data.data_etudiant).map(([matiere, details]) => {
      // Calculer la moyenne des notes si nécessaire
      // if (details.notes[mois_demande]){

      // }
      const notes_mensuelles = Object.values(details.notes);
      const moyenne = notes_mensuelles.reduce((a, b) => a + b, 0) / notes_mensuelles.length;

        // Object.entries(data_etudiant).map(([matiere, details]) => {
        let note_a_afficher;
        
        if (mois_demande === 'all') {
          // Moyenne de tous les mois
          const notes = Object.values(details.notes);
          note_a_afficher = notes.reduce((a, b) => a + b, 0) / notes.length;
        } else {
          // Note d'un mois spécifique
          note_a_afficher = details.notes[mois_demande] || 0;
        }
      
      return {
        matiere: matiere,
        note: Math.round(note_a_afficher * 10) / 10, // Arrondir à 1 décimale
        coef: parseInt(details.coefficients),
        noteMax: details.coefficients ?? 20,
        prof: details.professeur_id, // Ou chercher le nom du prof si vous avez une table
        icon: getIconForMatiere(matiere),
        color: getColorForMatiere(matiere)
      };
    })

  
} catch (error) {
  console.error('Erreur:', error.response?.data || error.message);
}
  
}

const reload_data_paie = async (last_year)=>  {  
    try {      
  const response = await axios.post('/student-paiments', {
    etudiant_id: authStore.user.user.userable_id,
    annee_academique: last_year ?? student.value?.annee
  });
  
  const data = response.data;
  
  console.log('Données reçues response:', data);
  
  await axios.post('/paiement-statut', {
      etudiant_id: authStore.user.user.userable_id,
      annee_id: last_year ?? student.value?.annee,
      mois: data?.show_paiement?.mois?.mois
    });

  await get_payment_status(last_year)
const mois = data?.show_paiement?.mois?.mois;

const check_echeance = Object.keys(mois).reduce((acc, key) => {
  const numero = parseInt(key.split("_")[1]);
  const suffix = numero === 1 ? "er" : "ème";
  const label = `${numero}${suffix} Versement`;
  acc[label] = mois[key];
  return acc;
}, {});


} catch (error) {
  console.error('Erreur:', error.response?.data || error.message);
}
  
}

const get_payment_status = async (last_year)=>{
  try {
    const response = await axios.post('/get-paiement-statut',{ 
      etudiant_id: authStore.user.user.userable_id,
    annee_academique: last_year  
    });
    const data = response.data;
    month_payes.value=response?.data?.mois_accessibles 
    console.log(data);
    
  } catch (error) {
    
  }
}
 
const getAppreciation = (pourcentage) => {
  if (pourcentage >= 80) return { label: '🌟 Excellent',  class: 'bg-emerald-100 text-emerald-700' }
  if (pourcentage >= 60) return { label: '👍 Bien',       class: 'bg-sky-100 text-sky-700'         }
  if (pourcentage >= 50) return { label: '⚠️ Passable',   class: 'bg-amber-100 text-amber-700'     }
  return                         { label: '❌ Insuffisant', class: 'bg-red-100 text-red-700'         }
}
 

const colorMap = {
  emerald: { bg: 'bg-emerald-50', text: 'text-emerald-600', ring: 'ring-emerald-200', dot: 'bg-emerald-500' },
  amber:   { bg: 'bg-amber-50',   text: 'text-amber-600',   ring: 'ring-amber-200',   dot: 'bg-amber-500'   },
  sky:     { bg: 'bg-sky-50',     text: 'text-sky-600',     ring: 'ring-sky-200',     dot: 'bg-sky-500'     },
  violet:  { bg: 'bg-violet-50',  text: 'text-violet-600',  ring: 'ring-violet-200',  dot: 'bg-violet-500'  },
}

const statutCoursClass = {
  'terminé':  'bg-slate-100 text-slate-500',
  'en cours': 'bg-emerald-100 text-emerald-700 ring-1 ring-emerald-300',
  'à venir':  'bg-sky-50 text-sky-600',
}

const statutPaiClass = {
  'payé':       'bg-emerald-100 text-emerald-700',
  'en attente': 'bg-amber-100 text-amber-700',
  'impayé':     'bg-red-100 text-red-700',
}

const typeAnnonce = {
  'examen':    { bg: 'bg-rose-50',    text: 'text-rose-600',    icon: '📝' },
  'sortie':    { bg: 'bg-sky-50',     text: 'text-sky-600',     icon: '🚌' },
  'reunion':   { bg: 'bg-violet-50',  text: 'text-violet-600',  icon: '👥' },
  'evenement': { bg: 'bg-amber-50',   text: 'text-amber-600',   icon: '🎉' },
  'aucune': { bg: 'bg-red-50',   text: 'text-amber-600',   icon: '' },
}

const notess = computed(() => { 
    const tousMois = new Set();
    Object.values(dataEtudiant.value).forEach(details => {
      Object.keys(details.notes).forEach(mois => tousMois.add(mois));
    });

    // Retourner un tableau par mois
    return [...tousMois].map(mois => ({
      mois,
      notes: Object.entries(dataEtudiant.value)
        .filter(([_, details]) => details.notes.hasOwnProperty(mois))
        .map(([matiere, details]) => ({
          matiere,
          note: Math.round(details.notes[mois] * 10) / 10,
          coef: parseInt(details.coefficients)
        }))
    })); 
});

const evolutionData = computed(() => {
  if (!notess.value || notess.value.length === 0) return []

  return notess.value.map(groupe => {
    const totalNote = groupe.notes.reduce((sum, m) => sum + m.note, 0)
    const totalCoef = groupe.notes.reduce((sum, m) => sum + m.coef, 0)
    const moy = totalCoef > 0 ? ((totalNote / totalCoef) * 10).toFixed(1) : 0

    return {
      mois: groupe.mois.substring(0, 3),
      moisFull: groupe.mois,  // 👈 nom complet pour comparer avec month_payes
      moy: parseFloat(moy)
    }
  })
})

const evolutionDatass = computed(() => {
  if (!notess.value || notess.value.length === 0) return []

  return notess.value.map(groupe => {
    const totalNote = groupe.notes?.reduce((sum, m) => sum + m.note, 0)
    const totalCoef = groupe.notes?.reduce((sum, m) => sum + m.coef, 0)
    const moy = totalCoef > 0 ? ((totalNote / totalCoef) * 10).toFixed(1) : 0

    return {
      mois: groupe.mois.substring(0, 3), // "Octobre" → "Oct"
      moy: parseFloat(moy)
    }
  })
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 pb-16 animate-[fadeUp_0.4s_ease_both]">

    <!-- ══ HERO BANNER ══ -->
    <div class="relative bg-gradient-to-br from-emerald-700 via-emerald-800 to-teal-900 overflow-hidden -mt-8">
      <!-- Pattern décoratif -->
      <div class="absolute inset-0 opacity-10">
        <svg width="100%" height="100%"><defs><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="white" stroke-width="1"/></pattern></defs><rect width="100%" height="100%" fill="url(#grid)"/></svg>
      </div>
      <div class="relative max-w-6xl mx-auto px-4 sm:px-6 py-8 flex flex-col sm:flex-row items-start sm:items-center gap-5">

        <!-- Avatar -->
        <div class="relative shrink-0">
          <div class="w-20 h-20 rounded-2xl bg-white/20 backdrop-blur ring-2 ring-white/30 flex items-center justify-center text-4xl shadow-xl">
            {{ student.prenom.charAt(0) }}{{ student.nom.charAt(0) }}
          </div>
          <span class="absolute -bottom-1.5 -right-1.5 w-5 h-5 bg-emerald-400 rounded-full border-2 border-emerald-800"></span>
        </div>

        <!-- Infos -->
        <div class="flex-1">
          <p class="text-emerald-300 text-xs font-semibold tracking-widest uppercase mb-0.5">Espace Étudiant</p>
          <h1 class="text-white text-2xl sm:text-3xl font-bold leading-tight">
            {{ student.prenom }} <span class="text-emerald-300">{{ student.nom }}</span>
          </h1>
          <div class="flex flex-wrap items-center gap-3 mt-2">
            <span class="inline-flex items-center gap-1.5 bg-white/10 text-white/80 text-xs px-3 py-1 rounded-full backdrop-blur">
              🏫 {{ student.classe }} — {{ student.niveau }}
            </span>
            <span class="inline-flex items-center gap-1.5 bg-white/10 text-white/80 text-xs px-3 py-1 rounded-full backdrop-blur">
              🪪 {{ student.identifiant }}
            </span>
            <span class="inline-flex items-center gap-1.5 bg-white/10 text-white/80 text-xs px-3 py-1 rounded-full backdrop-blur">
              📅 Année {{ student.annee }}
            </span>

             <!-- <span class="inline-flex items-center gap-1.5 bg-white/10 text-white/80 text-xs px-3 py-1 rounded-full backdrop-blur">
              <select @change="reload_data($event, last_year=null)" name="" id="" class="border border-0 focus:border-0 text-yellow-500 active:border-0">
                <option v-for="(index,value) in allHeaders" :key="value" :value="index">{{ index }}</option>
              </select>
            </span> -->
          </div>
        </div>

        <!-- Jauge moyenne -->
        <div class="flex flex-col items-center shrink-0">
          <svg width="128" height="128" viewBox="0 0 128 128" class="drop-shadow-lg">
            <circle cx="64" cy="64" r="54" fill="none" stroke="rgba(255,255,255,.15)" stroke-width="10"/>
            <circle cx="64" cy="64" r="54" fill="none" stroke="#34d399" stroke-width="10"
              stroke-linecap="round" :stroke-dasharray="gaugeDash" stroke-dashoffset="-1"
              transform="rotate(-90 64 64)"
              style="transition: stroke-dasharray 1.2s cubic-bezier(.4,0,.2,1)"/>
            <text x="64" y="58" text-anchor="middle" fill="white" font-size="22" font-weight="700" font-family="serif">{{ moyennePonderee }}</text>
            <text x="64" y="75" text-anchor="middle" fill="rgba(255,255,255,.6)" font-size="10">/10</text>
            <text x="64" y="90" text-anchor="middle" fill="#34d399" font-size="9" font-weight="600">MOY. GÉNÉRALE</text>
          </svg>
        </div>

      </div>

      <!-- Onglets -->
      <div class="relative max-w-6xl mx-auto px-4 sm:px-6">
        <div class="flex gap-1 overflow-x-auto scrollbar-hide pb-0">
          <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
            class="flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap transition-all border-b-2"
            :class="activeTab === tab.id
              ? 'border-emerald-400 text-white bg-white/10'
              : 'border-transparent text-white/60 hover:text-white hover:bg-white/5'">
            <span>{{ tab.icon }}</span>
            <span>{{ tab.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ══ CONTENU ══ -->
    <div class="max-w-6xl mx-auto px-4 sm:px-6 pt-6 space-y-6">

      <!-- ████ APERÇU ████ -->
      <template v-if="activeTab === 'apercu'">

        <!-- Cartes stats -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="(card, i) in statsCards" :key="i"
            class="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm hover:shadow-md transition-shadow"
            :style="`animation-delay: ${i * 80}ms`">
            <div class="flex items-start justify-between mb-3">
              <span class="text-2xl">{{ card.icon }}</span>
              <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                :class="[colorMap[card.color].bg, colorMap[card.color].text]">
                {{ card.trend }}
              </span>
            </div>
            <div class="flex items-baseline gap-1">
              <span class="text-3xl font-bold text-slate-800" :class="colorMap[card.color].text">{{ card.value }}</span>
              <span class="text-sm text-slate-400">{{ card.unit }}</span>
            </div>
            <p class="text-xs text-slate-500 mt-1 font-medium">{{ card.label }}</p>
          </div>
        </div>

        <!-- {{notess}} -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Graphique évolution -->
          <!-- <div class="lg:col-span-2 bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
            <div class="flex items-center justify-between mb-5">
              <div>
                <h3 class="font-bold text-slate-800">Évolution de la moyenne</h3> 
                 <p class="text-xs text-slate-400 mt-0.5">{{ evolutionTitre ?? '' }}</p>
              </div>
  
              <span class="text-xs font-semibold px-2.5 py-1 rounded-full"
                :class="evolutionDiff?.startsWith('+') ? 'text-emerald-600 bg-emerald-50' : 'text-red-500 bg-red-50'">
                {{ evolutionDiff }}
              </span>
            </div>
            <svg :width="svgWidth" height="150" viewBox="0 0 520 140" class="w-full overflow-visible"  v-if="linePoints.length > 0">
           
              <line v-for="y in [4,6,8,10]" :key="y"
                x1="20" :y1="120 - ((y-10)/10)*80" x2="500" :y2="120 - ((y-10)/10)*80"
                stroke="#f1f5f9" stroke-width="1"/>
             
              <text v-for="y in [4,6,8,10]" :key="'l'+y"
                x="14" :y="124 - ((y-10)/10)*80"
                fill="#94a3b8" font-size="9" text-anchor="end">{{ y }}</text>
              
              <polygon :points="polygonFill" fill="url(#grad)" opacity="0.3"/>
              <defs>
                <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#10b981"/>
                  <stop offset="100%" stop-color="#10b981" stop-opacity="0"/>
                </linearGradient>
              </defs>
             
              <polyline :points="polyline" fill="none" stroke="#10b981" stroke-width="2.5"
                stroke-linecap="round" stroke-linejoin="round"/>
            
              <g v-for="(p, i) in linePoints" :key="i">
                <circle :cx="p.x" :cy="p.y" r="5" fill="white" stroke="#10b981" stroke-width="2.5"/>
                <text :x="p.x" :y="p.y - 10" fill="#10b981" font-size="9" font-weight="700" text-anchor="middle">{{ p.moy }}</text>
                <text :x="p.x" y="135" fill="#94a3b8" font-size="9" text-anchor="middle">{{ p.mois }}</text>
              </g>
            </svg>
          </div> -->

          <div class="lg:col-span-2 bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
            <div class="flex items-center justify-between mb-5">
              <div>
                <h3 class="font-bold text-slate-800">Évolution de la moyenne</h3>
                <p class="text-xs text-slate-400 mt-0.5">{{ evolutionTitre ?? '' }}</p>
              </div>
              <span class="text-xs font-semibold px-2.5 py-1 rounded-full"
                :class="evolutionDiff?.startsWith('+') ? 'text-emerald-600 bg-emerald-50' : 'text-red-500 bg-red-50'">
                {{ evolutionDiff }}
              </span>
            </div>

            <svg :width="svgWidth" height="150" viewBox="0 0 520 140" class="w-full overflow-visible" v-if="linePoints.length > 0">
              
              <!-- Grilles -->
               <line v-for="g in gridLines" :key="g.val"
                x1="20" :y1="g.y" x2="500" :y2="g.y"
                stroke="#f1f5f9" stroke-width="1"/>
              <!-- <line v-for="y in [4,6,8,10]" :key="y"
                x1="20" :y1="120 - ((y-10)/10)*80" x2="500" :y2="120 - ((y-10)/10)*80"
                stroke="#f1f5f9" stroke-width="1"/> -->

              <!-- Labels Y -->
               <text v-for="g in gridLines" :key="'l'+g.val"
                  x="14" :y="g.y + 4"
                  fill="#94a3b8" font-size="9" text-anchor="end">{{ g.val }}</text>
              <!-- <text v-for="y in [4,6,8,10]" :key="'l'+y"
                x="14" :y="124 - ((y-10)/10)*80"
                fill="#94a3b8" font-size="9" text-anchor="end">{{ y }}</text> -->

              <defs>
                <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"
                    :stop-color="evolutionData.at(-1)?.moy < 5 ? '#ef4444' : evolutionData.at(-1)?.moy < 6 ? '#f59e0b' : '#10b981'"/>
                  <stop offset="100%"
                    :stop-color="evolutionData.at(-1)?.moy < 5 ? '#ef4444' : evolutionData.at(-1)?.moy < 6 ? '#f59e0b' : '#10b981'"
                    stop-opacity="0"/>
                </linearGradient>
              </defs>

              <!-- Aire remplie -->
              <polygon :points="polygonFill" fill="url(#grad)" opacity="0.3"/>

              <!-- Ligne -->
              <polyline :points="polyline" fill="none"
                :stroke="evolutionData.at(-1)?.moy < 5 ? '#ef4444' : evolutionData.at(-1)?.moy < 6 ? '#f59e0b' : '#10b981'"
                stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>

              <!-- Points -->
               <!-- Points -->
              <g v-for="(p, i) in linePoints" :key="i">
                <circle :cx="p.x" :cy="p.y" r="5" fill="white"
                  :stroke="p.moy < 5 ? '#ef4444' : p.moy < 6 ? '#f59e0b' : '#10b981'"
                  stroke-width="2.5"/>
                <text :x="p.x" :y="p.y - 10"
                  :fill="p.moy < 5 ? '#ef4444' : p.moy < 6 ? '#f59e0b' : '#10b981'"
                  font-size="9" font-weight="700" text-anchor="middle">{{ p.moy }}</text>
                <text :x="p.x" y="135" fill="#94a3b8" font-size="9" text-anchor="middle">{{ p.mois }}</text>

                <!-- 🔒 Cadenas si mois non payé -->
                <g v-if="month_payes && !month_payes.includes(p.moisFull)">
                  <rect :x="p.x - 8" :y="p.y - 8" width="16" height="16" rx="3"
                    fill="white" stroke="#e2e8f0" stroke-width="1" opacity="0.9"/>
                  <text :x="p.x" :y="p.y + 5"
                    font-size="10" text-anchor="middle">🔒</text>
                </g>

              </g>
              <!-- <g v-for="(p, i) in linePoints" :key="i">
                <circle :cx="p.x" :cy="p.y" r="5" fill="white"
                  :stroke="p.moy < 5 ? '#ef4444' : p.moy < 6 ? '#f59e0b' : '#10b981'"
                  stroke-width="2.5"/>
                <text :x="p.x" :y="p.y - 10"
                  :fill="p.moy < 5 ? '#ef4444' : p.moy < 6 ? '#f59e0b' : '#10b981'"
                  font-size="9" font-weight="700" text-anchor="middle">{{ p.moy }}</text>
                <text :x="p.x" y="135" fill="#94a3b8" font-size="9" text-anchor="middle">{{ p.mois }}</text>
              </g> -->

            </svg>

            <div v-else class="text-center text-slate-400 text-sm py-10">
              Aucune donnée disponible
            </div>
          </div>

          <!-- Cours aujourd'hui (aperçu 3) -->
          <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-bold text-slate-800">Aujourd'hui</h3>
              <button @click="activeTab='emploi'"
                class="text-xs text-sky-600 hover:underline font-medium">Voir tout →</button>
            </div>
            <div class="space-y-2.5">
              <div v-for="cours in coursAujourdhui.slice(0,4)" :key="cours.heure"
                class="flex items-center gap-3 p-2.5 rounded-xl transition-colors"
                :class="cours.statut === 'en cours' ? 'bg-emerald-50 ring-1 ring-emerald-200' : 'hover:bg-slate-50'">
                <span class="text-xs font-mono font-bold text-slate-400 w-10 shrink-0">{{ cours.heure }}</span>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-semibold text-slate-700 truncate">{{ cours.matiere }}</p>
                  <p class="text-xs text-slate-400">Salle {{ cours.salle }}</p>
                </div>
                <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full shrink-0"
                  :class="statutCoursClass[cours.statut]">
                  {{ cours.statut }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Annonces récentes (aperçu) -->
        <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-bold text-slate-800">Annonces récentes</h3>
            <button @click="activeTab='annonces'" class="text-xs text-sky-600 hover:underline font-medium">Voir tout →</button>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <div v-for="a in annonces" :key="a.titre"
              class="rounded-xl p-4 border border-slate-100 hover:shadow-sm transition-shadow"
              :class="typeAnnonce[a.type].bg">
              <div class="flex items-center gap-2 mb-2">
                <span class="text-lg">{{ typeAnnonce[a.type].icon }}</span>
                <span class="text-[10px] font-bold uppercase tracking-wider" :class="typeAnnonce[a.type].text">{{ a.type }}</span>
              </div>
              <p class="text-sm font-semibold text-slate-800 leading-tight">{{ a.titre }}</p>
              <p class="text-xs text-slate-500 mt-1">{{ a.date }}</p>
            </div>
          </div>
        </div>

      </template>

      <!-- ████ NOTES ████ -->
      <template v-if="activeTab === 'notes'">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

          <!-- Graphique barres -->
          <div class="lg:col-span-2 bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
            <h3 class="font-bold text-slate-800 mb-1">Notes par matière</h3>
            <p class="text-xs text-slate-400 mb-5">1er trimestre — résultats pondérés</p>
            <div class="overflow-x-auto">
              <svg :width="svgWidth" :height="svgHeight + 40" :viewBox="`0 0 ${svgWidth} ${svgHeight + 40}`" class="w-full">
                <!-- Ligne de fond -->
                <line x1="0" :y1="svgHeight - 20" :x2="svgWidth" :y2="svgHeight - 20" stroke="#f1f5f9" stroke-width="1"/>
                <!-- Ligne 10/20 -->
                <line x1="0" :y1="svgHeight - 20 - ((10/20)*(svgHeight-30))" :x2="svgWidth" :y2="svgHeight - 20 - ((10/20)*(svgHeight-30))"
                  stroke="#fca5a5" stroke-width="1" stroke-dasharray="4,4"/>
                <text x="4" :y="svgHeight - 22 - ((10/20)*(svgHeight-30))" fill="#fca5a5" font-size="8">10/20</text>
                <g v-for="(bar, i) in bars" :key="i">
                  <rect :x="bar.x" :y="bar.y" :width="barWidth" :height="bar.barH"
                    :fill="bar.color" rx="6" opacity="0.85"
                    class="transition-all duration-700 hover:opacity-100"/>
                  <text :x="bar.x + barWidth/2" :y="bar.y - 5"
                    fill="#334155" font-size="10" font-weight="700" text-anchor="middle">{{ bar.note }}</text>
                  <text :x="bar.x + barWidth/2" :y="svgHeight + 14"
                    fill="#94a3b8" font-size="9" text-anchor="middle">{{ bar.label }}.</text>
                </g>
              </svg>
            </div>
          </div>

          <!-- Récap -->
          <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 flex flex-col">
            <h3 class="font-bold text-slate-800 mb-4">Bilan du trimestre</h3>
            <div class="space-y-2 flex-1">
              <div v-for="n in [...notes].sort((a,b) => b.note - a.note)" :key="n.matiere"
                class="flex items-center gap-3">
                <span class="text-base w-7 shrink-0">{{ n.icon }}</span>
                <div class="flex-1 min-w-0">
                  <div class="flex justify-between items-center mb-0.5">
                    <span class="text-xs font-medium text-slate-600 truncate">{{ n.matiere }}</span>
                    <span class="text-xs font-bold ml-2 shrink-0" :style="`color:${n.color}`">{{ n.note }}/{{n.coef}}</span>
                  </div>
                  <div class="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-1000"
                      :style="`width:${(n.note/n.coef)*100}%; background:${n.color}`"></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
              <span class="text-sm font-semibold text-slate-500">Moyenne pondérée</span>
              <span class="text-2xl font-bold text-emerald-600">{{ moyennePonderee }}
                <!-- <span class="text-sm text-slate-400">/{{n.coef}}</span> -->
              </span>
            </div>
          </div>
        </div> 
        <!-- Tableau détaillé -->
        <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
          <div class="px-5 py-4 border-b border-slate-100">
            <h3 class="font-bold text-slate-800">Détail des notes</h3>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-400">
                  <th class="px-5 py-3 text-left font-semibold">Matière</th>
                  <!-- <th class="px-5 py-3 text-left font-semibold">Professeur</th> -->
                  <th class="px-5 py-3 text-center font-semibold">Coef.</th>
                  <th class="px-5 py-3 text-center font-semibold">Note</th>
                  <th class="px-5 py-3 text-left font-semibold">Appréciation</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-50" v-if="month_payes && month_payes.includes(mois_demande_)">
                <tr v-for="n in notes" :key="n.matiere" class="hover:bg-slate-50 transition-colors">
                  <td class="px-5 py-3.5">
                    <div class="flex items-center gap-2.5">
                      <span class="text-lg">{{ n.icon }}</span>
                      <span class="font-medium text-slate-700">{{ n.matiere }}</span>
                    </div>
                  </td>
                  <!-- <td class="px-5 py-3.5 text-slate-500">{{ n.prof }}</td> -->
                  <td class="px-5 py-3.5 text-center">
                    <span class="bg-slate-100 text-slate-600 text-xs font-bold px-2 py-0.5 rounded-md">×{{ n.coef }}</span>
                  </td>
                  <td class="px-5 py-3.5 text-center">
                    <span class="text-base font-bold" :style="`color:${n.color}`">{{ n.note }}</span>
                    <span class="text-slate-400 text-xs">/{{ n.coef }}</span>
                  </td>
      
             <td class="px-5 py-3.5">
                <span class="text-xs px-2.5 py-1 rounded-full font-medium"
                  :class="getAppreciation((n.note / n.coef) * 100).class">
                  {{ getAppreciation((n.note / n.coef) * 100).label }}
                </span>
              </td>
                </tr>
              </tbody>
              <tbody class="divide-y divide-slate-50" v-else>
                <tr><td colspan="4" class="text-center py-2">🔒 </td></tr>
                 </tbody>
            </table>
          </div>
        </div>
      </template>

      <!-- ████ EMPLOI DU TEMPS ████ -->
      <template v-if="activeTab === 'emploi'">
        <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
          <div class="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 class="font-bold text-slate-800">Emploi du temps — Aujourd'hui</h3>
              <p class="text-xs text-slate-400 mt-0.5">{{ new Date().toLocaleDateString('fr-FR', { weekday:'long', day:'numeric', month:'long', year:'numeric' }) }}</p>
            </div>
            <span class="text-xs font-semibold bg-emerald-50 text-emerald-600 px-3 py-1 rounded-full">
              {{ coursAujourdhui.filter(c => c.statut === 'en cours').length }} en cours
            </span>
          </div>
          <div class="divide-y divide-slate-50">
            <div v-for="cours in coursAujourdhui" :key="cours.heure"
              class="flex items-center gap-4 px-5 py-4 transition-colors"
              :class="cours.statut === 'en cours' ? 'bg-emerald-50' : 'hover:bg-slate-50'">

              <!-- Heure -->
              <div class="w-16 shrink-0 text-center">
                <span class="text-sm font-mono font-bold text-slate-700">{{ cours.heure }}</span>
              </div>

              <!-- Indicateur -->
              <div class="w-1 h-12 rounded-full shrink-0"
                :class="cours.statut === 'en cours' ? 'bg-emerald-500'
                      : cours.statut === 'terminé'  ? 'bg-slate-200'
                      :                               'bg-sky-300'"></div>

              <!-- Infos -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <p class="font-semibold text-slate-800">{{ cours.matiere }}</p>
                  <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                    :class="statutCoursClass[cours.statut]">
                    {{ cours.statut }}
                  </span>
                </div>
                <p class="text-xs text-slate-400 mt-0.5">{{ cours.prof }} · Salle {{ cours.salle }}</p>
              </div>

              <!-- Icône statut -->
              <div class="shrink-0 text-xl">
                {{ cours.statut === 'en cours' ? '🟢' : cours.statut === 'terminé' ? '✅' : '🕐' }}
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ████ PAIEMENTS ████ -->
      <template v-if="activeTab === 'paiements'">

        <!-- Résumé -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
            <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Total payé</p>
            <p class="text-3xl font-bold text-emerald-600">
              {{ paiements.filter(p => p.statut === 'payé').reduce((s,p) => s + p.montant, 0).toLocaleString() }}
              <span class="text-sm font-normal text-slate-400">HTG</span>
            </p>
          </div>
          <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
            <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">En attente</p>
            <p class="text-3xl font-bold text-amber-500">
              {{ paiements.filter(p => p.statut !== 'payé').reduce((s,p) => s + p.montant, 0).toLocaleString() }}
              <span class="text-sm font-normal text-slate-400">HTG</span>
            </p>
          </div>
          <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
            <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Mois payés</p>
            <p class="text-3xl font-bold text-slate-800">
              {{ paiements.filter(p => p.statut === 'payé').length }}
              <span class="text-sm font-normal text-slate-400">/ {{ paiements.length }}</span>
            </p>
          </div>
        </div>

        <!-- Tableau paiements -->
        <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
          <div class="px-5 py-4 border-b border-slate-100">
            <h3 class="font-bold text-slate-800">Historique des paiements</h3>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-400">
                  <th class="px-5 py-3 text-left font-semibold">Période</th>
                  <th class="px-5 py-3 text-right font-semibold">Montant</th>
                  <th class="px-5 py-3 text-center font-semibold">Statut</th>
                  <th class="px-5 py-3 text-center font-semibold">Date</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-50">
                <tr v-for="p in paiements" :key="p.mois" class="hover:bg-slate-50 transition-colors">
                  <td class="px-5 py-3.5 font-medium text-slate-700">{{ p.mois }}</td>
                  <td class="px-5 py-3.5 text-right font-bold text-slate-800">
                    {{ p.montant.toLocaleString() }} <span class="text-xs text-slate-400 font-normal">HTG</span>
                  </td>
                  <td class="px-5 py-3.5 text-center">
                    <span class="text-xs font-semibold px-3 py-1 rounded-full"
                      :class="statutPaiClass[p.statut]">
                      {{ p.statut === 'payé' ? '✅ ' : '⏳ ' }}{{ p.statut }}
                    </span>
                  </td>
                  <td class="px-5 py-3.5 text-center text-slate-500 font-mono text-xs">{{ p.date }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>

      <!-- ████ ANNONCES ████ -->
      <template v-if="activeTab === 'annonces'">
        <div class="space-y-4">
          <div v-for="a in annonces" :key="a.titre"
            class="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 hover:shadow-md transition-shadow flex gap-4">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shrink-0"
              :class="typeAnnonce[a.type].bg">
              {{ typeAnnonce[a.type].icon }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-3 flex-wrap">
                <h4 class="font-bold text-slate-800">{{ a.titre }}</h4>
                <div class="flex items-center gap-2 shrink-0">
                  <span class="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full"
                    :class="[typeAnnonce[a.type].bg, typeAnnonce[a.type].text]">
                    {{ a.type }}
                  </span>
                  <span class="text-xs text-slate-400 font-medium">📅 {{ a.date }}</span>
                </div>
              </div>
              <p class="text-sm text-slate-500 mt-1.5 leading-relaxed">{{ a.desc }}</p>
            </div>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>