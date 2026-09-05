<script setup>
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import Swal from "sweetalert2";
import TextInput from "@/components/TextInput.vue";
import InsertNotesComponents from "@/components/InsertNotesComponents.vue";
import PrimaryButton from "@/components/PrimaryButton.vue";
import InputError from "@/components/InputError.vue";
import InputLabel from "@/components/InputLabel.vue";

const url = import.meta.env.VITE_APP_BASE_URL;

const students = ref([]);
const list_cours = ref([]);
const evaluation = ref('');
const data_students = ref({});
const isSubmitting = ref(false);
const isdata = ref(false);
const errors = ref({});
const isLoading = ref(false);

const handleSearchStart = () => {
  isLoading.value = true;
  students.value = [];
};
const handleSearchError = () => { isLoading.value = false; };

const saveFormNote = ref({
  examen: '', controle: '', cours: '', coefficients: '',
  note_de_passage: '', annee_academique: '', type_matiere: '',
  professeur_id: '', change_cours: ''
});

const evalOptions = {
  session:  [{ value: '1 ere Session', title: '1ère Session' }, { value: '2 eme Session', title: '2ème Session' }],
  controle: [{ value: 'Contr. I', title: 'Contrôle I' }, { value: 'Contr. II', title: 'Contrôle II' }, { value: 'Contr. III', title: 'Contrôle III' }],
  trimestre:[{ value: 'Trimestre I', title: 'Trimestre I' }, { value: 'Trimestre II', title: 'Trimestre II' }, { value: 'Trimestre III', title: 'Trimestre III' }]
};

const handleDataFetched = (data) => {
  if (!data) return;
  isLoading.value = false;
  saveFormNote.value.cours           = data.datas.cours?.cours_nom || '';
  saveFormNote.value.coefficients    = data.datas.cours?.coefficients || '';
  saveFormNote.value.annee_academique= data.datas.annee || '';
  saveFormNote.value.note_de_passage = data.datas.cours?.note_de_passage || '';
  saveFormNote.value.type_matiere    = data.datas.cours.type_matiere;
  saveFormNote.value.controle        = data.datas.examEcheance?.evaluation_par || '';
  list_cours.value = data.datas.list_cours || [];
  data_students.value = {
    session: data.datas.session,
    examEcheance: data.datas.examEcheance,
    month: data.datas.month,
    nom_classe: data.datas.cours?.nom_classe
  };
  students.value = data.datas.result.map(s => ({ ...s, note: '' }));
  isdata.value = true;
};

const showSwal = (text, icon = 'info') => Swal.fire({ position:"top-end", text, icon, showConfirmButton:false, timer:2000 });

const evaluationChange = async (e) => {
  evaluation.value = e.target.value;
  const payload = { ...saveFormNote.value, examen: evaluation.value, notes: students.value.map(s => ({ id:s.id, identifiant:s.identifiant })) };
  try {
    const res = await axios.post(`${url}/cours-etudiant-edit-note`, payload);
    if (res.status === 200 && res.data.success)
      res.data.success.forEach(item => { const s = students.value.find(s => s.id === item.etudiant_id); if (s) s.note = item.note; });
  } catch (err) { showSwal(err.response?.data?.errors?.cours || "Erreur de chargement", 'error'); }
};

const coursChange = (e) => {
  const cours = list_cours.value.find(c => c.id == e.target.value);
  if (cours) {
    Object.assign(saveFormNote.value, { cours:cours.cours_nom, coefficients:cours.coefficients, note_de_passage:cours.note_de_passage, type_matiere:cours.type_matiere, professeur_id:cours.professeur_id });
    students.value.forEach(s => s.note = '');
  }
};

const submitNotes = async () => {
  isSubmitting.value = true;
  errors.value = {};
  const payload = { ...saveFormNote.value, notes: students.value.map(s => ({ id:s.id, identifiant:s.identifiant, note:s.note })) };
  try {
    const res = await axios.post(`${url}/coursEtudiant`, payload);
    if (res.data.success) {
      showSwal(res.data.success, 'success');
      saveFormNote.value.examen = "";
      saveFormNote.value.change_cours = "";
      students.value.forEach(s => s.note = '');
    }
  } catch (err) {
    errors.value = err.response?.data?.errors || {};
    showSwal("Veuillez vérifier les notes saisies", 'error');
  } finally { isSubmitting.value = false; }
};
</script>

