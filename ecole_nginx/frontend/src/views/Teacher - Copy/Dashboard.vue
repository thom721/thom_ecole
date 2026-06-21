<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router'; 

const router = useRouter();

// Données fictives du professeur
const teacher = ref({
  nom: 'Jean-Baptiste',
  prenom: 'Dubois',
  photo: 'https://i.pravatar.cc/150?img=12',
  matiere: 'Mathématiques',
  grade: 'Professeur Agrégé',
  email: 'jb.dubois@ecole.com',
  telephone: '+509 3456-7890'
});

// Statistiques générales
const stats = ref({
  totalClasses: 5,
  totalEleves: 156,
  coursAujourdhui: 4,
  evaluationsPendantes: 8,
  moyenneGenerale: 14.5,
  tauxReussite: 87,
  absencesAujourdhui: 12,
  devoirs: 23
});

// Classes du professeur
const classes = ref([
  {
    id: 1,
    nom: '3ème A',
    niveau: 'Secondaire',
    effectif: 32,
    moyenne: 15.2,
    couleur: 'bg-blue-500',
    prochainCours: '2025-02-13 08:00',
    progression: 78
  },
  {
    id: 2,
    nom: '3ème B',
    niveau: 'Secondaire',
    effectif: 30,
    moyenne: 13.8,
    couleur: 'bg-green-500',
    prochainCours: '2025-02-13 10:00',
    progression: 75
  },
  {
    id: 3,
    nom: '4ème A',
    niveau: 'Secondaire',
    effectif: 28,
    moyenne: 14.6,
    couleur: 'bg-purple-500',
    prochainCours: '2025-02-13 13:00',
    progression: 82
  },
  {
    id: 4,
    nom: '4ème B',
    niveau: 'Secondaire',
    effectif: 34,
    moyenne: 12.9,
    couleur: 'bg-orange-500',
    prochainCours: '2025-02-13 15:00',
    progression: 70
  },
  {
    id: 5,
    nom: '5ème A',
    niveau: 'Secondaire',
    effectif: 32,
    moyenne: 16.1,
    couleur: 'bg-pink-500',
    prochainCours: '2025-02-14 08:00',
    progression: 85
  }
]);

// Emploi du temps aujourd'hui
const emploiDuTemps = ref([
  {
    id: 1,
    heure: '08:00 - 09:30',
    classe: '3ème A',
    matiere: 'Mathématiques',
    salle: 'B203',
    statut: 'en_cours',
    couleur: 'bg-green-100 border-green-500 text-green-700'
  },
  {
    id: 2,
    heure: '10:00 - 11:30',
    classe: '3ème B',
    matiere: 'Mathématiques',
    salle: 'B203',
    statut: 'a_venir',
    couleur: 'bg-blue-100 border-blue-500 text-blue-700'
  },
  {
    id: 3,
    heure: '13:00 - 14:30',
    classe: '4ème A',
    matiere: 'Mathématiques',
    salle: 'B205',
    statut: 'a_venir',
    couleur: 'bg-blue-100 border-blue-500 text-blue-700'
  },
  {
    id: 4,
    heure: '15:00 - 16:30',
    classe: '4ème B',
    matiere: 'Mathématiques',
    salle: 'B203',
    statut: 'a_venir',
    couleur: 'bg-blue-100 border-blue-500 text-blue-700'
  }
]);

// Évaluations à corriger
const evaluations = ref([
  {
    id: 1,
    titre: 'Contrôle Algèbre',
    classe: '3ème A',
    date: '2025-02-10',
    copies: 32,
    corrigees: 24,
    restantes: 8,
    progression: 75
  },
  {
    id: 2,
    titre: 'Devoir Géométrie',
    classe: '3ème B',
    date: '2025-02-11',
    copies: 30,
    corrigees: 18,
    restantes: 12,
    progression: 60
  },
  {
    id: 3,
    titre: 'Test Équations',
    classe: '4ème A',
    date: '2025-02-09',
    copies: 28,
    corrigees: 28,
    restantes: 0,
    progression: 100
  },
  {
    id: 4,
    titre: 'Interrogation Fractions',
    classe: '5ème A',
    date: '2025-02-12',
    copies: 32,
    corrigees: 0,
    restantes: 32,
    progression: 0
  }
]);

