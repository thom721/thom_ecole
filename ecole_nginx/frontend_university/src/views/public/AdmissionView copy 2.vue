<template>
  <div>
    <!-- ══ HERO ══════════════════════════════════════════ -->
    <div class="relative overflow-hidden" style="height:58vh;min-height:280px">
      <img
        src="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1800&q=80"
        alt="Admission"
        class="hero-img w-full h-full object-cover block"
      />
      <div class="absolute inset-0" style="background:linear-gradient(135deg,rgba(26,122,110,.92),rgba(11,31,58,.75),rgba(212,168,83,.25))"></div>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <p class="text-xs font-bold mb-3" style="color:#fde68a;letter-spacing:.3em;text-transform:uppercase">Inscriptions {{ annee_global?.find(x=>x.status==1)?.annee_academique }}</p>
        <h1 class="font-serif text-white mb-4" style="font-size:clamp(2rem,4.5vw,3.8rem)">
          Demande d'<span class="text-gold">Admission</span>
        </h1>
        <p style="color:rgba(255,255,255,.8)" class="max-w-md leading-relaxed">
          Complétez votre dossier en ligne en quelques étapes. Traitement garanti sous 24h.
        </p>
      </div>
    </div>
<!-- {{ niveau_global }} -->
    <!-- ══ BARRE DE PROGRESSION ══════════════════════════ -->
    <div class="bg-[#21262d] sticky top-16 z-40" style="box-shadow:0 2px 12px rgba(11,31,58,.07)">
      <div class="max-w-6xl mx-auto px-6 pt-5">
        <div class="flex items-center">
          <template v-for="(s, i) in ADM_STEPS" :key="i">
            <div class="flex flex-col items-center gap-1">
              <div class="step-circle" :class="step > i ? 'done' : step === i ? 'current' : 'todo'">
                <template v-if="step > i">
                  <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </template>
                <template v-else>{{ i + 1 }}</template>
              </div>
              <span
                class="text-xs font-semibold hidden sm:block"
                :class="step > i ? 'text-green-500' : step === i ? 'text-gold' : 'text-gray-300'"
              >{{ s.l }}</span>
            </div>
            <div v-if="i < ADM_STEPS.length - 1" class="step-line" :class="step > i ? 'done' : 'todo'" style="margin-bottom:20px"></div>
          </template>
        </div>
        <div class="prog-bar mt-3">
          <div class="prog-fill" :style="{ width: (step / (ADM_STEPS.length - 1) * 100) + '%' }"></div>
        </div>
      </div>
      <div class="flex justify-around border-b-2 border-gray-50 px-6 max-w-4xl mx-auto mt-2 overflow-x-auto">
        <button
          v-for="(s, i) in ADM_STEPS"
          :key="i"
          class="tab-btn"
          :class="{ active: step === i }"
          @click="step = i"
        >{{ s.icon }} {{ s.l }}</button>
      </div>
    </div>

    <!-- ══ PANELS ═════════════════════════════════════════ -->
    <div class="max-w-6xl mx-auto px-6 pb-16">
   <form @submit.prevent="submitEtudiant">
        <Transition name="tab-slide" mode="out-in">
      <!-- Succès -->
      <div v-if="done" class="mt-8 rounded-3xl py-16 px-10 text-center" style="background:linear-gradient(135deg,#1A7A6E,#0f5e54)">
        <div style="font-size:5rem" class="mb-4">🎉</div>
        <h2 class="font-serif text-white text-4xl mb-3">Dossier envoyé avec succès !</h2>
        <p class="mb-2 max-w-sm mx-auto" style="color:rgba(255,255,255,.8)">
          Notre équipe examinera votre candidature sous 24h et vous contactera par email.
        </p>
        <p class="mb-8 text-sm" style="color:rgba(255,255,255,.65)">
          Référence : <strong class="text-white">ADM-{{ admRef }}</strong>
        </p>
        <button class="btn-gold px-8 py-3.5 rounded-full font-semibold" @click="reset">Nouvelle candidature</button>
      </div>
   
      <!-- Étape 0 — Élève -->
          <div v-else-if="step === 0" class="bg-white rounded-3xl p-10 mt-8" style="box-shadow:0 16px 48px rgba(11,31,58,.12)">
            <SectionCard title="Informations Personnel" icon="📚">
            <!-- <div class="text-xs font-bold uppercase tracking-widest text-gold flex items-center gap-2.5 mb-5">
              <span class="w-5 h-0.5 bg-gold inline-block"></span> Informations sur l'élève
            </div> -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div><label class="field-label">Nom *</label><input class="field-input" :class="{'input-err': f.errors?.nom}" type="text" placeholder="Dupont" v-model="f.nom" /></div>
              <div><label class="field-label">Prénom *</label><input class="field-input" :class="{'input-err': f.errors?.prenom}" type="text" placeholder="Marie" v-model="f.prenom" /></div>
              <div><label class="field-label">Date de naissance *</label><input class="field-input" :class="{'input-err': f.errors?.date_de_naissance}" type="date" v-model="f.date_de_naissance" />
              </div>

              <div>
                <label class="field-label">Lieu de naissance *</label><input class="field-input" :class="{'input-err': f.errors?.lieu_de_naissance}" type="text" v-model="f.lieu_de_naissance" /></div>
              <div>
                <label class="field-label">sexe *</label>
                <select class="field-select"  :class="{'input-err': f.errors?.sexe}" v-model="f.sexe">
                  <option value="">Choisir…</option>
                  <option value="F">Féminin</option><option value="M">Masculin</option><option value="A">Autre</option>
                </select>
              </div>
              <div><label class="field-label">Email *</label><input class="field-input"  :class="{'input-err': f.errors?.email}" type="email" placeholder="marie@exemple.fr" v-model="f.email" /></div>
              <div><label class="field-label">Téléphone</label><input class="field-input" type="tel" placeholder="+33 6 00 00 00 00" v-model="f.telephone" /></div>
              <div class="sm:col-span-2"><label class="field-label">Adresse *</label><input class="field-input" type="text" placeholder="12 rue de la Paix, 75001 Paris" v-model="f.adresse" /></div>
            </div>

            <!-- <div class="text-xs font-bold uppercase tracking-widest text-gold flex items-center gap-2.5 mb-4 mt-7">
              <span class="w-5 h-0.5 bg-gold inline-block"></span> Formation souhaitée
            </div> -->
            </SectionCard>
            <SectionCard title="Formation souhaitée" icon="📚" class="mt-4">
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label class="field-label">Niveau visé *</label>
                <select class="field-select"  :class="{'input-err': f.errors?.niveau_id}" v-model="f.niveau_id">
                  <option value="">Choisir…</option>
                  <option v-for="niveau in niveau_global" :value="niveau.id" :key="niveau.id">{{niveau.name}}</option> 
                </select>
              </div>
                <div>
                <label class="field-label">Classe *</label>
                <select class="field-input"  :class="{'input-err': f.errors?.classe_actuelle_id}" v-model="f.classe_actuelle_id">
                  <option value="">Choisir…</option>
                  <option v-for="classe in getClassesByNiveau(f.niveau_id)" :value="classe.id" :key="classe.id">{{classe.nom_classe}}</option> 
                </select>
              </div> 
              <div v-if="is_university">
                <label class="field-label">Faculté / Domaine *</label>
                <select class="field-input"  :class="{'input-err': f.errors?.faculte_id}"  v-model="f.faculte_id">
                  <option value="">Choisir…</option>
                  <option v-for="faculte in faculte" :value="faculte.id" :key="faculte.id">{{faculte.nom}}</option> 
                </select>
              </div>
              <div>
                <label class="field-label">Année scolaire</label>
                <select class="field-input"  :class="{'input-err': f.errors?.annee_academique_id}"  v-model="f.annee_academique_id">
                  <option value="" disabled="">Année Académique</option>
                  <option v-for="value in annee_global" :key="value" value="value.id">{{ value.annee_academique }}</option>
                </select>
              </div>
              <div class="sm:col-span-2">
                <label class="field-label">Motif de candidature</label>
                <textarea class="field-input" rows="3" placeholder="Expliquez votre motivation…" v-model="f.motif"></textarea>
              </div>
            </div>
            </SectionCard>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-6 mb-7">
              <div class="radio-card" :class="{ on: f.bourse }" @click="f.bourse = !f.bourse">
                <div class="rounded-full border-2 flex items-center justify-center flex-shrink-0" :class="f.bourse ? 'border-gold' : 'border-gray-300'" style="width:18px;height:18px">
                  <div v-if="f.bourse" class="rounded-full bg-gold" style="width:9px;height:9px"></div>
                </div>
                <div>
                  <div class="font-semibold text-sm">🎓 Demande de bourse</div>
                  <div class="text-gray-400 text-xs mt-0.5">Joindre attestation dans les documents</div>
                </div>
              </div>
              <div class="radio-card" :class="{ on: f.handicap }" @click="f.handicap = !f.handicap">
                <div class="rounded-full border-2 flex items-center justify-center flex-shrink-0" :class="f.handicap ? 'border-gold' : 'border-gray-300'" style="width:18px;height:18px">
                  <div v-if="f.handicap" class="rounded-full bg-gold" style="width:9px;height:9px"></div>
                </div>
                <div>
                  <div class="font-semibold text-sm">♿ Besoin particulier</div>
                  <div class="text-gray-400 text-xs mt-0.5">Aménagement pédagogique requis</div>
                </div>
              </div>
            </div>
            <div class="flex justify-end">
              <button type="button" class="btn-gold px-7 py-3 rounded-full font-semibold" @click="step = 1">Tuteur / Responsable →</button>
            </div>
          </div>

          <!-- Étape 1 — Tuteur -->
          <div v-else-if="step === 1" class="bg-white rounded-3xl p-10 mt-8" style="box-shadow:0 16px 48px rgba(11,31,58,.12)">
            <SectionCard title="Responsable légal" icon="">
          
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label class="field-label">Lien de parenté *</label>
                <select class="field-input" v-model="f.relation_responsable">
                  <option value="">Choisir…</option>
                  <option>Père</option><option>Mère</option><option>Tuteur légal</option><option>Grand-parent</option><option>Autre</option>
                </select>
              </div>
              <div>
                <label class="field-label">Civilité</label>
                <select class="field-input" v-model="f.tCiv"><option>Madame</option><option>Monsieur</option></select>
              </div>
              <div><label class="field-label">Nom *</label><input class="field-input" type="text" placeholder="Dupont" v-model="f.nom_responsable" /></div>
              <div><label class="field-label">Prénom *</label><input class="field-input" type="text" placeholder="Jean" v-model="f.prenom_responsable" /></div>
              <div><label class="field-label">Téléphone *</label><input class="field-input" type="tel" v-model="f.tTel" /></div>
              <div><label class="field-label">Email *</label><input class="field-input" type="email" v-model="f.email_responsable" /></div>
              <div class="sm:col-span-2"><label class="field-label">Profession</label><input class="field-input" type="text" placeholder="Ingénieur" v-model="f.metier_responsable" /></div>
            </div>
            </SectionCard>

            <!-- <div class="flex gap-3.5 items-start p-4 rounded-2xl mt-6 mb-4" style="background:rgba(212,168,83,.07);border:1.5px solid rgba(212,168,83,.25)">
              <div class="text-2xl">🚨</div>
              <div>
                <h4 class="text-sm font-bold text-gold mb-1">Contact d'urgence</h4>
                <p class="text-xs text-gray-400">Personne à contacter en cas d'urgence, autre que le responsable légal</p>
              </div>
            </div> -->
            <SectionCard title="Contact d'urgence" icon="🚨" class="mt-4">
              <p class="text-xs text-gray-400 py-2">Personne à contacter en cas d'urgence, autre que le responsable légal</p>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div><label class="field-label">Nom complet</label><input class="field-input" type="text" placeholder="Marie Martin" v-model="f.nom_responsable" /></div>
              <div><label class="field-label">Téléphone</label><input class="field-input" type="tel" v-model="f.telephone_responsable" /></div>
              <div><label class="field-label">Relation</label><input class="field-input" type="text" placeholder="Tante" v-model="f.relation_responsable" /></div>
            </div>
