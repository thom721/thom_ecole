<script setup>
import { onMounted, ref, watch, computed } from "vue";
import { RouterLink, useRouter } from "vue-router";
import axios from "axios";
import Swal from 'sweetalert2';
import DialogModal from "@/components/DialogModal.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import DataTable from "@/components/DataTable.vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const canWrite = computed(() =>
  authStore.roleNames.some(r => ['admin', 'Responsable des admissions', 'Responsable pédagogique'].includes(r))
);
 
defineOptions({ layout: AdminLayout });
const url = import.meta.env.VITE_APP_BASE_URL;
const router = useRouter();

// --- États ---
const allStudent = ref({ data: [], meta: { links: [] } });
const search = ref("");
const pages = ref(1);
const dataLoading = ref(false);
const activatingId = ref(null)

// Modales
const searchForCertificate = ref(false);

// --- Recherche & Pagination ---
const searchEtudiants = async (page=1) => {
  dataLoading.value = true;
  try {
    const response = await axios.get(`${url}/etudiant`, {
      params: {
        search: search.value,
        page: page,
      },
    });
 
      allStudent.value = response.data;
  
  } catch (error) {
    console.error('Erreur lors de la recherche :', error);
  } finally {
    dataLoading.value = false;
  }
};

const showSwalInfo = (text, color) => {
  Swal.fire({
    position: "top-end",
    text: text,
    showConfirmButton: false,
    timer: 3000,
    color: color,
  });
};

// Surveillance des changements pour rafraîchir la liste
watch(search, () => {
  pages.value = 1;
  searchEtudiants();
});

watch(pages, () => {
  searchEtudiants();
});

onMounted(() => {
  searchEtudiants();
});

 

// --- Actions ---
const toggleStatus = async (id) => {
  activatingId.value=id
  try {
    const response =await axios.patch(`${url}/active-etudiant`, { id: id });
    console.log(response);
    // if (response.data?.status) {
      showSwalInfo(response.data.success, 'green')      
    // }
    activatingId.value=null
    searchEtudiants(); 
  } catch (error) {
    activatingId.value=null
     if (error.response?.data?.detail) {
      showSwalInfo(error.response?.data?.detail,"red")
    }
    // console.log(error.response); 
  }
};

const deleteStudent = (id) => {
  if (confirm("Voulez-vous vraiment supprimer cet étudiant ?")) {
    // Logique de suppression ici
  }
};

const columns = [ 
  { key: 'identifiant',       label: 'Identifiant',    badge: true },
  { key: 'nom',       label: 'Nom', },
  { key: 'prenom',       label: 'Prénom', nowrap: true },
  { key: 'sexe',       label: 'Sexe', nowrap: true ,    badge: true},
  { key: '_naissance',  label: "Date Naissance" },
  { key: 'email',        label: 'Courriel' , nowrap: true }
]


const actions = computed(() => {
  const base = [
    {
      key: 'edit',
      type: 'slot',
      icon: 'ri-edit-box-line text-sky-500 hover:text-sky-700 cursor-pointer',
      onClick: async (row) => { console.log(row); },
    },
    {
      key: 'view',
      type: 'slot',
      icon: 'ri-eye-line text-emerald-500 hover:text-emerald-700',
      onClick: async (row) => { console.log(row); },
    },
  ];
  if (canWrite.value) {
    base.push({
      key: 'delete',
      type: 'button',
      icon: 'ri-delete-bin-6-line text-rose-400 hover:bg-rose-600/10 text-md',
      onClick: async (row) => { console.log(row); },
    });
  }
  return base;
});
</script>

<template>
  <div class="max-w-7xl mx-auto animate-[fadeUp_0.4s_ease_both]">
    <div class="flex items-center gap-3 mb-5">
  <div class="w-9 h-9 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center shrink-0">
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.6" class="w-5 h-5 text-rose-400">
      <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5"/>
    </svg>
  </div>
  <div>
    <h1 class="text-[15px] font-bold text-[#e8eaf0] leading-tight">Étudiants</h1>
    <p class="text-[12px] text-[#7c83a0]">Inscriptions, dossiers et scolarité</p>
  </div>