<template>
  <div class="page-root">

    <!-- ── Recherche initiale ── -->
    <InsertNotesComponents
      v-if="!isdata"
      route="cours-etudiant-add-note"
      @search-started="handleSearchStart"
      @search-error="handleSearchError"
      @result-fetched="handleDataFetched"
    />

    <!-- ── Spinner ── -->
    <div v-if="isLoading" class="loader-wrap">
      <div class="loader-ring">
        <span /><span /><span />
      </div>
      <p class="loader-text">Récupération de la liste des étudiants…</p>
    </div>

    <!-- ── Contenu principal ── -->
    <div v-if="!isLoading && students.length > 0" class="content-card">

      <!-- En-tête info + contrôles -->
      <div class="card-header">
        <div class="header-grid">

          <!-- Info cours -->
          <div class="info-block">
            <div class="info-row">
              <span class="info-label">Cours</span>
              <span class="info-value accent">{{ saveFormNote.cours }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Classe · Année</span>
              <span class="info-value">{{ data_students.nom_classe }}
                <span class="divider">·</span>
                {{ saveFormNote.annee_academique }}
              </span>
            </div>
            <div class="badges">
              <span class="badge">Coeff. {{ saveFormNote.coefficients }}</span>
              <span class="badge">Passage {{ saveFormNote.note_de_passage }}</span>
              <span class="badge muted">{{ saveFormNote.type_matiere }}</span>
            </div>
          </div>

          <!-- Changer matière -->
          <div class="field-block">
            <label class="field-label">Changer de matière</label>
            <div class="select-wrap">
              <select @change="coursChange" v-model="saveFormNote.change_cours" class="styled-select">
                <option value="" disabled>Sélectionnez une matière</option>
                <option v-for="c in list_cours" :key="c.id" :value="c.id">{{ c.cours_nom }}</option>
              </select>
              <i class="ri-arrow-down-s-line select-arrow" />
            </div>
          </div>

          <!-- Type d'évaluation -->
          <div class="field-block">
            <label class="field-label">Type d'évaluation</label>

            <div v-if="data_students.session" class="radio-group">
              <label class="radio-option">
                <input type="radio" v-model="saveFormNote.controle" value="intra" />
                <span class="radio-btn" />
                <span>Intra</span>
              </label>
              <label class="radio-option">
                <input type="radio" v-model="saveFormNote.controle" value="finale" />
                <span class="radio-btn" />
                <span>Final</span>
              </label>
            </div>

            <div v-else class="select-wrap">
              <select @change="evaluationChange" v-model="saveFormNote.examen" class="styled-select">
                <option value="" disabled>Choisir l'examen</option>
                <template v-if="data_students.examEcheance?.evaluation_par?.toLowerCase() === 'mois'">
                  <option v-for="(val, key) in data_students.month" :key="key" :value="key">{{ key }}</option>
                </template>
                <template v-else-if="data_students.examEcheance?.evaluation_par === 'Controle'">
                  <option v-for="opt in evalOptions.controle" :key="opt.value" :value="opt.value">{{ opt.title }}</option>
                </template>
                <template v-else-if="data_students.examEcheance?.evaluation_par === 'Trimestre'">
                  <option v-for="opt in evalOptions.trimestre" :key="opt.value" :value="opt.value">{{ opt.title }}</option>
                </template>
              </select>
              <i class="ri-arrow-down-s-line select-arrow" />
            </div>
            <p v-if="errors.examen?.[0]" class="field-error">{{ errors.examen[0] }}</p>
          </div>

        </div>
      </div>

      <!-- Tableau des notes -->
      <form @submit.prevent="submitNotes">
        <div class="table-wrap">
          <table class="notes-table">
            <thead>
              <tr>
                <th class="th-num">#</th>
                <th>Identifiant</th>
                <th>Nom &amp; Prénom</th>
                <th class="th-note">{{ saveFormNote.controle || evaluation || 'Note' }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(student, index) in students"
                :key="student.id"
                class="student-row"
                :style="{ animationDelay: `${index * 14}ms` }"
              >
                <td class="td-num">{{ index + 1 }}</td>
                <td>
                  <code class="id-chip">{{ student.identifiant }}</code>
                </td>
                <td class="td-name">{{ student.nom }} {{ student.prenom }}</td>
                <td class="td-note-cell">
                  <div class="note-input-wrap">
                    <input
                      type="number"
                      v-model="student.note"
                      step="0.1" min="0"
                      class="note-input"
                      :class="{ 'note-input--error': errors[`notes.${index}.note`] }"
                    />
                    <p v-if="errors[`notes.${index}.note`]" class="note-error">
                      {{ errors[`notes.${index}.note`][0] }}
                    </p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Footer -->
        <div class="card-footer">
          <span class="footer-count">{{ students.length }} étudiant{{ students.length > 1 ? 's' : '' }}</span>
          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            <svg v-if="isSubmitting" class="btn-spinner" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <i v-else class="ri-save-3-line" />
            {{ isSubmitting ? 'Enregistrement…' : 'Enregistrer les notes' }}
          </button>
        </div>
      </form>

    </div>
  </div>
</template>

<style scoped>
/* ═══════════════════════════════════════════
   TOKENS
═══════════════════════════════════════════ */
:root {
  --bg-page:    #0f1117;
  --bg-card:    #161b27;
  --bg-header:  #1a2033;
  --bg-row-alt: #191e2d;
  --bg-input:   #1e2436;
  --bg-chip:    #252c40;

  --border:     rgba(255,255,255,0.07);
  --border-md:  rgba(255,255,255,0.11);

  --text-primary:   #dde1ef;
  --text-secondary: #8b92ad;
  --text-muted:     #565d76;

  --accent:     #3b82f6;      /* bleu sobre */
  --accent-dim: #1d4ed840;
  --green:      #10b981;
  --red:        #ef4444;
}

/* ═══════════════════════════════════════════
   LAYOUT
═══════════════════════════════════════════ */
.page-root {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1rem 4rem;
  color: var(--text-primary);
  font-family: 'DM Sans', 'Nunito', system-ui, sans-serif;
}

/* ═══════════════════════════════════════════
   LOADER
═══════════════════════════════════════════ */
.loader-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 0;
  gap: 1rem;
}
.loader-ring {
  position: relative;
  width: 44px;
  height: 44px;
}
.loader-ring span {
  position: absolute;
  inset: 0;
  border: 2px solid transparent;
  border-radius: 50%;
  animation: spin 1.2s linear infinite;
}
.loader-ring span:nth-child(1) { border-top-color: var(--accent); animation-delay: 0s; }
.loader-ring span:nth-child(2) { border-right-color: var(--accent); opacity: .5; animation-delay: -.4s; }
.loader-ring span:nth-child(3) { border-bottom-color: var(--accent); opacity: .25; animation-delay: -.8s; }
@keyframes spin { to { transform: rotate(360deg); } }
.loader-text { font-size: .875rem; color: var(--text-secondary); letter-spacing: .02em; }

/* ═══════════════════════════════════════════
   CARD
═══════════════════════════════════════════ */
.content-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  animation: slideUp .35s ease both;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── En-tête ── */
.card-header {
  background: var(--bg-header);
  border-bottom: 1px solid var(--border);
  padding: 1.5rem 1.75rem;
}
.header-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.5rem;
  align-items: start;
}
@media (max-width: 768px) { .header-grid { grid-template-columns: 1fr; } }

