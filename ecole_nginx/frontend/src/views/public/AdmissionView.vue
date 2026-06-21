<template>
  <div class="min-h-screen bg-[#0b0f14] text-[#dde4ed] font-sans">

    <!-- ═══════════════════════ HERO ══════════════════════ -->
    <section class="relative h-[50vh] min-h-[240px] overflow-hidden">
      <img
        src="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1800&q=80"
        alt="" class="absolute inset-0 w-full h-full object-cover object-[center_30%]"
      />
      <div class="absolute inset-0"
        style="background:linear-gradient(140deg,rgba(10,28,25,.96),rgba(11,15,20,.85),rgba(20,14,6,.7))">
      </div>
      <div class="relative z-10 h-full flex flex-col items-center justify-center text-center px-6 gap-3">
        <span class="text-[#c9a84c] text-[11px] font-bold tracking-[.25em] uppercase">
          Inscriptions {{ currentYear?.annee_academique }}
        </span>
        <h1 class="text-[clamp(1.9rem,5vw,3.4rem)] font-extrabold text-white leading-tight tracking-tight m-0">
          Demande d'<em class="not-italic text-[#c9a84c]">Admission</em>
        </h1>
        <p class="text-sm text-white/60 leading-relaxed max-w-sm m-0">
          Complétez votre dossier en ligne en quelques étapes.<br>Traitement garanti sous 24 h.
        </p>
      </div>
    </section>

    <!-- ═══════════════════════ STEPPER ═══════════════════ -->
    <nav class="bg-[#111820] border-b border-[#252d38] sticky top-16 z-40 px-6 pt-4">
      <div class="max-w-[820px] mx-auto">
        <ol class="list-none m-0 p-0 flex items-center overflow-x-auto pb-3">
          <template v-for="(s, i) in STEPS" :key="i">
            <li class="flex-shrink-0">
              <button type="button" class="flex flex-col items-center gap-1 bg-transparent border-0 cursor-pointer p-0"
                @click="step = i">
                <span class="w-[30px] h-[30px] rounded-full flex items-center justify-center text-[.78rem] font-bold border-2 transition-all duration-200"
                  :class="step > i
                    ? 'bg-[#1f8f82] border-[#1f8f82] text-white'
                    : step === i
                      ? 'bg-[#c9a84c] border-[#c9a84c] text-[#0b0f14]'
                      : 'bg-[#181f28] border-[#2e3845] text-[#6b7a8d]'"
                >
                  <svg v-if="step > i" class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 16 16">
                    <polyline points="3 8 7 12 13 5"/>
                  </svg>
                  <span v-else>{{ i + 1 }}</span>
                </span>
                <span class="hidden sm:block text-[.6rem] font-bold uppercase tracking-[.1em] transition-colors"
                  :class="step > i ? 'text-[#3aad7a]' : step === i ? 'text-[#c9a84c]' : 'text-[#3d4a58]'">
                  {{ s }}
                </span>
              </button>
            </li>
            <li v-if="i < STEPS.length - 1" class="flex-1 min-w-[20px] h-px mx-1.5 mb-5 transition-colors"
              :class="step > i ? 'bg-[#1f8f82]' : 'bg-[#2e3845]'" aria-hidden="true">
            </li>
          </template>
        </ol>
        <!-- progress bar -->
        <div class="h-[2px] bg-[#252d38] rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-[width_.45s_cubic-bezier(.4,0,.2,1)]"
            style="background:linear-gradient(90deg,#1f8f82,#c9a84c)"
            :style="{ width: (step / (STEPS.length - 1) * 100) + '%' }">
          </div>
        </div>
      </div>
    </nav>

    <!-- ═══════════════════════ PANELS ════════════════════ -->
    <main class="max-w-[880px] mx-auto px-5 pt-7 pb-24">
      <form @submit.prevent="submitForm" novalidate>
        <Transition name="panel" mode="out-in">

          <!-- ─────── SUCCÈS ─────── -->
          <div v-if="done" key="done"
            class="rounded-2xl text-center px-8 py-16 border border-[#1f8f82]/30"
            style="background:linear-gradient(145deg,#0f2a26,#0b1f1c)">
            <div class="text-[3.5rem] mb-4">🎉</div>
            <h2 class="text-3xl font-extrabold text-white m-0 mb-3">Dossier transmis !</h2>
            <p class="text-sm text-white/60 max-w-sm mx-auto leading-relaxed mb-4">
              Notre équipe examinera votre candidature sous 24 h et vous contactera par email.
            </p>
            <div class="inline-block bg-white/[.08] border border-white/[.12] text-white/75 text-sm px-5 py-2 rounded-full mb-6">
              Référence&nbsp;: <strong class="text-[#fde68a]">ADM-{{ admRef }}</strong>
            </div><br>

             <button  @click="submitPdf(`/print-recu-inscrit/${student_id}`, { student_id: student_id }, 'print-recu-inscrit')" type="submit" class="btn-gold":disabled="loadingMap['print-recu-inscrit'] === true">              
              <svg v-if="loadingMap['print-recu-inscrit'] === true" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>Génération...
                </svg>
              <span v-else>Reçu</span>
            </button>
            <!-- <button type="button" class="btn-gold" @click="reset">Nouvelle candidature</button> -->
          </div>

          <!-- ─────── ÉTAPE 0 — INFORMATIONS ─────── -->
          <div v-else-if="step === 0" key="s0" class="card">
            <CardHeader icon="👤" title="Informations personnelles" />

            <!-- Identité -->
            <Fieldset legend="Identité de l'élève">
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
                <FormField label="Nom *"               :error="f.errors.nom">
                  <input class="inp" :class="{ 'inp-err': f.errors.nom }"
                    type="text" placeholder="DUPONT" v-model="f.nom" />
                </FormField>
                <FormField label="Prénom *"            :error="f.errors.prenom">
                  <input class="inp" :class="{ 'inp-err': f.errors.prenom }"
                    type="text" placeholder="Marie" v-model="f.prenom" />
                </FormField>
                <FormField label="Sexe *"              :error="f.errors.sexe">
                  <select class="inp" :class="{ 'inp-err': f.errors.sexe }" v-model="f.sexe">
                    <option value="">Choisir…</option>
                    <option value="F">Féminin</option>
                    <option value="M">Masculin</option>
                    <option value="A">Autre</option>
                  </select>
                </FormField>
                <FormField label="Date de naissance *" :error="f.errors.date_de_naissance">
                  <input class="inp" :class="{ 'inp-err': f.errors.date_de_naissance }"
                    type="date" v-model="f.date_de_naissance" />
                </FormField>
                <FormField label="Lieu de naissance *" :error="f.errors.lieu_de_naissance">
                  <input class="inp" :class="{ 'inp-err': f.errors.lieu_de_naissance }"
                    type="text" v-model="f.lieu_de_naissance" />
                </FormField>
                <FormField label="Religion">
                  <input class="inp" type="text" v-model="f.religion" />
                </FormField>
                <FormField label="Email *"             :error="f.errors.email">
                  <input class="inp" :class="{ 'inp-err': f.errors.email }"
                    type="email" placeholder="marie@exemple.com" v-model="f.email" />
                </FormField>
                <FormField label="Téléphone">
                  <input class="inp" type="tel" placeholder="+509 00 00 0000" v-model="f.telephone" />
                </FormField>
                <FormField label="Adresse">
                  <input class="inp" type="text" placeholder="Adresse complète" v-model="f.adresse" />
                </FormField>
              </div>
            </Fieldset>

            <!-- Formation -->
            <Fieldset legend="Formation souhaitée" class="mt-4">
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
                <FormField label="Niveau *"            :error="f.errors.niveau_id">
                  <select class="inp" :class="{ 'inp-err': f.errors.niveau_id }" v-model="f.niveau_id">
                    <option value="">Choisir…</option>
                    <option v-for="n in niveau_global" :key="n.id" :value="n.id">{{ n.name }}</option>
                  </select>
                </FormField>
         
                <FormField label="Classe *"            :error="f.errors.classe_actuelle_id">
                  <select class="inp" :class="{ 'inp-err': f.errors.classe_actuelle_id }"
                    v-model="f.classe_actuelle_id" :disabled="!f.niveau_id">
                    <option value="">{{ f.niveau_id ? 'Choisir…' : 'Sélectionner un niveau' }}</option>
                    <option v-for="c in classesFiltrees" :key="c.id" :value="c.id">{{ c.nom_classe }}</option>
                  </select>
                </FormField>
                <FormField v-if="is_university" label="Faculté *" :error="f.errors.faculte_id">
                  <select class="inp" :class="{ 'inp-err': f.errors.faculte_id }" v-model="f.faculte_id">
                    <option value="">Choisir…</option>
                    <option v-for="fac in faculte" :key="fac.id" :value="fac.id">{{ fac.nom }}</option>
                  </select>
                </FormField>
                <FormField label="Année académique *"  :error="f.errors.annee_academique_id">
                  <select class="inp" :class="{ 'inp-err': f.errors.annee_academique_id }"
                    v-model="f.annee_academique_id">
                    <option value="" disabled>Choisir…</option>
                    <option v-for="a in annee_global" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
                  </select>
                </FormField>
                <FormField label="Dernier établissement">
                  <input class="inp" type="text" v-model="f.dernier_etablissement" />
                </FormField>
                <FormField label="Aide financière">
                  <select class="inp" v-model="f.aide_financiere">
                    <option value="Aucune">Aucune</option>
                    <option value="Demi Bourse">Demi-bourse</option>
                    <option value="Bourse">Bourse complète</option>
                  </select>
                </FormField>
              </div>
              <div class="mt-3">
                <FormField label="Motif de candidature">
                  <textarea class="inp resize-y min-h-[70px]" rows="3"
                    placeholder="Expliquez brièvement votre motivation…" v-model="f.motif">
                  </textarea>
                </FormField>
              </div>
            </Fieldset>

            <!-- Toggles -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
              <ToggleCard icon="🎓" title="Demande de bourse"
                sub="Joindre une attestation dans les documents"
                :on="f.bourse" @toggle="f.bourse = !f.bourse" />
              <ToggleCard icon="♿" title="Besoin particulier"
                sub="Aménagement pédagogique requis"
                :on="f.handicap" @toggle="f.handicap = !f.handicap" />
            </div>

            <div class="flex justify-between items-center mt-7">
              <span></span>
              <button type="button" class="btn-gold" @click="goStep0">
                Tuteur / Responsable →
              </button>
            </div>
          </div>

          <!-- ─────── ÉTAPE 1 — TUTEUR ─────── -->
          <div v-else-if="step === 1" key="s1" class="card">
            <CardHeader icon="👨‍👩‍👧" title="Responsable légal" />

            <Fieldset legend="Informations du responsable">
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
                <FormField label="Lien de parenté *">
                  <select class="inp" v-model="f.relation_responsable">
                    <option value="">Choisir…</option>
                    <option>Père</option><option>Mère</option>
                    <option>Tuteur légal</option><option>Grand-parent</option><option>Autre</option>
                  </select>
                </FormField>
                <FormField label="Civilité">
                  <select class="inp" v-model="f.sexe_responsable">
                    <option value="F">Madame</option>
                    <option value="M">Monsieur</option>
                  </select>
                </FormField>
                <FormField label="Nom *">
                  <input class="inp" type="text" placeholder="MARTIN" v-model="f.nom_responsable" />
                </FormField>
                <FormField label="Prénom *">
                  <input class="inp" type="text" placeholder="Jean" v-model="f.prenom_responsable" />
                </FormField>
                <FormField label="Téléphone *">
                  <input class="inp" type="tel" v-model="f.telephone_responsable" />
                </FormField>
                <FormField label="Email *">
                  <input class="inp" type="email" v-model="f.email_responsable" />
                </FormField>
                <FormField label="Profession">
                  <input class="inp" type="text" placeholder="Médecin, Ingénieur…" v-model="f.metier_responsable" />
                </FormField>
                <FormField label="Adresse">
                  <input class="inp" type="text" v-model="f.adresse_responsable" />
                </FormField>
              </div>
            </Fieldset>

            <Fieldset legend="Contact d'urgence" class="mt-4">
              <p class="text-xs text-[#6b7a8d] mb-3 leading-relaxed">
                Personne à contacter en cas d'urgence, différente du responsable légal.
              </p>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
                <FormField label="Nom complet">
                  <input class="inp" type="text" placeholder="Ex: Marie Dupont" v-model="f.nom_urgence" />
                </FormField>
                <FormField label="Téléphone">
                  <input class="inp" type="tel" v-model="f.telephone_urgence" />
                </FormField>
                <FormField label="Relation">
                  <input class="inp" type="text" placeholder="Tante, Oncle…" v-model="f.relation_urgence" />
                </FormField>
              </div>
            </Fieldset>

            <div class="flex justify-between items-center mt-7">
              <button type="button" class="btn-ghost" @click="step = 0">← Retour</button>
              <button type="button" class="btn-gold"  @click="step = 2">Documents →</button>
            </div>
          </div>

          <!-- ─────── ÉTAPE 2 — DOCUMENTS ─────── -->
          <div v-else-if="step === 2" key="s2" class="card">
            <CardHeader icon="📁" title="Pièces justificatives" />

            <div class="flex gap-3 items-start bg-[#181f28] border border-[#252d38] rounded-xl p-4 mb-5 text-sm text-[#6b7a8d]">
              <span class="text-[#4f9eff] font-bold flex-shrink-0 mt-0.5">ℹ</span>
              <div>
                <strong class="text-[#dde4ed]">Formats acceptés : PDF, JPG, PNG — 5 Mo max.</strong>
                <span> Les originaux pourront être demandés lors de l'entretien.</span>
              </div>
            </div>

            <TransitionGroup name="doc" tag="div" class="flex flex-col gap-3.5">
              <div v-for="(doc, idx) in documents" :key="'d'+idx"
                class="relative bg-[#181f28] border border-[#252d38] rounded-xl pt-6 pb-4 px-4">
                <span class="absolute -top-2.5 left-3 bg-[#1e2733] text-[#4f9eff] text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border border-[#2e3845]">
                  Doc {{ idx + 1 }}
                </span>
                <button type="button"
                  class="absolute top-2.5 right-3 text-[#3d4a58] hover:text-[#e05c56] hover:bg-[#e05c56]/10 text-xs px-1.5 py-0.5 rounded transition-colors"
                  @click="removeDoc(idx)">✕</button>

                <div class="grid grid-cols-1 sm:grid-cols-4 gap-3">
                  <FormField label="Type de document">
                    <select class="inp" v-model="doc.type_de_document">
                      <option value="" disabled>Sélectionner</option>
                      <option v-for="t in DOC_TYPES" :key="t" :value="t">{{ t }}</option>
                    </select>
                  </FormField>
                  <FormField label="Numéro / Référence">
                    <input class="inp" type="text" placeholder="CIN-12345" v-model="doc.document_numero" />
                  </FormField>
                  <FormField label="Date d'expiration">
                    <input class="inp" type="date" v-model="doc.document_date_dexpiration" />
                  </FormField>
                  <FormField label="Fichier">
                    <label class="flex items-center gap-2 cursor-pointer bg-[#1e2733] border border-[#2e3845] hover:border-[#4f9eff] hover:text-[#4f9eff] rounded-lg px-3 py-2 text-xs text-[#6b7a8d] transition-colors truncate">
                      <span class="flex-shrink-0">📎</span>
                      <span class="truncate">{{ doc._filename || 'Choisir…' }}</span>
                      <input type="file" class="hidden" accept=".pdf,.jpg,.jpeg,.png"
                        @change="onFileChange($event, idx)" />
                    </label>
                  </FormField>
                </div>
              </div>
            </TransitionGroup>

            <button type="button"
              class="flex items-center gap-2 text-[#4f9eff] text-xs font-semibold mt-3.5 px-3 py-2 rounded-lg border border-dashed border-[#2e3845] hover:border-[#4f9eff] hover:bg-[#4f9eff]/[.05] transition-colors"
              @click="addDoc">
              <span class="w-5 h-5 bg-[#4f9eff]/20 rounded flex items-center justify-center text-sm leading-none">+</span>
              Ajouter un document
            </button>

            <div class="flex justify-between items-center mt-7">
              <button type="button" class="btn-ghost" @click="step = 1">← Retour</button>
              <button type="button" class="btn-gold"  @click="step = 3">Vérifier & Soumettre →</button>
            </div>
          </div>

          <!-- ─────── ÉTAPE 3 — VÉRIFICATION ─────── -->
          <div v-else-if="step === 3" key="s3" class="card">
            <CardHeader icon="📋" title="Vérification finale" />
            <p class="text-sm text-[#6b7a8d] -mt-3 mb-6 leading-relaxed">
              Relisez votre dossier avant la soumission.
              Cliquez sur <strong class="text-[#dde4ed]">Modifier</strong> pour corriger une section.
            </p>

            <!-- Bloc Élève -->
            <RecapSection title="Élève" icon="👤" @edit="step = 0">
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-3">
                <RecapField label="Nom complet"       :val="fullName(f.prenom, f.nom)" />
                <RecapField label="Sexe"              :val="sexeLabel(f.sexe)" />
                <RecapField label="Date de naissance" :val="f.date_de_naissance || '—'" />
                <RecapField label="Lieu de naissance" :val="f.lieu_de_naissance || '—'" />
                <RecapField label="Email"             :val="f.email || '—'" />
                <RecapField label="Téléphone"         :val="f.telephone || '—'" />
                <RecapField v-if="f.adresse" label="Adresse" :val="f.adresse" wide />
              </div>
            </RecapSection>

            <!-- Bloc Formation -->
            <RecapSection title="Formation" icon="📚" @edit="step = 0">
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-3">
                <RecapField label="Niveau"           :val="niveauLabel" />
                <RecapField label="Classe"           :val="classeLabel" />
                <RecapField v-if="is_university" label="Faculté" :val="faculteLabel" />
                <RecapField label="Année académique" :val="anneeLabel" />
                <RecapField label="Aide financière"  :val="f.aide_financiere || 'Aucune'" />
                <RecapField label="Bourse"           :val="f.bourse ? '✓ Demandée' : 'Non'" />
                <RecapField label="Besoin particulier" :val="f.handicap ? '✓ Oui' : 'Non'" />
                <RecapField v-if="f.motif" label="Motif" :val="f.motif" wide />
              </div>
            </RecapSection>

            <!-- Bloc Responsable -->
            <RecapSection title="Responsable légal" icon="👨‍👩‍👧" @edit="step = 1">
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-3">
                <RecapField label="Nom complet"  :val="fullName(f.prenom_responsable, f.nom_responsable)" />
                <RecapField label="Lien"         :val="f.relation_responsable || '—'" />
                <RecapField label="Téléphone"    :val="f.telephone_responsable || '—'" />
                <RecapField label="Email"        :val="f.email_responsable || '—'" />
                <RecapField label="Profession"   :val="f.metier_responsable || '—'" />
              </div>
              <template v-if="f.nom_urgence || f.telephone_urgence">
                <p class="text-[10px] font-bold uppercase tracking-widest text-[#3d4a58] mt-3 mb-2 pt-3 border-t border-dashed border-[#252d38]">
                  Contact d'urgence
                </p>
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-3">
                  <RecapField label="Nom"       :val="f.nom_urgence || '—'" />
                  <RecapField label="Téléphone" :val="f.telephone_urgence || '—'" />
                  <RecapField label="Relation"  :val="f.relation_urgence || '—'" />
                </div>
              </template>
            </RecapSection>

            <!-- Bloc Documents -->
            <RecapSection title="Documents" icon="📁" @edit="step = 2">
              <div v-if="documents.length === 0" class="text-xs text-[#3d4a58] italic">
                Aucun document ajouté.
              </div>
              <template v-else>
                <div class="flex flex-col gap-1.5">
                  <div v-for="(doc, i) in documents" :key="i"
                    class="flex items-center gap-2.5 text-sm bg-[#111820] border border-[#252d38] rounded-lg px-3 py-2">
                    <span class="w-5 h-5 bg-[#1e2733] rounded text-[10px] font-bold text-[#6b7a8d] flex items-center justify-center flex-shrink-0">
                      {{ i + 1 }}
                    </span>
                    <span class="flex-1 font-medium text-[#dde4ed] text-[.82rem]">
                      {{ doc.type_de_document || '—' }}
                    </span>
                    <span v-if="doc.document_numero" class="text-[.72rem] font-mono text-[#6b7a8d]">
                      {{ doc.document_numero }}
                    </span>
                    <span class="text-[.73rem] font-semibold flex-shrink-0"
                      :class="doc.document_image ? 'text-[#3aad7a]' : 'text-[#e05c56]'">
                      {{ doc.document_image ? '✓ Fichier joint' : '✕ Manquant' }}
                    </span>
                  </div>
                </div>
                <p class="text-xs text-[#6b7a8d] mt-2">
                  <span :class="allDocsHaveFile ? 'text-[#3aad7a]' : 'text-[#d4893a]'" class="font-bold">
                    {{ documents.filter(d => d.document_image).length }}/{{ documents.length }}
                  </span>
                  fichier{{ documents.length > 1 ? 's' : '' }} joint{{ documents.length > 1 ? 's' : '' }}
                </p>
              </template>
            </RecapSection>

            <!-- Consentements -->
            <div class="flex flex-col gap-2.5 mt-6">
              <label class="flex items-start gap-3 p-4 rounded-xl border cursor-pointer transition-all text-sm leading-relaxed select-none"
                :class="f.cgv
                  ? 'border-[#c9a84c] bg-[#c9a84c]/[.05] text-[#dde4ed]'
                  : 'border-[#252d38] bg-[#111820] text-[#6b7a8d]'">
                <span class="w-4 h-4 rounded border-[1.5px] flex items-center justify-center flex-shrink-0 mt-0.5 transition-all"
                  :class="f.cgv ? 'bg-[#c9a84c] border-[#c9a84c]' : 'bg-[#1e2733] border-[#2e3845]'">
                  <svg v-if="f.cgv" class="w-2.5 h-2.5" fill="none" stroke="#0b0f14" stroke-width="2.5" viewBox="0 0 12 12">
                    <polyline points="2 6 5 9 10 3"/>
                  </svg>
                </span>
                <input type="checkbox" class="hidden" v-model="f.cgv" />
                <span>
                  J'accepte les <strong class="text-[#c9a84c]">conditions générales</strong>
                  et la politique de protection des données personnelles.
                  <span class="text-[#e05c56]">*</span>
                </span>
              </label>

              <label class="flex items-start gap-3 p-4 rounded-xl border cursor-pointer transition-all text-sm leading-relaxed select-none"
                :class="f.conf
                  ? 'border-[#c9a84c] bg-[#c9a84c]/[.05] text-[#dde4ed]'
                  : 'border-[#252d38] bg-[#111820] text-[#6b7a8d]'">
                <span class="w-4 h-4 rounded border-[1.5px] flex items-center justify-center flex-shrink-0 mt-0.5 transition-all"
                  :class="f.conf ? 'bg-[#c9a84c] border-[#c9a84c]' : 'bg-[#1e2733] border-[#2e3845]'">
                  <svg v-if="f.conf" class="w-2.5 h-2.5" fill="none" stroke="#0b0f14" stroke-width="2.5" viewBox="0 0 12 12">
                    <polyline points="2 6 5 9 10 3"/>
                  </svg>
                </span>
                <input type="checkbox" class="hidden" v-model="f.conf" />
                <span>
                  Je certifie que toutes les informations fournies sont exactes et sincères.
                  <span class="text-[#e05c56]">*</span>
                </span>
              </label>
            </div>

            <Transition name="fade">
              <div v-if="!f.cgv || !f.conf"
                class="mt-3 text-xs text-[#d4893a] bg-[#d4893a]/[.08] border border-[#d4893a]/20 rounded-lg px-4 py-2.5">
                ⚠ Veuillez cocher les deux déclarations pour soumettre votre dossier.
              </div>
            </Transition>

            <div class="flex justify-between items-center mt-7 flex-wrap gap-3">
              <button type="button" class="btn-ghost" @click="step = 2">← Retour</button>
              <button type="submit" class="btn-gold px-8 py-2.5 text-base"
                :disabled="f.processing || !f.cgv || !f.conf"
                :class="{ 'opacity-40 cursor-not-allowed': f.processing || !f.cgv || !f.conf }">
                <svg v-if="f.processing" class="w-4 h-4 animate-spin flex-shrink-0"
                  fill="none" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" class="opacity-25"/>
                  <path d="M4 12a8 8 0 018-8" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                </svg>
                {{ f.processing ? 'Envoi en cours…' : 'Soumettre ma candidature' }}
              </button>
            </div>
          </div>

        </Transition>
      </form>
    </main>

    <AppToast :show="toast.show" :message="toast.message" :ok="toast.ok" />
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, computed, h, defineComponent } from 'vue'
import { DOCS_BASE } from '@/data/index.js'
import { initReveal } from '@/composables/useReveal.js'
import { storeToRefs } from 'pinia'
import { useSchoolStoreInfo } from '@/stores/schoolStore'
import AppToast from '@/components/AppToast.vue'
import { useToast } from '@/composables/useToast'
import axios from 'axios'
import { usePdfWithLoading } from '@/stores/usePdf';
const { submitPdf, loading, errors, loadingMap } = usePdfWithLoading()
const { toast, success, error } = useToast()
const schoolStore = useSchoolStoreInfo()
const { classes_global, annee_global, niveau_global, faculte } = storeToRefs(schoolStore)

