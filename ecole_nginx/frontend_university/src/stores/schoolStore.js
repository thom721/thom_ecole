import { defineStore } from 'pinia';
import axios from 'axios';

const url = import.meta.env.VITE_APP_BASE_URL;

export const useSchoolStore = defineStore('school', {
  state: () => ({
    classes: [],
    faculte: [],
    niveau: [],
    annee: [],
    cours: [],
    professeur: [],
    school_info: null,
    isLoaded: false, 
    loading: false
  }),

  actions: {
    async fetchAllDependencies() { 
      if (this.isLoaded) return;

      this.loading = true;
      try { 
        const [resCl, resFa, resNi, resAn, resPr,resCr,profile] = await Promise.all([
          axios.get(`${url}/cl-load-asses_`),
          axios.get(`${url}/get-all-faculte`),
          axios.get(`${url}/niveau`),
          axios.get(`${url}/annee-academique`),
          axios.get(`${url}/prof-for-combo`),
          axios.get(`${url}/for-combo-cours`),
          axios.get(`${url}/get-profile`)
        ]);
        console.log(resNi.data.data);
        
        this.classes = resCl.data.data;
        this.faculte = resFa.data.data;
        this.niveau = resNi.data.data;
        this.annee = resAn.data.data;
        this.professeur = resPr.data.prof;
        this.cours = resCr.data.cours;
        this.school_info = profile.data.data
        
        this.isLoaded = true; // Marquer comme chargé
      } catch (error) {
        console.error("Erreur lors du chargement des dépendances:", error);
      } finally {
        this.loading = false;
      }
    }
  }
});

export const useSchoolStoreInfo = defineStore('school_info', {
  state: () => ({ 
    school_info: null,
    isLoaded: false, 
    classes_global: [],
    annee_global: [],
    role_global: [],
    niveau_global: [],
    faculte: [],
    loading: false
  }),

  actions: {
    async fetchAllDependencies() { 
      if (this.isLoaded) return; 
      this.loading = true;
      try { 
        const [profile,resCl , resAn,role,resNi,resFa] = await Promise.all([
        axios.get(`${url}/get-profile`),
        axios.get(`${url}/cl-load-asses_`),
        axios.get(`${url}/annee-academique`),
        axios.get(`${url}/role`),
        axios.get(`${url}/niveau`),
        axios.get(`${url}/get-all-faculte`)
        ]);

        this.faculte = resFa.data.data;
        this.classes_global = resCl.data.data;
        this.annee_global = resAn.data.data;
        this.school_info = profile.data.data
        this.role_global = role.data.data
        this.niveau_global = resNi.data.data;
        this.isLoaded = true; 
        console.log(resCl.data.data);
         
      } catch (error) {
        console.error("Erreur lors du chargement des dépendances:", error);
      } finally {
        this.loading = false;
      }
    }
  }
});