/* Info block */
.info-block { display: flex; flex-direction: column; gap: .5rem; }
.info-row   { display: flex; align-items: baseline; gap: .75rem; flex-wrap: wrap; }
.info-label {
  font-size: .68rem;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: var(--text-muted);
  font-weight: 600;
  white-space: nowrap;
}
.info-value { font-size: .9rem; color: var(--text-primary); font-weight: 500; }
.info-value.accent { color: var(--accent); }
.divider { color: var(--text-muted); margin: 0 .25rem; }
.badges { display: flex; flex-wrap: wrap; gap: .4rem; margin-top: .25rem; }
.badge {
  font-size: .7rem;
  padding: .2rem .6rem;
  border-radius: 99px;
  border: 1px solid var(--border-md);
  background: var(--bg-chip);
  color: var(--text-secondary);
  font-weight: 600;
  letter-spacing: .03em;
}
.badge.muted { color: var(--text-muted); }

/* Field block */
.field-block { display: flex; flex-direction: column; gap: .5rem; }
.field-label {
  font-size: .72rem;
  text-transform: uppercase;
  letter-spacing: .09em;
  color: var(--text-muted);
  font-weight: 600;
}
.field-error { font-size: .72rem; color: var(--red); margin-top: .25rem; }

/* Select */
.select-wrap { position: relative; }
.styled-select {
  width: 100%;
  appearance: none;
  background: var(--bg-input);
  border: 1px solid var(--border-md);
  border-radius: 8px;
  padding: .55rem 2.25rem .55rem .85rem;
  font-size: .85rem;
  color: var(--text-primary);
  cursor: pointer;
  transition: border-color .15s, box-shadow .15s;
  outline: none;
}
.styled-select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
.select-arrow {
  position: absolute;
  right: .65rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
  font-size: 1rem;
}