// Élèves nécessitant une attention
const elevesAttention = ref([
  {
    id: 1,
    nom: 'Marie Dupont',
    classe: '3ème A',
    photo: 'https://i.pravatar.cc/100?img=5',
    raison: 'Baisse de moyenne',
    moyenneActuelle: 8.5,
    moyennePrecedente: 13.2,
    urgence: 'haute',
    couleur: 'text-red-600'
  },
  {
    id: 2,
    nom: 'Pierre Martin',
    classe: '4ème B',
    photo: 'https://i.pravatar.cc/100?img=11',
    raison: 'Absences répétées',
    absences: 8,
    urgence: 'moyenne',
    couleur: 'text-orange-600'
  },
  {
    id: 3,
    nom: 'Sophie Laurent',
    classe: '3ème B',
    photo: 'https://i.pravatar.cc/100?img=9',
    raison: 'Retards fréquents',
    retards: 12,
    urgence: 'basse',
    couleur: 'text-yellow-600'
  }
]);

// Actualités et annonces
const actualites = ref([
  {
    id: 1,
    titre: 'Réunion pédagogique',
    description: 'Réunion des enseignants de mathématiques le 15 février à 14h',
    date: '2025-02-12',
    type: 'reunion',
    icone: 'ri-calendar-event-line',
    couleur: 'bg-purple-100 text-purple-700'
  },
  {
    id: 2,
    titre: 'Formation continue',
    description: 'Atelier sur les nouvelles méthodes d\'enseignement',
    date: '2025-02-20',
    type: 'formation',
    icone: 'ri-graduation-cap-line',
    couleur: 'bg-blue-100 text-blue-700'
  },
  {
    id: 3,
    titre: 'Conseil de classe',
    description: 'Conseil de classe des 3èmes prévu le 18 février',
    date: '2025-02-18',
    type: 'conseil',
    icone: 'ri-group-line',
    couleur: 'bg-green-100 text-green-700'
  }
]);

// Performances des classes (pour graphique)
const performancesClasses = ref([
  { classe: '3ème A', moyenne: 15.2 },
  { classe: '3ème B', moyenne: 13.8 },
  { classe: '4ème A', moyenne: 14.6 },
  { classe: '4ème B', moyenne: 12.9 },
  { classe: '5ème A', moyenne: 16.1 }
]);

// Absences par jour (dernière semaine)
const absencesParJour = ref([
  { jour: 'Lun', nombre: 8 },
  { jour: 'Mar', nombre: 12 },
  { jour: 'Mer', nombre: 6 },
  { jour: 'Jeu', nombre: 15 },
  { jour: 'Ven', nombre: 10 }
]);

// Computed
const heureActuelle = computed(() => {
  const now = new Date();
  return now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
});

const coursEnCours = computed(() => {
  return emploiDuTemps.value.find(c => c.statut === 'en_cours');
});

const prochainCours = computed(() => {
  return emploiDuTemps.value.find(c => c.statut === 'a_venir');
});


const totalEvaluationsRestantes = computed(() => {
  return evaluations.value.reduce((sum, evaluation) => sum + evaluation.restantes, 0);
});

// Methods
const navigateToClasse = (classeId) => {
  router.push(`/teacher/classes/${classeId}`);
};

const navigateToEvaluation = (evalId) => {
  router.push(`/teacher/evaluations/${evalId}`);
};

const navigateToEleve = (eleveId) => {
  router.push(`/teacher/students/${eleveId}`);
};