</div>


    <div class="flex flex-wrap items-center justify-between gap-4 pb-4">
      <!-- <div class="flex flex-wrap gap-2">
        <router-link to="/admin/etudiants/ajouter"
          class="inline-flex items-center px-4 py-2 bg-sky-600 border border-transparent rounded-lg  text-xs text-white uppercase tracking-widest hover:bg-sky-700 transition duration-200 shadow-sm">
          <i class="fas fa-plus mr-2"></i> Ajouter étudiant
        </router-link>

        <button type="button"
          class="px-4 py-2 border border-amber-500 text-amber-500 rounded-lg text-xs  uppercase hover:bg-amber-500 hover:text-white transition duration-200">
          <i class="fas fa-file-excel mr-2"></i> Import Excel
        </button>

        <button @click="searchForCertificate = true"
          class="px-4 py-2 border border-purple-500 text-purple-500 rounded-lg text-xs  uppercase hover:bg-purple-500 hover:text-white transition duration-200">
          <i class="fas fa-certificate mr-2"></i> Certificat / Diplôme
        </button>
      </div> -->

      <div class="flex flex-wrap gap-2">

        <!-- Ajouter étudiant — admin / Resp. admissions / Resp. pédagogique -->
        <router-link v-if="canWrite" to="/admin/etudiants/ajouter"
          class="btn-custum-sky">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/>
          </svg>
          Ajouter étudiant
        </router-link>

        <button v-if="canWrite" type="button"
          class="btn-emerald">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
          </svg>
          Import Excel
        </button>

        <button @click="searchForCertificate = true"
          class="btn-violet">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5"/>
          </svg>
          Certificat / Diplôme
        </button>

      </div>

      <div class="w-full md:w-5/12">
          <div class="relative flex-1">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
              class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#3d4d62] pointer-events-none">
              <path fill-rule="evenodd" d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" clip-rule="evenodd" />
            </svg>
          <input 
            type="text" 
            v-model="search" 
            placeholder="Rechercher un étudiant..."
            class="field-search"
          />
        </div>
      </div>
    </div>

    <DataTable
    :columns="columns"
    :rows="allStudent.data"
    row-key="id"
    :loading="dataLoading"
    :skeleton-rows="10"
    :meta="allStudent.meta"
    :actions="actions"  
    @change-page="searchEtudiants"
    @update:selections="selections = $event"
  > 
      <template #cell-email="{value }">
      <span class="text-[13px] text-[#7c83a0]">{{ value ?? 'Non definie' }}</span>
       </template>

    <template #cell-identifiant="{row, value }">      
          <button
          v-if="activatingId !== row.id"
          @click="toggleStatus(row.id)"
          :disabled="activatingId !== null"
          class="font-mono hover:underline cursor-pointer text-sm"
          :class="{
            'text-green-400 bg-green-500/10 border border-green-500/20 px-2.5 rounded-full': row?.user?.status == '1',
            'text-orange-400 bg-orange-500/10 border border-orange-500/20 px-2.5 rounded-full': row?.user?.status == '0',
            'text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2.5 rounded-full': row?.user?.status != '1' && row?.user?.status != '0'
          }">
          {{ value }}
        </button>

        <span v-else class="inline-flex items-center gap-1.5 text-sky-500 text-sm">
          <svg class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10"
              stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
          </svg>
          Waiting…
        </span>
    </template>

      <template #action-view="{row}">
        <router-link :to="'/etudiants/voir/' + row.id" title="Détails">
          <i class="ri-eye-line text-emerald-500 hover:bg-emerald-500/10 rounded-full text-xs"></i>
        </router-link>
      </template>

      <template #action-edit="{row}">
        <router-link :to="'/etudiants/modifier/' + row.id" title="Modifier">
          <i class="ri-edit-box-line text-sky-500 hover:bg-sky-500/10 hover:border-sky-500/10 text-xs"></i>
        </router-link>
      </template>
 
        <template #empty>
        Aucun étudiant trouvé pour cette recherche.
    </template>
    </DataTable> 

    <!-- <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left text-slate-600">
          <thead class="text-xs text-white uppercase border-b border-slate-200 bg-gray-700">
            <tr>
              <th class="px-6 py-4 ">Identifiant</th>
              <th class="px-6 py-4 ">Nom </th>
              <th class="px-6 py-4 ">Prénom </th>
              <th class="px-6 py-4 ">Sexe</th>
              <th class="px-6 py-4 ">Date Naissance</th>
              <th class="px-6 py-4  text-center">Actions</th>
            </tr>
          </thead>

 
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(student, index) in allStudent.data" :key="student.id" 
                class="hover:bg-slate-50 transition-colors" :class="{ 'bg-gray-200': index % 2 == 1 }">


                <td class="px-6 py-4 whitespace-nowrap cursor-pointer">

                  <button
                    v-if="activatingId !== student.id"
                    @click="toggleStatus(student.id)"
                    :disabled="activatingId !== null"
                    class="font-mono hover:underline"
                    :class="student.status == '1' ? 'text-green-600' : 'text-rose-500'">
                    {{ student.identifiant }}
                  </button>

                  <span v-else class="inline-flex items-center gap-1.5 text-sky-500 text-sm">
                    <svg class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10"
                        stroke="currentColor" stroke-width="4"/>
                      <path class="opacity-75" fill="currentColor"
                        d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
                    </svg>
                    Waiting…
                  </span>

                </td>
              
              
              <td class="px-6 py-4">
                <div class=" text-slate-800">{{ student.nom }}</div>
              </td>
              <td class="px-6 py-4">
                <div class=" text-slate-800">{{ student.prenom }}</div>
              </td>
              
              <td class="px-6 py-4">
                <span class="px-2 py-1 rounded-md text-xs font-medium bg-slate-100">
                  {{ student.sexe }}
                </span>
              </td>
              
              <td class="px-6 py-4 text-slate-500">
                {{ student._naissance }}
              </td>

              <td class="px-6 py-4 text-center">
                <div class="flex justify-center gap-3">
                  <router-link :to="'/etudiants/modifier/' + student.id" title="Modifier">
                    <i class="ri-edit-box-line text-sky-500 hover:text-sky-700"></i>
                  </router-link>
                  
                  <button @click="deleteStudent(student.id)" title="Supprimer">
                    <i class="ri-delete-bin-6-line text-rose-400 hover:text-rose-600"></i>
                  </button>
                  <router-link :to="'/etudiants/voir/' + student.id" title="Détails">
                    <i class="ri-eye-line text-emerald-500 hover:text-emerald-700"></i>
                  </router-link>
                </div>
              </td>
            </tr>
 
          </tbody>
        </table>
      </div>
 
    </div> -->

    <DialogModal :show="searchForCertificate" @close="searchForCertificate = false">
      <template #title>Émission de documents</template>
      <template #content>
        <div class="p-4">
          <label class="block text-sm font-medium text-slate-700 mb-2">Rechercher par identifiant</label>
          <input type="text" class="w-full border-slate-300 rounded-lg shadow-sm focus:ring-sky-500 focus:border-sky-500" placeholder="Ex: ET-2024-001">
          <p class="mt-4 text-xs text-slate-400 text-center italic">Le document sera généré au format PDF après validation.</p>
        </div>
      </template>
      <template #footer>
        <button @click="searchForCertificate = false" class="px-4 py-2 text-sm  text-slate-500">Fermer</button>
      </template>
    </DialogModal>

  </div>
</template>