/* Radio */
.radio-group { display: flex; gap: 1.25rem; padding: .4rem 0; }
.radio-option {
  display: flex;
  align-items: center;
  gap: .5rem;
  cursor: pointer;
  font-size: .875rem;
  color: var(--text-secondary);
  user-select: none;
  transition: color .15s;
}
.radio-option:hover { color: var(--text-primary); }
.radio-option input[type="radio"] { display: none; }
.radio-btn {
  width: 16px; height: 16px;
  border: 2px solid var(--border-md);
  border-radius: 50%;
  position: relative;
  transition: border-color .15s;
  flex-shrink: 0;
}
.radio-option input:checked ~ .radio-btn {
  border-color: var(--accent);
}
.radio-option input:checked ~ .radio-btn::after {
  content: '';
  position: absolute;
  inset: 3px;
  background: var(--accent);
  border-radius: 50%;
}
.radio-option input:checked ~ span:last-child { color: var(--accent); font-weight: 600; }

/* ── Tableau ── */
.table-wrap { overflow-x: auto; }
.notes-table {
  width: 100%;
  border-collapse: collapse;
  font-size: .875rem;
}
.notes-table thead tr {
  border-bottom: 1px solid var(--border-md);
}
.notes-table th {
  padding: .75rem 1rem;
  font-size: .68rem;
  text-transform: uppercase;
  letter-spacing: .1em;
  font-weight: 700;
  color: var(--text-muted);
  text-align: left;
  background: var(--bg-header);
}
.th-num   { width: 48px; text-align: center; }
.th-note  { width: 120px; text-align: center; }

.student-row {
  border-bottom: 1px solid var(--border);
  transition: background .12s;
  animation: rowIn .22s ease both;
}
.student-row:nth-child(even) { background: var(--bg-row-alt); }
.student-row:hover { background: rgba(59,130,246,.05); }
@keyframes rowIn {
  from { opacity: 0; transform: translateX(-4px); }
  to   { opacity: 1; transform: translateX(0); }
}

.notes-table td { padding: .65rem 1rem; vertical-align: middle; }
.td-num  { text-align: center; color: var(--text-muted); font-size: .78rem; font-variant-numeric: tabular-nums; }
.td-name { color: var(--text-primary); font-weight: 500; }

.id-chip {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: .72rem;
  background: var(--bg-chip);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: .15rem .55rem;
  border-radius: 5px;
  letter-spacing: .04em;
}

/* Note input */
.td-note-cell { text-align: center; }
.note-input-wrap { display: inline-flex; flex-direction: column; align-items: center; gap: .25rem; }
.note-input {
  width: 72px;
  text-align: center;
  background: var(--bg-input);
  border: 1px solid var(--border-md);
  border-radius: 7px;
  padding: .4rem .5rem;
  color: var(--text-primary);
  font-weight: 700;
  font-size: .95rem;
  font-variant-numeric: tabular-nums;
  outline: none;
  transition: border-color .15s, box-shadow .15s;
  -moz-appearance: textfield;
}
.note-input::-webkit-outer-spin-button,
.note-input::-webkit-inner-spin-button { -webkit-appearance: none; }
.note-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
.note-input--error { border-color: var(--red) !important; box-shadow: 0 0 0 3px rgba(239,68,68,.2) !important; }
.note-error { font-size: .67rem; color: var(--red); }

/* ── Footer ── */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.1rem 1.75rem;
  border-top: 1px solid var(--border);
  background: var(--bg-header);
}
.footer-count {
  font-size: .78rem;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: .03em;
}
.submit-btn {
  display: inline-flex;
  align-items: center;
  gap: .5rem;
  padding: .6rem 1.6rem;
  border-radius: 8px;
  background: var(--green);
  color: #fff;
  font-size: .875rem;
  font-weight: 600;
  letter-spacing: .02em;
  border: none;
  cursor: pointer;
  transition: opacity .15s, transform .1s, box-shadow .15s;
  box-shadow: 0 2px 12px rgba(16,185,129,.25);
}
.submit-btn:hover:not(:disabled) { opacity: .88; transform: translateY(-1px); box-shadow: 0 4px 18px rgba(16,185,129,.35); }
.submit-btn:active:not(:disabled){ transform: translateY(0); }
.submit-btn:disabled { opacity: .45; cursor: not-allowed; }
.btn-spinner { width: 14px; height: 14px; animation: spin 1s linear infinite; }
</style>