</SectionCard>
            <div class="flex justify-between mt-7">
              <button class="btn-outline px-7 py-3 rounded-full font-semibold" @click="step = 0">← Retour</button>
              <button class="btn-gold px-7 py-3 rounded-full font-semibold" @click="step = 2">Documents →</button>
            </div>
          </div>

          <!-- Étape 2 — Documents -->
          <div v-else-if="step === 2" class="bg-white rounded-3xl p-10 mt-8" style="box-shadow:0 16px 48px rgba(11,31,58,.12)">
            <div class="flex gap-3.5 items-start p-4 rounded-xl mb-6 bg-[#21262d] border border-[#161b22] " >
              <div class="text-2xl">ℹ️</div>
              <div>
                <h4 class="text-sm font-bold text-slate-300 mb-1">Formats acceptés : PDF, JPG, PNG — Max 5 Mo</h4>
                <p class="text-xs text-gray-400">Documents lisibles et à jour. Les originaux pourront être demandés .</p>
              </div>
              <!-- lors de l'entretien -->
            </div>

            <SectionCard title="Pièces soumises" icon="📎">
              <TransitionGroup name="doc-list" tag="div" class="space-y-3">
                <div
                  v-for="(doc, index) in documents" :key="index"
                  class="relative group bg-[#0d1117] border border-[#21262d] hover:border-[#30363d] rounded-xl p-4 transition-all duration-200"
                >
                  <span class="absolute -top-2.5 left-4 bg-[#21262d] text-[#58a6ff] text-[10px] font-mono px-2 py-0.5 rounded-full border border-[#30363d]">
                    Doc {{ index + 1 }}
                  </span>
                  <p v-if="faculte.errors?.[`documentss.${index}.type_de_document`]"
                    class="text-[#f85149] text-[12px] mb-2">
                    {{ f.errors[`documentss.${index}.type_de_document`] }}
                  </p>
                  <div class="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
                    <FormField label="Type">
                      <select class="field-select" v-model="doc.type_de_document">
                        <option value="" disabled>Sélectionner</option>
                        <option v-for="type in documentTypes" :key="type" :value="type">{{ type }}</option>
                      </select>
                    </FormField>
                    <FormField label="Numéro">
                      <input class="field-input" type="text" v-model="doc.document_numero" placeholder="ex: CIN-12345" />
                    </FormField>
                    <FormField label="Expiration">
                      <input class="field-input" type="date" v-model="doc.document_date_dexpiration" />
                    </FormField>
                    <FormField label="Fichier">
                      <label class="flex items-center gap-2 cursor-pointer bg-[#161b22] border border-[#30363d] hover:border-[#58a6ff]/50 rounded-lg px-3 py-2 transition-colors">
                        <span class="text-[#58a6ff]">📁</span>
                        <span class="text-[12px] text-[#7d8590] truncate">
                          {{ doc.document_image ? 'Sélectionné ✓' : 'Choisir un fichier' }}
                        </span>
                        <input type="file" class="hidden" @change="handleFileChange($event, index)" />
                      </label>
                    </FormField>
                  </div>
                  <button
                    type="button" @click="removeDocument(index)"
                    class="absolute top-3 right-3 opacity-0 group-hover:opacity-100 text-[#7d8590] hover:text-[#f85149] transition-all duration-150"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
                      <path d="M5.28 4.22a.75.75 0 0 0-1.06 1.06L6.94 8l-2.72 2.72a.75.75 0 1 0 1.06 1.06L8 9.06l2.72 2.72a.75.75 0 1 0 1.06-1.06L9.06 8l2.72-2.72a.75.75 0 0 0-1.06-1.06L8 6.94 5.28 4.22Z" />
                    </svg>
                  </button>
                </div>
              </TransitionGroup>

              <button type="button" @click="addDocument"
                class="mt-4 flex items-center gap-2 text-[#58a6ff] hover:text-[#79c0ff] text-[13px] font-medium transition-colors group">
                <span class="w-6 h-6 rounded-md bg-[#1f6feb]/20 border border-[#1f6feb]/30 flex items-center justify-center group-hover:bg-[#1f6feb]/30 transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
                    <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
                  </svg>
                </span>
                Ajouter un document
              </button>
            </SectionCard>

            <!-- <div class="text-xs font-bold uppercase tracking-widest text-gold flex items-center gap-2.5 mb-4">
              <span class="w-5 h-0.5 bg-gold inline-block"></span> Documents obligatoires
            </div>
            <div v-for="(doc, i) in docs" :key="'o' + i" class="doc-row" :class="{ ok: doc.document_image }">
              <div
                class="rounded-xl flex items-center justify-center text-lg flex-shrink-0"
                :style="{ background: doc.document_image ? 'rgba(26,122,110,.1)' : 'rgba(11,31,58,.05)', width: '40px', height: '40px' }"
              >{{ doc.i }}</div>
              <div class="flex-1">
                <div class="font-semibold text-sm">{{ doc.type_de_document }} <span class="text-red-400 text-xs">*</span></div>
                <div class="text-gray-400 text-xs mt-0.5">{{ doc.h }}</div>
              </div>
              <div class="flex-shrink-0">
                <div v-if="doc.document_image" class="flex items-center gap-1.5 text-xs font-semibold text-teal py-1.5 px-3 rounded-xl" style="background:rgba(26,122,110,.08)">
                  <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                  <span class="max-w-[80px] overflow-hidden text-ellipsis whitespace-nowrap">{{ doc.document_image }}</span>
                  <button @click="doc.f = null" class="bg-transparent border-none text-gray-300 cursor-pointer text-base leading-none ml-1 hover:text-red-400">×</button>
                </div>
                <label v-else class="upload-label">
                  Choisir
                   <input type="file" class="hidden" @change="handleFileChange($event, index)" />
                   
                  <input type="file" accept=".pdf,.jpg,.jpeg,.png" class="hidden" @change="e => { if (e.target.files[0]) doc.document_image = e.target.files[0].name }" />
                </label>
              </div>
            </div> -->

            <!-- Récap -->
            <div class="rounded-2xl p-5 mt-4 mb-4" style="background:#FAF7F2">
              <div class="font-bold text-sm mb-3">
                Récapitulatif —
                <span :class="docs.filter(d => d.document_image).length === docs.length ? 'text-teal' : 'text-gold'">
                  {{ docs.filter(d => d.document_image).length }}/{{ docs.length }}
                </span> obligatoires fournis
              </div>
              <div class="grid grid-cols-2 gap-1.5">
                <div v-for="d in docs" :key="d.type_de_document" class="text-sm">
                  {{ d.document_image ? '✅' : '⬜' }}
                  <span :class="d.document_image ? 'text-navy' : 'text-gray-400'">{{ d.type_de_document }}</span>
                </div>
              </div>
            </div>

            <div class="flex justify-between">
              <button class="btn-outline px-7 py-3 rounded-full font-semibold" @click="step = 1">← Retour</button>
              <button class="btn-gold px-7 py-3 rounded-full font-semibold" @click="step = 3">Vérifier & Soumettre →</button>
            </div>
          </div>

          <!-- Étape 3 — Vérification -->
          <div v-else-if="step === 3" class="bg-white rounded-3xl p-10 mt-8" style="box-shadow:0 16px 48px rgba(11,31,58,.12)">
            <div class="text-center mb-8">
              <div class="text-6xl mb-3">📋</div>
              <h2 class="font-serif text-3xl mb-2">Vérification finale</h2>
              <p class="text-gray-400 text-sm">Relisez votre dossier avant la soumission définitive.</p>
            </div>

            <!-- Récap élève -->
            <div class="rounded-2xl p-5 mb-4" style="background:#FAF7F2">
              <div class="flex justify-between items-center mb-3.5">
                <h3 class="font-bold text-sm">👤 Élève</h3>
                <button class="text-gold text-xs font-semibold bg-transparent border-none cursor-pointer" @click="step = 0">Modifier</button>
              </div>
              <div class="grid grid-cols-2 gap-2 text-sm">
                <div><span class="text-gray-400">Nom : </span><span class="font-semibold">{{ f.prenom }} {{ f.nom }}</span></div>
                <div><span class="text-gray-400">Email : </span><span class="font-semibold">{{ f.email || '—' }}</span></div>
                <div><span class="text-gray-400">Niveau : </span><span class="font-semibold">{{ f.niveau || '—' }}</span></div>
                <div><span class="text-gray-400">Naissance : </span><span class="font-semibold">{{ f.dob || '—' }}</span></div>
              </div>
            </div>

            <!-- Récap tuteur -->
            <div class="rounded-2xl p-5 mb-4" style="background:#FAF7F2">
              <div class="flex justify-between items-center mb-3.5">
                <h3 class="font-bold text-sm">👨‍👩‍👧 Responsable</h3>
                <button class="text-gold text-xs font-semibold bg-transparent border-none cursor-pointer" @click="step = 1">Modifier</button>
              </div>
              <div class="grid grid-cols-2 gap-2 text-sm">
                <div><span class="text-gray-400">Nom : </span><span class="font-semibold">{{ f.tPrenom }} {{ f.tNom }}</span></div>
                <div><span class="text-gray-400">Lien : </span><span class="font-semibold">{{ f.tLien || '—' }}</span></div>
                <div><span class="text-gray-400">Tél : </span><span class="font-semibold">{{ f.tTel || '—' }}</span></div>
                <div><span class="text-gray-400">Email : </span><span class="font-semibold">{{ f.tEmail || '—' }}</span></div>
              </div>
            </div>

            <!-- Récap docs -->
            <div class="rounded-2xl p-5 mb-5" style="background:#FAF7F2">
              <div class="flex justify-between items-center mb-3.5">
                <h3 class="font-bold text-sm">📁 Documents ({{ docs.filter(d => d.f).length }}/{{ docs.length }})</h3>
                <button class="text-gold text-xs font-semibold bg-transparent border-none cursor-pointer" @click="step = 2">Modifier</button>
              </div>
              <div class="grid grid-cols-2 gap-1.5 text-sm">
                <div v-for="d in docs" :key="d.n">
                  {{ d.f ? '✅' : '❌' }} <span :class="d.f ? 'text-navy' : 'text-red-400'">{{ d.n }}</span>
                </div>
              </div>
            </div>

            <!-- Consentements -->
            <div class="consent-row" :class="{ on: f.cgv }" @click="f.cgv = !f.cgv">
              <input type="checkbox" :checked="f.cgv" @change="f.cgv = !f.cgv" style="width:16px;height:16px;accent-color:#D4A853;flex-shrink:0;margin-top:2px" />
              <p class="text-sm text-gray-500 leading-relaxed">J'accepte les <strong class="text-gold">conditions générales</strong> et la politique de protection des données. *</p>
            </div>
            <div class="consent-row" :class="{ on: f.conf }" @click="f.conf = !f.conf">
              <input type="checkbox" :checked="f.conf" @change="f.conf = !f.conf" style="width:16px;height:16px;accent-color:#D4A853;flex-shrink:0;margin-top:2px" />
              <p class="text-sm text-gray-500 leading-relaxed">Je certifie que toutes les informations fournies sont exactes et sincères. *</p>
            </div>

            <div class="flex justify-between items-center mt-7">
              <button class="btn-outline px-7 py-2 rounded-full font-semibold" @click="step = 2">← Retour</button>
              <button type="submit"
                class="btn-gold px-8 py-2 rounded-full font-semibold"
                :disabled="f.processing"
                :class="{ 'opacity-40 cursor-not-allowed': f.processing }"
                 
              >
              <svg v-if="!f.processing" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
                  <path d="M12.78 5.22a.749.749 0 0 1 0 1.06l-4.25 4.25a.749.749 0 0 1-1.06 0L5.22 8.28a.749.749 0 1 1 1.06-1.06L8 8.94l3.72-3.72a.749.749 0 0 1 1.06 0Z" />
                </svg>
              <svg v-if="f.processing" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              
               {{ f.processing ? 'Enregistrement cours…' : 'Soumettre ma candidature' }}
            
            </button>
            </div>
          </div>
      
        </Transition>
    </form>

    </div>
  <AppToast :show="toast.show" :message="toast.message" :ok="toast.ok" />
  </div>