/* ── Sub-components ───────────────────────────────────── */

const CardHeader = defineComponent({
  props: ['icon', 'title'],
  setup: (p) => () => h('div', { class: 'flex items-center gap-3 pb-5 mb-6 border-b border-[#252d38]' }, [
    h('span', { class: 'text-2xl' }, p.icon),
    h('h2',  { class: 'text-[1.05rem] font-bold tracking-tight text-[#dde4ed] m-0' }, p.title),
  ]),
})

const Fieldset = defineComponent({
  props: ['legend'],
  setup: (p, { slots }) => () => h('fieldset', {
    class: 'border border-[#252d38] rounded-xl p-0 m-0 overflow-hidden',
  }, [
    h('legend', {
      class: 'block w-full px-4 py-2 text-[.6rem] font-bold uppercase tracking-[.13em] text-[#6b7a8d] bg-[#181f28] border-b border-[#252d38] float-none',
    }, p.legend),
    h('div', { class: 'p-4' }, slots.default?.()),
  ]),
})

const FormField = defineComponent({
  props: ['label', 'error'],
  setup: (p, { slots }) => () => h('div', { class: 'flex flex-col gap-1.5' }, [
    h('label', { class: 'text-[.62rem] font-bold uppercase tracking-[.1em] text-[#6b7a8d]' }, p.label),
    slots.default?.(),
    p.error
      ? h('span', { class: 'text-[.72rem] text-[#e05c56]' }, p.error)
      : null,
  ]),
})

