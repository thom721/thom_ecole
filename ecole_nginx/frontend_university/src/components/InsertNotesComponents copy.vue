<script setup> 
import { ref, onMounted } from "vue";
import axios from 'axios';
import PrimaryButton from '@/components/PrimaryButton.vue';
import InputLabel from "@/components/InputLabel.vue";
import InputError from "@/components/InputError.vue";
import Swal from 'sweetalert2';
import { useSchoolStore } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';


const url = import.meta.env.VITE_APP_BASE_URL;

const props = defineProps({ 
    route: String, // ex: "/add-note-student"
});

const emit = defineEmits(['result-fetched']);
const schoolStore = useSchoolStore(); 
const { niveau, professeur, annee,classes,faculte,cours, loading } = storeToRefs(schoolStore);

onMounted(() => {
  schoolStore.fetchAllDependencies();
}); 
const getClassesByNiveau = (niveauId) => { 
  if (!niveauId || !classes.value) return [];  
  return classes.value.filter(c => c.niveau_id === niveauId);
};

// --- ÉTATS ---
const choseNiveau = ref([]);
const classe_actuelle = ref([]); 
const errors = ref({});
const isSubmitting = ref(false);

// Remplacement de useForm par un objet ref standard
const formNote = ref({
    cours: "",
    niveau: "",
    annee_academique: "",
    faculte: "",
    session: "",
    class: "",
});

// --- LOGIQUE DE RÉCUPÉRATION ---
const fetchNiveauData = async () => {
    if (!formNote.value.niveau) return;
    
    try {
        const res = await axios.get(`${url}/niveau-with-class/${formNote.value.niveau}`);
        choseNiveau.value = res.data.niveau;
        cours.value = res.data.cours;
        classe_actuelle.value = res.data.classe_actuelle;
        
        // Réinitialisation partielle
        formNote.value.cours = "";
        formNote.value.faculte = "";
        formNote.value.session = "";
        formNote.value.class = "";
        errors.value = {};
    } catch (error) {
        console.error("Erreur lors de la récupération du niveau", error);
    }
};
 
const submitNote = async () => {
    isSubmitting.value = true;
    errors.value = {};
    emit('search-started');
    try {
        const response = await axios.post(`${url}/${props.route}`, formNote.value);
        
        if (response.status === 200) {
            Swal.fire({
                icon: 'success',
                title: 'Succès',
                text: 'Données enregistrées. Passage à l\'étape suivante...',
                timer: 1500,
                showConfirmButton: false
            });
            console.log(response.data);
            emit('result-fetched', response.data);
        }
    } catch (error) {
     console.log(error.response);
            emit('search-error');
          if(error.response && error.response.data.detail.errors){
                Swal.fire('Erreur', error.response.data.detail.errors.warning, 'error');
          }else if(error.response && error.response.data.detail){
            Swal.fire('Erreur', error.response.data.detail, 'error');
          } else{
        if (error.response && error.response.status === 422) {
            errors.value = error.response.data.errors;
        } else {
            Swal.fire('Erreur', 'Une erreur inattendue est survenue', 'error');
        }
        }
    } finally {
        isSubmitting.value = false;
    }
};
</script>

<template>
    <form class="grid md:grid-cols-4 content-center gap-4 mt-2" @submit.prevent="submitNote">

        <div class="w-full">
            <InputLabel for="niveau" value="Cycle" />
            <select class="select" v-model="formNote.niveau" id="niveau">
                <option value="" disabled>Choisir un Cycle</option>
                <option v-for="n in niveau" :key="n.id" :value="n.id">
                    {{ n.name }}
                </option>
            </select>
            <InputError class="mt-2" :message="errors.niveau ? errors.niveau[0] : ''" />
        </div>

        <div class="w-full">
            <InputLabel for="cours" value="Cours / Matière" />
            <select class="select" v-model="formNote.cours" id="cours">
                <option value="" disabled>Choisir Matière</option>
                <option v-for="c in cours" :key="c.id" :value="c.id">
                    {{ c.cours_nom }}
                </option>
            </select>
            <InputError class="mt-2" :message="errors.cours ? errors.cours[0] : ''" />
        </div>

        <div v-if="choseNiveau.name === 'Universitaire' || choseNiveau.name === 'Technique'" class="w-full">
            <InputLabel for="faculte" value="Facultés / Option" />
            <select class="select" v-model="formNote.faculte" id="faculte">
                <option value="" disabled>Faculté / Option</option>
                <option v-for="f in props.faculte" :key="f.id" :value="f.id">
                    {{ f.nom }}
                </option>
            </select>
            <InputError class="mt-2" :message="errors.faculte ? errors.faculte[0] : ''" />
        </div>

        <div class="w-full">
            <InputLabel for="Classe" value="Classe" />
            <select class="select" v-model="formNote.class" id="class">
                <option value="" disabled>Choisir Classe</option> 
               <option v-for="cls in getClassesByNiveau(formNote.niveau)" 
                         :key="cls.id" 
                         :value="cls.id">
               {{ cls.nom_classe }}
               </option>
            </select>
            <InputError class="mt-2" :message="errors.class ? errors.class[0] : ''" />
        </div>

        <div class="w-full">
            <InputLabel for="annee_academique" value="Année Académique" />
            <select class="select" v-model="formNote.annee_academique" id="annee_academique">
                <option value="" disabled>Année Académique</option>
                <option v-for="a in annee" :key="a.id" :value="a.id">
                    {{ a.annee_academique }}
                </option>
            </select>
            <InputError class="mt-2" :message="errors.annee_academique ? errors.annee_academique[0] : ''" />
        </div>

        <div v-if="choseNiveau.name === 'Universitaire' || choseNiveau.name === 'Professionel'" class="w-full">
            <InputLabel for="session" value="Session" />
            <select class="select" v-model="formNote.session" id="session">
                <option value="" disabled>Choisir Session</option>
                <option value="1ere">1 ère</option>
                <option value="2eme">2 ème</option>
            </select>
            <InputError class="mt-2" :message="errors.session ? errors.session[0] : ''" />
        </div>

        <div class="flex items-end pb-1">
            <PrimaryButton type="submit" :class="{ 'opacity-50': isSubmitting }" :disabled="isSubmitting">
                <span v-if="isSubmitting">Chargement...</span>
                <span v-else>Suivant</span>
            </PrimaryButton>
        </div>

    </form>
</template>
 <!-- #0f1117 → carte #161b27 → en-tête #1a2033,  #0d1117 / #161b22 / #21262d avec accents bleu #58a6ff -->