</template>

<script setup>
import { ref, reactive, watch, onMounted, computed, h,defineComponent } from 'vue'
import { DOCS_BASE } from '@/data/index.js'
import { initReveal } from '@/composables/useReveal.js'
import { storeToRefs } from 'pinia';
import { useSchoolStoreInfo } from '@/stores/schoolStore';
import AppToast from '@/components/AppToast.vue';
import { useToast } from '@/composables/useToast';
import axios from 'axios';
const { toast, success, error } = useToast();
const schoolStore = useSchoolStoreInfo();
const { classes_global, annee_global, niveau_global,faculte } = storeToRefs(schoolStore);
 
// ── Données statiques ─────────────────────────
const ADM_STEPS = [
  { l: 'Informations', icon: '👤' },
  { l: 'Tuteur',       icon: '👨‍👩‍👧' },
  { l: 'Documents',    icon: '📁' },
  { l: 'Vérification', icon: '✅' },
]

// ── State ─────────────────────────────────────
const step   = ref(0)
const done   = ref(false)
const admRef = ref('')
const docs   = ref(DOCS_BASE.map(d => ({ ...d })))

const documentTypes = [
  'Attestation', 'Certificat', 'Certificat de naissance',
  "Carte d'identité", 'Diplôme', 'Relevé de notes',
  "Photo d'identité", 'Autre',
];