const ToggleCard = defineComponent({
  props: ['icon', 'title', 'sub', 'on'],
  emits: ['toggle'],
  setup: (p, { emit }) => () => h('button', {
    type: 'button',
    class: [
      'flex items-start gap-3 p-4 rounded-xl border text-left w-full cursor-pointer transition-all',
      p.on ? 'border-[#c9a84c] bg-[#c9a84c]/[.06]' : 'border-[#252d38] bg-[#181f28]',
    ],
    onClick: () => emit('toggle'),
  }, [
    h('span', {
      class: [
        'w-[18px] h-[18px] rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center text-[9px] font-black transition-all',
        p.on ? 'bg-[#c9a84c] border-[#c9a84c] text-[#0b0f14]' : 'bg-[#1e2733] border-[#2e3845]',
      ],
    }, p.on ? '✓' : ''),
    h('span', { class: 'flex flex-col gap-0.5' }, [
      h('span', { class: 'text-[.82rem] font-semibold text-[#dde4ed]' }, `${p.icon} ${p.title}`),
      h('span', { class: 'text-[.71rem] text-[#6b7a8d]' }, p.sub),
    ]),
  ]),
})

const RecapSection = defineComponent({
  props: ['title', 'icon'],
  emits: ['edit'],
  setup: (p, { slots, emit }) => () => h('div', {
    class: 'border border-[#252d38] rounded-xl overflow-hidden mb-3.5',
  }, [
    h('div', { class: 'flex justify-between items-center px-4 py-2.5 bg-[#181f28] border-b border-[#252d38]' }, [
      h('span', { class: 'text-[.62rem] font-bold uppercase tracking-[.12em] text-[#6b7a8d]' }, `${p.icon} ${p.title}`),
      h('button', {
        type: 'button',
        class: 'text-[.7rem] font-semibold text-[#c9a84c] bg-transparent border border-[#c9a84c]/30 rounded-full px-3 py-0.5 cursor-pointer hover:bg-[#c9a84c]/10 transition-colors',
        onClick: () => emit('edit'),
      }, 'Modifier'),
    ]),
    h('div', { class: 'p-4' }, slots.default?.()),
  ]),
})

