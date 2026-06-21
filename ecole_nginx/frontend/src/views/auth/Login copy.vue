<script setup>
import TextInput from "@/components/TextInput.vue";
import InputLabel from "@/components/InputLabel.vue";
import InputError from "@/components/InputError.vue";
import PrimaryButton from "@/components/PrimaryButton.vue";
import Checkbox from "@/components/Checkbox.vue"; // Nouveau
import Swal from 'sweetalert2'; // Sera résolu après le npm install
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth"; 

// Importe tes composants UI s'ils existent, sinon remplace par des balises standards
// import TextInput from "@/Components/TextInput.vue"; 

const router = useRouter();
const authStore = useAuthStore();

const form = reactive({
    email: '',
    password: '',
    remember: false,
    processing: false,
    errors: {}
});



const submit1 = async () => {
    form.processing = true;
    try {
        const response = await authStore.login({
            email: form.email,
            password: form.password
        });

        const user = response.data.user;

      if (user.userable_type === 'App\\Models\\Professeur') {
          router.push({ name: 'teacher.dashboard' });
      } else {
          router.push({ name: 'Dashboard' });
      }
        router.push('/admin/dashboard');
    } catch (err) {
      console.log(err);
      
        // Si l'API renvoie des erreurs de validation (422) ou une 401
        if (err.response && err.response.status === 401) {
            Swal.fire('Échec', 'Email ou mot de passe incorrect', 'error');
        } else {
            Swal.fire('Erreur', 'Impossible de joindre le serveur', 'error');
        }
    } finally {
        form.processing = false;
    }
};

const submit = async () => {
    form.processing = true;
    try {
        const response = await authStore.login({
            email: form.email,
            password: form.password
        });        
        const user = response.user;
 
        if (user.userable_type === 'App\\Models\\Professeur') {
            router.push({ name: 'teacher.dashboard' });
        } else if (user.userable_type === 'App\\Models\\Etudiant') {
            router.push({ name: 'etudiant.dashboard' });
        } else { 
            router.push({ name: 'Dashboard' }); 
        } 

    } catch (err) {
        console.error("Erreur de login:", err.response?.data?.detail);
        if (err.response && err.response.status === 422) {
            Swal.fire('Échec', err.response?.data?.detail ?? 'Email ou mot de passe incorrect', 'error');
        } else {
            Swal.fire('Erreur', 'Impossible de joindre le serveur', 'error');
        }
    } finally {
        form.processing = false;
    }
};
</script>

<template>
  <div class="min-h-screen bg-[#f1f1f1] flex items-center justify-center px-8">
    
    <div class="max-w-md w-full animate__animated animate__fadeInUp">
      
      <div class="flex items-center mb-6">
        <button @click="router.push('/')" class="p-2 text-slate-500 hover:text-blue-600 transition-colors cursor-pointer">
          <i class="fa-lg">Retour à l'accueil</i>
        </button> 
      </div>

      <div class="bg-white p-8 rounded-2xl shadow-xl border border-yellow-100">
        <div class="mb-8 text-center md:text-left">
          <h4 class="m-0 font-bold text-slate-800 text-2xl tracking-tight">Bienvenue !</h4>
          <div class="w-12 h-1 bg-blue-500 mt-2 mb-8"></div>
          <p class="text-slate-500 pb-4">Connectez-vous à votre compte Ecole Pro.</p>
        </div>

        <form @submit.prevent="submit" class="space-y-8">
    
            <div class="mt-4">
                  <InputLabel for="email" value="Email" />
                  <TextInput id="email" v-model="form.email" type="text" class="mt-1 input-field" autofocus
                    autocomplete="username" />
                  <InputError v-if="form.errors && form.errors.email" class="mt-2" :message="form.errors?.email[0]" />
                </div>

                <div class="pt-4">
                  <InputLabel for="password" value="Mot de passe" />
                  <TextInput id="password" v-model="form.password" type="password" class="mt-1 input-field" required
                    autocomplete="current-password" />
                  <InputError class="mt-2" :message="form.errors.password" />
                </div>

          <div class="flex items-center justify-end py-2">
            <label class="flex items-center cursor-pointer">
              <input type="checkbox" v-model="form.remember" class="rounded text-blue-600 focus:ring-blue-500 border-slate-300">
              <span class="ps-2 text-sm text-slate-600">Se souvenir de moi</span>
            </label>
            <!-- <router-link to="/forgot-password" class="text-sm text-blue-600 hover:underline">Oublié ?</router-link> -->
          </div>

          <div class="mt-4">
          <PrimaryButton class="mt-4 w-full text-center"
            type="submit" 
            :disabled="form.processing"
             
          >
            <span v-if="!form.processing">Se connecter</span>
            <span v-else>Chargement...</span>
          </PrimaryButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>