const documents = ref([{
  type_de_document: '', document_numero: '',
  document_date_dexpiration: '', document_status: '',
  document_image: '', etudiant_id: '',
}]);


const addDocument = () => documents.value.push({
  type_de_document: '', document_numero: '',
  document_date_dexpiration: '', document_status: '',
  document_image: '', etudiant_id: '',
});
const removeDocument = (i) => documents.value.splice(i, 1);

const handleFileChange = (e, i) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => { documents.value[i].document_image = reader.result; };
  reader.readAsDataURL(file);
};

const f = reactive({
  documentss: [], id: '', dernier_etablissement: '', nisu: '',
  aide_financiere: 'Aucune', nom: '', prenom: '', telephone: '',
  sexe: '', date_de_naissance: '', adresse: '', lieu_de_naissance: '',
  religion: '', niveau_id: '', classe_actuelle_id: '', annee_academique_id: '',
  faculte_id: '', email: '',
  nom_responsable: '', prenom_responsable: '', email_responsable: '',
  relation_responsable: '', sexe_responsable: '', telephone_responsable: '',
  metier_responsable: '', adresse_responsable: '',bourse: false,handicap: false,
  errors: {},processing:false
});

// ── Méthodes ──────────────────────────────────
function submit1() {
  if (!f.cgv || !f.conf) return
  admRef.value = Math.random().toString(36).substring(2, 8).toUpperCase()
  done.value = true
}
 