const RecapField = defineComponent({
  props: ['label', 'val', 'wide'],
  setup: (p) => () => h('div', {
    class: ['flex flex-col gap-0.5', p.wide ? 'col-span-2 sm:col-span-3' : ''],
  }, [
    h('span', { class: 'text-[.59rem] uppercase tracking-[.09em] text-[#3d4a58]' }, p.label),
    h('span', { class: 'text-[.84rem] font-medium text-[#dde4ed] break-words leading-snug' }, p.val ?? '—'),
  ]),
})

/* ── Constants ────────────────────────────────────────── */
const STEPS = ['Informations', 'Tuteur', 'Documents', 'Vérification']
const DOC_TYPES = [
  'Certificat de naissance', "Carte d'identité", 'Passeport',
  'Diplôme', 'Relevé de notes', 'Attestation', "Photo d'identité", 'Autre',
]

/* ── State ────────────────────────────────────────────── */
const step   = ref(0)
const done   = ref(false)
const admRef = ref('')
const student_id = ref('')

const newDoc = () => ({
  type_de_document: '', document_numero: '',
  document_date_dexpiration: '', document_status: '',
  document_image: null, _filename: '', etudiant_id: '',
})
const documents = ref([newDoc()])

const INIT = {
  documentss: [], id: '', dernier_etablissement: '', nisu: '',
  aide_financiere: 'Aucune', nom: '', prenom: '', telephone: '',
  sexe: '', date_de_naissance: '', adresse: '', lieu_de_naissance: '',
  religion: '', niveau_id: '', classe_actuelle_id: '', annee_academique_id: '',
  faculte_id: '', email: '', motif: '',
  nom_responsable: '', prenom_responsable: '', email_responsable: '',
  relation_responsable: '', sexe_responsable: 'F', telephone_responsable: '',
  metier_responsable: '', adresse_responsable: '',
  nom_urgence: '', telephone_urgence: '', relation_urgence: '',
  bourse: false, handicap: false, cgv: false, conf: false,
  errors: {}, processing: false,
}
const f = reactive({ ...INIT })