const getStatutBadge = (statut) => {
  const badges = {
    'en_cours': 'En cours',
    'a_venir': 'À venir',
    'termine': 'Terminé'
  };
  return badges[statut] || statut;
};

const getUrgenceColor = (urgence) => {
  const colors = {
    'haute': 'bg-red-100 border-red-500 text-red-700',
    'moyenne': 'bg-orange-100 border-orange-500 text-orange-700',
    'basse': 'bg-yellow-100 border-yellow-500 text-yellow-700'
  };
  return colors[urgence] || 'bg-gray-100';
};

onMounted(() => {
  // Animation au chargement
  console.log('Dashboard chargé');
});
</script>

<template>
  <!-- <TeacherLayout title="Tableau de Bord"> -->
    <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 pb-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
         
        <div class="mb-8 bg-white rounded-2xl shadow-lg p-6 border border-slate-200">
          <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div class="flex items-center gap-4">
              <div class="relative">
                <img 
                  :src="teacher.photo" 
                  alt="Photo professeur"
                  class="w-20 h-20 rounded-full border-4 border-blue-500 shadow-lg object-cover"
                >
                <div class="absolute -bottom-1 -right-1 bg-green-500 w-6 h-6 rounded-full border-4 border-white"></div>
              </div>
              <div>
                <h1 class="text-3xl font-bold text-slate-800">
                  Bonjour, {{ teacher.prenom }} !
                </h1>
                <p class="text-slate-600 text-lg">{{ teacher.grade }} - {{ teacher.matiere }}</p>
                <p class="text-slate-500 text-sm">{{ heureActuelle }}</p>
              </div>
            </div>
            
            <div class="flex gap-3">
              <button 
                class="px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                <i class="ri-calendar-line mr-2"></i>
                Mon emploi du temps
              </button>
              <button 
                class="px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl hover:from-purple-600 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                <i class="ri-book-open-line mr-2"></i>
                Mes cours
              </button>
            </div>
          </div>
        </div>

        <!-- Statistiques principales -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <!-- Stat 1 -->
          <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-lg p-6 text-white transform hover:scale-105 transition-all duration-300">
            <div class="flex items-center justify-between mb-4">
              <div class="bg-white/20 p-3 rounded-xl">
                <i class="ri-group-line text-3xl"></i>
              </div>
              <span class="text-4xl font-bold">{{ stats.totalEleves }}</span>
            </div>
            <h3 class="text-lg font-semibold opacity-90">Élèves</h3>
            <p class="text-sm opacity-75">Répartis dans {{ stats.totalClasses }} classes</p>
          </div>

          <!-- Stat 2 -->
          <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-lg p-6 text-white transform hover:scale-105 transition-all duration-300">
            <div class="flex items-center justify-between mb-4">
              <div class="bg-white/20 p-3 rounded-xl">
                <i class="ri-book-open-line text-3xl"></i>
              </div>
              <span class="text-4xl font-bold">{{ stats.coursAujourdhui }}</span>
            </div>
            <h3 class="text-lg font-semibold opacity-90">Cours aujourd'hui</h3>
            <p class="text-sm opacity-75">{{ stats.totalClasses }} classes à gérer</p>
          </div>

          <!-- Stat 3 -->
          <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl shadow-lg p-6 text-white transform hover:scale-105 transition-all duration-300">
            <div class="flex items-center justify-between mb-4">
              <div class="bg-white/20 p-3 rounded-xl">
                <i class="ri-file-list-3-line text-3xl"></i>
              </div>
              <span class="text-4xl font-bold">{{ totalEvaluationsRestantes }}</span>
            </div>
            <h3 class="text-lg font-semibold opacity-90">Copies à corriger</h3>
            <p class="text-sm opacity-75">{{ stats.evaluationsPendantes }} évaluations</p>
          </div>

          <!-- Stat 4 -->
          <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white transform hover:scale-105 transition-all duration-300">
            <div class="flex items-center justify-between mb-4">
              <div class="bg-white/20 p-3 rounded-xl">
                <i class="ri-line-chart-line text-3xl"></i>
              </div>
              <span class="text-4xl font-bold">{{ stats.moyenneGenerale }}/20</span>
            </div>
            <h3 class="text-lg font-semibold opacity-90">Moyenne générale</h3>
            <p class="text-sm opacity-75">{{ stats.tauxReussite }}% de réussite</p>
          </div>
        </div>

        <!-- Cours en cours / Prochain cours -->
        <div v-if="coursEnCours || prochainCours" class="mb-8">
          <div v-if="coursEnCours" class="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl shadow-lg p-6 text-white mb-4 animate-pulse">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4">
                <div class="bg-white/20 p-4 rounded-xl">
                  <i class="ri-live-line text-3xl"></i>
                </div>
                <div>
                  <h3 class="text-2xl font-bold mb-1">Cours en cours</h3>
                  <p class="text-lg opacity-90">{{ coursEnCours.classe }} - {{ coursEnCours.heure }}</p>
                  <p class="text-sm opacity-75">Salle {{ coursEnCours.salle }}</p>
                </div>
              </div>
              <button class="px-6 py-3 bg-white text-green-600 rounded-xl font-semibold hover:bg-green-50 transition-all">
                Voir les détails
              </button>
            </div>
          </div>

          <div v-if="prochainCours && !coursEnCours" class="bg-white rounded-2xl shadow-lg p-6 border-2 border-blue-500">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4">
                <div class="bg-blue-100 p-4 rounded-xl">
                  <i class="ri-time-line text-3xl text-blue-600"></i>
                </div>
                <div>
                  <h3 class="text-xl font-bold text-slate-800 mb-1">Prochain cours</h3>
                  <p class="text-lg text-slate-600">{{ prochainCours.classe }} - {{ prochainCours.heure }}</p>
                  <p class="text-sm text-slate-500">Salle {{ prochainCours.salle }}</p>
                </div>
              </div>
              <button class="px-6 py-3 bg-blue-500 text-white rounded-xl font-semibold hover:bg-blue-600 transition-all">
                Préparer le cours
              </button>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <!-- Emploi du temps du jour -->
          <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6 border border-slate-200">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-2xl font-bold text-slate-800 flex items-center gap-2">
                <i class="ri-calendar-line text-blue-600"></i>
                Emploi du temps - Aujourd'hui
              </h2>
              <button class="text-blue-600 hover:text-blue-700 font-semibold">
                Voir tout <i class="ri-arrow-right-line"></i>
              </button>
            </div>

            <div class="space-y-3">
              <div 
                v-for="cours in emploiDuTemps" 
                :key="cours.id"
                class="border-l-4 rounded-lg p-4 transition-all duration-300 hover:shadow-md cursor-pointer"
                :class="cours.couleur"
              >
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-4">
                    <div class="text-center">
                      <p class="text-sm font-semibold">{{ cours.heure.split(' - ')[0] }}</p>
                      <p class="text-xs opacity-75">{{ cours.heure.split(' - ')[1] }}</p>
                    </div>
                    <div class="h-12 w-px bg-slate-300"></div>
                    <div>
                      <h4 class="font-bold text-lg">{{ cours.classe }}</h4>
                      <p class="text-sm opacity-75">{{ cours.matiere }} - Salle {{ cours.salle }}</p>
                    </div>
                  </div>
                  <span 
                    class="px-3 py-1 rounded-full text-xs font-semibold"
                    :class="{
                      'bg-green-500 text-white': cours.statut === 'en_cours',
                      'bg-blue-500 text-white': cours.statut === 'a_venir',
                      'bg-gray-500 text-white': cours.statut === 'termine'
                    }"
                  >
                    {{ getStatutBadge(cours.statut) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Actualités -->
          <div class="bg-white rounded-2xl shadow-lg p-6 border border-slate-200">
            <h2 class="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
              <i class="ri-notification-3-line text-purple-600"></i>
              Actualités
            </h2>

            <div class="space-y-4">
              <div 
                v-for="actu in actualites" 
                :key="actu.id"
                class="rounded-xl p-4 transition-all duration-300 hover:shadow-md cursor-pointer"
                :class="actu.couleur"
              >
                <div class="flex items-start gap-3">
                  <i :class="actu.icone" class="text-2xl mt-1"></i>
                  <div class="flex-1">
                    <h4 class="font-bold mb-1">{{ actu.titre }}</h4>
                    <p class="text-sm opacity-75 mb-2">{{ actu.description }}</p>
                    <p class="text-xs font-semibold">{{ actu.date }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Mes classes -->
        <div class="mb-8 bg-white rounded-2xl shadow-lg p-6 border border-slate-200">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-slate-800 flex items-center gap-2">
              <i class="ri-school-line text-green-600"></i>
              Mes classes
            </h2>
            <button class="text-green-600 hover:text-green-700 font-semibold">
              Gérer <i class="ri-arrow-right-line"></i>
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            <div 
              v-for="classe in classes" 
              :key="classe.id"
              @click="navigateToClasse(classe.id)"
              class="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl p-5 border-2 border-slate-200 hover:border-blue-500 transition-all duration-300 cursor-pointer transform hover:-translate-y-2 hover:shadow-xl"
            >
              <div class="flex items-center justify-between mb-4">
                <div :class="classe.couleur" class="w-12 h-12 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-lg">
                  {{ classe.nom.charAt(0) }}
                </div>
                <span class="text-2xl">📚</span>
              </div>
              
              <h3 class="text-xl font-bold text-slate-800 mb-1">{{ classe.nom }}</h3>
              <p class="text-sm text-slate-600 mb-4">{{ classe.niveau }}</p>
              
              <div class="space-y-2 mb-4">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-slate-600">Élèves</span>
                  <span class="font-bold text-slate-800">{{ classe.effectif }}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-slate-600">Moyenne</span>
                  <span class="font-bold" :class="{
                    'text-green-600': classe.moyenne >= 14,
                    'text-orange-600': classe.moyenne >= 10 && classe.moyenne < 14,
                    'text-red-600': classe.moyenne < 10
                  }">
                    {{ classe.moyenne }}/20
                  </span>
                </div>
              </div>

              <div class="mb-2">
                <div class="flex items-center justify-between text-xs text-slate-600 mb-1">
                  <span>Progression</span>
                  <span class="font-semibold">{{ classe.progression }}%</span>
                </div>
                <div class="w-full bg-slate-200 rounded-full h-2">
                  <div 
                    class="h-2 rounded-full transition-all duration-500"
                    :class="classe.couleur"
                    :style="{ width: classe.progression + '%' }"
                  ></div>
                </div>
              </div>

              <p class="text-xs text-slate-500 mt-3">
                <i class="ri-time-line mr-1"></i>
                Prochain: {{ new Date(classe.prochainCours).toLocaleString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) }}
              </p>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <!-- Évaluations à corriger -->
          <div class="bg-white rounded-2xl shadow-lg p-6 border border-slate-200">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-2xl font-bold text-slate-800 flex items-center gap-2">
                <i class="ri-file-edit-line text-orange-600"></i>
                Évaluations à corriger
              </h2>
              <span class="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-bold">
                {{ totalEvaluationsRestantes }} copies
              </span>
            </div>

            <div class="space-y-4">
              <div 
                v-for="evaluation in evaluations" 
                :key="evaluation.id"
                @click="navigateToEvaluation(evaluation.id)"
                class="border-2 border-slate-200 rounded-xl p-4 hover:border-orange-500 transition-all duration-300 cursor-pointer hover:shadow-md"
              >
                <div class="flex items-start justify-between mb-3">
                  <div>
                    <h4 class="font-bold text-lg text-slate-800">{{ evaluation.titre }}</h4>
                    <p class="text-sm text-slate-600">{{ evaluation.classe }} - {{ evaluation.date }}</p>
                  </div>
                  <span 
                    class="px-3 py-1 rounded-full text-xs font-semibold"
                    :class="{
                      'bg-green-100 text-green-700': evaluation.progression === 100,
                      'bg-orange-100 text-orange-700': evaluation.progression > 0 && evaluation.progression < 100,
                      'bg-red-100 text-red-700': evaluation.progression === 0
                    }"
                  >
                    {{ evaluation.restantes }} restantes
                  </span>
                </div>

                <div class="mb-2">
                  <div class="flex items-center justify-between text-sm text-slate-600 mb-1">
                    <span>{{ evaluation.corrigees }}/{{ evaluation.copies }} corrigées</span>
                    <span class="font-semibold">{{ evaluation.progression }}%</span>
                  </div>
                  <div class="w-full bg-slate-200 rounded-full h-2">
                    <div 
                      class="h-2 rounded-full transition-all duration-500"
                      :class="{
                        'bg-green-500': evaluation.progression === 100,
                        'bg-orange-500': evaluation.progression > 0 && evaluation.progression < 100,
                        'bg-red-500': evaluation.progression === 0
                      }"
                      :style="{ width: evaluation.progression + '%' }"
                    ></div>
                  </div>
                </div>

                <button 
                  v-if="evaluation.restantes > 0"
                  class="mt-2 w-full py-2 bg-orange-500 text-white rounded-lg font-semibold hover:bg-orange-600 transition-all"
                >
                  Continuer la correction
                </button>
                <button 
                  v-else
                  class="mt-2 w-full py-2 bg-green-500 text-white rounded-lg font-semibold hover:bg-green-600 transition-all"
                >
                  Voir les résultats
                </button>
              </div>
            </div>
          </div>

          <!-- Élèves nécessitant attention -->
          <div class="bg-white rounded-2xl shadow-lg p-6 border border-slate-200">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-2xl font-bold text-slate-800 flex items-center gap-2">
                <i class="ri-alert-line text-red-600"></i>
                Suivi personnalisé
              </h2>
              <span class="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-bold">
                {{ elevesAttention.length }} élèves
              </span>
            </div>

            <div class="space-y-4">
              <div 
                v-for="eleve in elevesAttention" 
                :key="eleve.id"
                @click="navigateToEleve(eleve.id)"
                class="border-2 rounded-xl p-4 transition-all duration-300 cursor-pointer hover:shadow-md"
                :class="getUrgenceColor(eleve.urgence)"
              >
                <div class="flex items-start gap-3">
                  <img 
                    :src="eleve.photo" 
                    :alt="eleve.nom"
                    class="w-12 h-12 rounded-full border-2 border-white shadow-md object-cover"
                  >
                  <div class="flex-1">
                    <div class="flex items-start justify-between">
                      <div>
                        <h4 class="font-bold text-lg">{{ eleve.nom }}</h4>
                        <p class="text-sm opacity-75">{{ eleve.classe }}</p>
                      </div>
                      <span class="text-2xl">
                        {{ eleve.urgence === 'haute' ? '🔴' : eleve.urgence === 'moyenne' ? '🟠' : '🟡' }}
                      </span>
                    </div>
                    
                    <div class="mt-3 p-3 bg-white/50 rounded-lg">
                      <p class="text-sm font-semibold mb-1">{{ eleve.raison }}</p>
                      <p class="text-sm" v-if="eleve.moyenneActuelle">
                        Moyenne: {{ eleve.moyenneActuelle }}/20 
                        <span class="text-red-600">({{ eleve.moyennePrecedente }})</span>
                      </p>
                      <p class="text-sm" v-if="eleve.absences">
                        {{ eleve.absences }} absences ce mois
                      </p>
                      <p class="text-sm" v-if="eleve.retards">
                        {{ eleve.retards }} retards ce mois
                      </p>
                    </div>

                    <button class="mt-3 w-full py-2 bg-slate-800 text-white rounded-lg text-sm font-semibold hover:bg-slate-900 transition-all">
                      Contacter le responsable
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Graphiques performances -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Moyennes par classe -->
          <div class="bg-white rounded-2xl shadow-lg p-6 border border-slate-200">
            <h2 class="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
              <i class="ri-bar-chart-box-line text-blue-600"></i>
              Moyennes par classe
            </h2>

            <div class="space-y-4">
              <div 
                v-for="(perf, index) in performancesClasses" 
                :key="index"
                class="flex items-center gap-4"
              >
                <div class="w-24 text-sm font-semibold text-slate-700">
                  {{ perf.classe }}
                </div>
                <div class="flex-1">
                  <div class="flex items-center justify-between text-sm text-slate-600 mb-1">
                    <span class="font-semibold">{{ perf.moyenne }}/20</span>
                  </div>
                  <div class="w-full bg-slate-200 rounded-full h-3">
                    <div 
                      class="h-3 rounded-full transition-all duration-500"
                      :class="{
                        'bg-green-500': perf.moyenne >= 14,
                        'bg-orange-500': perf.moyenne >= 10 && perf.moyenne < 14,
                        'bg-red-500': perf.moyenne < 10
                      }"
                      :style="{ width: (perf.moyenne / 20 * 100) + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Absences de la semaine -->
          <div class="bg-white rounded-2xl shadow-lg p-6 border border-slate-200">
            <h2 class="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
              <i class="ri-user-unfollow-line text-red-600"></i>
              Absences cette semaine
            </h2>

            <div class="space-y-4">
              <div 
                v-for="(abs, index) in absencesParJour" 
                :key="index"
                class="flex items-center gap-4"
              >
                <div class="w-16 text-sm font-semibold text-slate-700">
                  {{ abs.jour }}
                </div>
                <div class="flex-1">
                  <div class="flex items-center justify-between text-sm text-slate-600 mb-1">
                    <span class="font-semibold">{{ abs.nombre }} absences</span>
                  </div>
                  <div class="w-full bg-slate-200 rounded-full h-3">
                    <div 
                      class="h-3 bg-gradient-to-r from-red-500 to-orange-500 rounded-full transition-all duration-500"
                      :style="{ width: (abs.nombre / 20 * 100) + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-6 p-4 bg-red-50 border-2 border-red-200 rounded-xl">
              <p class="text-sm text-red-700 flex items-center gap-2">
                <i class="ri-information-line text-xl"></i>
                <span><strong>{{ stats.absencesAujourdhui }}</strong> élèves absents aujourd'hui</span>
              </p>
            </div>
          </div>
        </div>

        <!-- Actions rapides -->
        <div class="mt-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
          <h2 class="text-2xl font-bold mb-6">Actions rapides</h2>
          
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button class="bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-xl p-4 transition-all duration-300 transform hover:scale-105">
              <i class="ri-file-add-line text-3xl mb-2"></i>
              <p class="text-sm font-semibold">Créer une évaluation</p>
            </button>
            
            <button class="bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-xl p-4 transition-all duration-300 transform hover:scale-105">
              <i class="ri-calendar-check-line text-3xl mb-2"></i>
              <p class="text-sm font-semibold">Marquer les absences</p>
            </button>
            
            <button class="bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-xl p-4 transition-all duration-300 transform hover:scale-105">
              <i class="ri-message-3-line text-3xl mb-2"></i>
              <p class="text-sm font-semibold">Envoyer un message</p>
            </button>
            
            <button class="bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-xl p-4 transition-all duration-300 transform hover:scale-105">
              <i class="ri-file-download-line text-3xl mb-2"></i>
              <p class="text-sm font-semibold">Exporter les notes</p>
            </button>
          </div>
        </div>

      </div>
    </div>
  <!-- </TeacherLayout> -->
</template>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

/* Scrollbar personnalisée */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>