const is_university = computed(() => {
  const niveau = niveau_global.value?.find(x => x.id === f?.niveau_id)
  return niveau?.name === 'Universitaire' || niveau?.name === 'Technique' // adapte selon ta structure
})

const SectionCard = defineComponent({
  props: ['title', 'icon'],
  setup(props, { slots }) {
    return () => h('div', { class: 'bg-[#161b22] border border-[#21262d] rounded-xl overflow-hidden' }, [
      h('div', { class: 'flex items-center gap-2 px-4 py-3 bg-[#0d1117] border-b border-[#21262d]' }, [
        h('span', { class: 'text-base' }, props.icon),
        h('span', { class: 'text-[12px] font-semibold text-[#e6edf3] uppercase tracking-wide' }, props.title),
      ]),
      h('div', { class: 'p-4' }, slots.default?.()),
    ])
  }
});

const FormField = defineComponent({
  props: ['label', 'error'],
  setup(props, { slots }) {
    return () => h('div', { class: 'flex flex-col gap-1' }, [
      h('label', { class: 'text-[11px] font-medium text-[#7d8590] uppercase tracking-wide' }, props.label),
      slots.default?.(),
      props.error
        ? h('span', { class: 'text-[11px] text-[#f85149] flex items-center gap-1 mt-0.5' }, [
            h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 16 16', fill: 'currentColor', class: 'w-3 h-3 flex-shrink-0' },
              h('path', { 'fill-rule': 'evenodd', d: 'M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14Zm0-4a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM7.25 6a.75.75 0 0 1 1.5 0v2a.75.75 0 0 1-1.5 0V6Z', 'clip-rule': 'evenodd' })
            ),
            props.error,
          ])
        : null,
    ])
  }
});