/* ── Computed ─────────────────────────────────────────── */
const currentYear    = computed(() => annee_global.value?.find(x => x.status == 1))

const is_university  = computed(() => ['Universitaire','Technique'].includes(niveau_global.value?.find(x => x.id === f.niveau_id)?.name))

const classesFiltrees = computed(() => f.niveau_id && classes_global.value ? classes_global.value.filter(c => c.niveau_id === f.niveau_id) : [])

const niveauLabel    = computed(() => niveau_global.value?.find(x => x.id === f.niveau_id)?.name || '—')
const classeLabel    = computed(() => classes_global.value?.find(x => x.id === f.classe_actuelle_id)?.nom_classe || '—')

const faculteLabel   = computed(() => faculte.value?.find(x => x.id === f.faculte_id)?.nom || '—')

const anneeLabel     = computed(() => annee_global.value?.find(x => x.id === f.annee_academique_id)?.annee_academique || '—')

const allDocsHaveFile = computed(() => documents.value.every(d => d.document_image))

/* ── Watchers ─────────────────────────────────────────── */
watch(() => f.niveau_id, () => { f.classe_actuelle_id = ''; f.faculte_id = ''
 })
watch(step, () => window.scrollTo({ top: 260, behavior: 'smooth' }))

/* ── Helpers ──────────────────────────────────────────── */
const fullName  = (p, n) => [p, n].filter(Boolean).join(' ') || '—'
const sexeLabel = v => ({ F: 'Féminin', M: 'Masculin', A: 'Autre' }[v] || '—')
const addDoc    = () => documents.value.push(newDoc())
const removeDoc = i  => documents.value.splice(i, 1)
const onFileChange = (e, i) => {
  const file = e.target.files[0]; if (!file) return
  documents.value[i]._filename = file.name
  const r = new FileReader()
  r.onload = () => { documents.value[i].document_image = r.result }
  r.readAsDataURL(file)
}