const submitEtudiant = async () => {
  f.documentss =docs.value?.map(x=>x.document_image != null) // documents;
  f.errors = {};
  f.processing=true
  console.log(f);
  
  try {
    const r = await axios.post(`/student-register`, f);
 
    if (r.data) {
      success(r.data.success, '#34a853');
      // router.push('/etudiants');
      // if (formEtudiant.value.id) await fetchStudentDetails(formEtudiant.value.id);
      // else router.push('/etudiants');
    }
  } catch (e) {
    console.log(e);
  if (e.response?.data?.detail) {
    error(e.response.data.detail, false);
  }

  if (e.response?.data?.errors) {
    f.errors = e.response.data.errors;
  }
   
    // if (e.response?.data?.detail) showSwalInfo(e.response.data.detail, 'red');
  }finally{
    f.processing=false
  }
};

// const classesFiltrees = ref([]);

// watch(() => f.niveau_id, (newVal) => {
//   classesFiltrees.value = getClassesByNiveau(newVal);
// }, { immediate: true });

function reset() {
  done.value = false
  step.value = 0
  docs.value = DOCS_BASE.map(d => ({ ...d }))
  Object.keys(f).forEach(k => { f[k] = typeof f[k] === 'boolean' ? false : '' })
  f.tCiv  = 'Madame'
  f.annee = '2025 – 2026'
}