/* ── Step 0 validation ────────────────────────────────── */
const REQUIRED_0 = ['nom','prenom','sexe','date_de_naissance','lieu_de_naissance','email','niveau_id','classe_actuelle_id','annee_academique_id']
const goStep0 = () => {
  f.errors = {}
  REQUIRED_0.forEach(k => { if (!f[k]) f.errors[k] = 'Champ requis' })
  if (Object.keys(f.errors).length) return
  step.value = 1
}

/* ── Submit ───────────────────────────────────────────── */
const submitForm = async () => {
  f.documentss = documents.value.map(({ _filename, ...rest }) => rest)
  f.errors = {}; f.processing = true
  try {
    const r = await axios.post('/student-register', f)
    if (r.data) {
      console.log(r.data);
      
      admRef.value = r?.data?.identifiant || Math.random().toString(36).substring(2,8).toUpperCase()
      student_id.value =r?.data?.id
      success(r.data.success || 'Candidature soumise.', true)
      done.value = true
    }
  } catch (e) {
    console.log(e.response?.data);
    
    if (e.response?.data?.detail) error(e.response.data.detail, false)
    if (e.response?.data?.errors) f.errors = e.response.data.errors
  } finally { f.processing = false }
}

/* ── Reset ────────────────────────────────────────────── */
const reset = () => {
  done.value = false; step.value = 0
  documents.value = [newDoc()]
  Object.assign(f, { ...INIT, errors: {}, processing: false })
}

onMounted(() => { schoolStore.fetchAllDependencies(); window.scrollTo(0,0); initReveal() })
</script>

<style scoped>
/* ─── Card ──────────────────────────────────────────────────────── */
.card {
  background: #111820;
  border: 1px solid #252d38;
  border-radius: 1rem;
  padding: 1.75rem;
  margin-top: 1.5rem;
  box-shadow: 0 12px 40px rgba(0, 0, 0, .5);
}

/* ─── Inputs ────────────────────────────────────────────────────── */
.inp {
  width: 100%;
  background: #181f28;
  border: 1px solid #2e3845;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  color: #dde4ed;
  font-size: 0.84rem;
  outline: none;
  transition: border-color .15s, box-shadow .15s;
  box-sizing: border-box;
}
.inp::placeholder {
  color: #3d4a58;
}
.inp:focus {
  border-color: #4f9eff;
  box-shadow: 0 0 0 3px rgba(79, 158, 255, .1);
}
.inp:disabled {
  opacity: .4;
  cursor: not-allowed;
}
.inp-err {
  border-color: #e05c56 !important;
}
.inp[type="date"]::-webkit-calendar-picker-indicator {
  filter: invert(.4);
}
select.inp {
  appearance: none;
  -webkit-appearance: none;
  padding-right: 2rem;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%236b7a8d'%3E%3Cpath fill-rule='evenodd' d='M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 14px;
}
select.inp option {
  background: #181f28;
}