const getClassesByNiveau = (niveauId) => {
  if (!niveauId || !classes_global.value) return [];
  return classes_global.value.filter(c => c.niveau_id === niveauId);
};

watch(() => f.niveau_id, (newVal) => {
  getClassesByNiveau(newVal); 
  console.log(is_university.value);
  

});

onMounted(() => { schoolStore.fetchAllDependencies();window.scrollTo(0, 0); initReveal() })
watch(step, () => { window.scrollTo({ top: 340, behavior: 'smooth' }); initReveal() })
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
 
.field-input {
  width: 100%;
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 8px 12px;
  color: #e6edf3;
  font-size: 13px;
  outline: none;
  transition: border-color .15s, box-shadow .15s;
}
.field-input::placeholder { color: #484f58; }
.field-input:focus {
  border-color: #58a6ff;
  box-shadow: 0 0 0 3px rgba(88,166,255,.1);
}
.field-input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(.5); }

.field-select {
  width: 100%;
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 8px 12px;
  color: #e6edf3;
  font-size: 13px;
  outline: none;
  cursor: pointer;
  transition: border-color .15s;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%237d8590'%3E%3Cpath fill-rule='evenodd' d='M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z' clip-rule='evenodd'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 14px;
  padding-right: 32px;
}
.field-select:focus { border-color: #58a6ff; }
.field-select option { background: #161b22; color: #e6edf3; }

/* Tab slide */
.tab-slide-enter-active, .tab-slide-leave-active {
  transition: opacity .2s ease, transform .2s ease;
}
.tab-slide-enter-from { opacity: 0; transform: translateY(8px); }
.tab-slide-leave-to   { opacity: 0; transform: translateY(-6px); }

/* Accordion */
.accordion-enter-active, .accordion-leave-active {
  transition: all .25s ease;
  overflow: hidden;
}
.accordion-enter-from, .accordion-leave-to {
  opacity: 0; max-height: 0; padding-top: 0; padding-bottom: 0;
}
.accordion-enter-to, .accordion-leave-from {
  opacity: 1; max-height: 600px;
}

/* Doc list */
.doc-list-enter-active { transition: all .25s ease; }
.doc-list-leave-active { transition: all .2s ease; position: absolute; }
.doc-list-enter-from   { opacity: 0; transform: translateX(-10px); }
.doc-list-leave-to     { opacity: 0; transform: translateX(10px); }
</style> 