/* ─── Buttons ───────────────────────────────────────────────────── */
.btn-gold {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #c9a84c;
  color: #0b0f14;
  font-weight: 700;
  border: none;
  border-radius: 9999px;
  padding: 0.625rem 1.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background .15s, transform .1s;
}
.btn-gold:hover:not(:disabled) {
  background: #dfc06a;
  transform: translateY(-1px);
}
.btn-gold:disabled {
  opacity: .4;
  cursor: not-allowed;
}
.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  border: 1px solid #2e3845;
  color: #6b7a8d;
  font-weight: 600;
  border-radius: 9999px;
  padding: 0.625rem 1.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: border-color .15s, color .15s;
}
.btn-ghost:hover {
  border-color: #6b7a8d;
  color: #dde4ed;
}

/* ─── Vue Transitions ───────────────────────────────────────────── */
.panel-enter-active,
.panel-leave-active { transition: opacity .22s ease, transform .22s ease; }
.panel-enter-from   { opacity: 0; transform: translateY(12px); }
.panel-leave-to     { opacity: 0; transform: translateY(-8px); }

.doc-enter-active { transition: all .22s ease; }
.doc-leave-active { transition: all .18s ease; position: absolute; }
.doc-enter-from   { opacity: 0; transform: translateX(-8px); }
.doc-leave-to     { opacity: 0; transform: translateX(8px); }

.fade-enter-active,
.fade-leave-active { transition: opacity .2s; }
.fade-enter-from,
.fade-leave-to     { opacity: 0; }
</style>


