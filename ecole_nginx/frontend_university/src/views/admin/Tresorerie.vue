<template>
  <div class="animate-[fadeUp_0.4s_ease_both]">

    <!-- Tabs -->
    <div class="flex border-b border-white/[0.07] mb-6">
      <button v-for="t in tabs" :key="t.key" @click="activeSub = t.key"
        :class="['px-4 py-2.5 text-[13.5px] font-medium border-b-2 -mb-px transition-colors',
          activeSub === t.key ? 'border-[var(--accent)] text-[var(--accent)]' : 'border-transparent text-[#7c83a0] hover:text-[#e8eaf0]']">
        {{ t.label }}
      </button>
    </div>

    <!-- ══ VENTES ══════════════════════════════════════════════════ -->
    <div v-if="activeSub === 'vente'">
      <!-- Stats cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
        <div v-for="c in ventesCards" :key="c.label" class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
          <p class="text-xs text-[#7c83a0] mb-2">{{ c.label }}</p>
          <p :class="['text-[22px] font-semibold font-mono tracking-tight leading-none', c.color]">
            {{ c.value }} <span class="text-base font-sans font-normal text-[#7c83a0]">{{ c.unit }}</span>
          </p>
          <p v-if="c.sub" class="text-xs mt-2" :class="c.subColor ?? 'text-[#7c83a0]'">{{ c.sub }}</p>
        </div>
      </div>

      <!-- Table + recherche -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-white/[0.07] flex items-center justify-between gap-3">
          <span class="text-[13.5px] font-medium text-[#e8eaf0]">
            Transactions · <span class="text-[#7c83a0] font-mono text-xs">{{ ventesMeta.total ?? 0 }}</span>
          </span>
          <input v-model="venteSearch" @input="debounceVente" type="text" placeholder="Rechercher…"
            class="text-[12px] bg-[#0d1117] border border-white/[0.08] rounded-lg px-3 py-1.5 text-[#c9d1d9] focus:outline-none focus:border-[var(--accent)]/40 w-48"/>
        </div>

        <!-- Skeleton -->
        <div v-if="venteLoading" class="animate-pulse px-5 py-4 space-y-3">
          <div v-for="i in 6" :key="i" class="h-8 bg-white/[0.04] rounded"></div>
        </div>

        <table v-else class="w-full">
          <thead>
            <tr class="bg-[#13161f]">
              <th v-for="h in ['###','Élève','Montant','Date','Action']" :key="h"
                  class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="ventes.length === 0"><td colspan="5" class="px-4 py-8 text-center text-[#7c83a0] text-sm">Aucune vente trouvée</td></tr>
            <tr v-for="t in ventes" :key="t.id" class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors">
              <td class="px-4 py-3 text-[13px] font-mono text-[#7c83a0]">{{ t.order_itemId }}</td>
              <td class="px-4 py-3 text-[13.5px] font-medium text-[#e8eaf0]">{{ t.nom }}</td>
              <td class="px-4 py-3 font-mono text-[13.5px]" :class="t.total > 0 ? 'text-emerald-400' : 'text-[#e8eaf0]'">
                {{ Number(t.total).toLocaleString('fr-FR') }} HTG
              </td>
              <td class="px-4 py-3 font-mono text-xs text-[#7c83a0]">{{ t.date }}</td>
              <td class="px-4 py-3">
                <button class="inline-flex items-center gap-1.5 px-3 py-1 bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded-md text-[11px] font-medium hover:bg-sky-500/20 transition-colors">Reçu</button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div v-if="ventesMeta.last_page > 1" class="px-5 py-3 border-t border-white/[0.05] flex items-center justify-between">
          <span class="text-xs text-[#7c83a0]">Page {{ ventesMeta.current_page }} / {{ ventesMeta.last_page }}</span>
          <div class="flex items-center gap-1">
            <button @click="ventePage = ventePage - 1; fetchVentes()" :disabled="ventePage <= 1"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">‹</button>
            <template v-for="p in paginationPages(ventesMeta)" :key="p">
              <button v-if="p !== '...'" @click="ventePage = p; fetchVentes()"
                :class="['px-2.5 py-1 rounded text-xs transition',
                  p === ventesMeta.current_page ? 'bg-[var(--accent)]/20 text-[var(--accent)]' : 'text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06]']">{{ p }}</button>
              <span v-else class="px-1 text-[#7c83a0] text-xs">…</span>
            </template>
            <button @click="ventePage = ventePage + 1; fetchVentes()" :disabled="ventePage >= ventesMeta.last_page"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">›</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ PRODUITS ════════════════════════════════════════════════ -->
    <div v-if="activeSub === 'produit'">
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-white/[0.07] flex items-center justify-between gap-3">
          <span class="text-[13.5px] font-medium text-[#e8eaf0]">
            Produits · <span class="text-[#7c83a0] font-mono text-xs">{{ produitMeta.total ?? 0 }}</span>
          </span>
          <div class="flex items-center gap-3">
            <input v-model="produitSearch" @input="debounceProduit" type="text" placeholder="Rechercher…"
              class="text-[12px] bg-[#0d1117] border border-white/[0.08] rounded-lg px-3 py-1.5 text-[#c9d1d9] focus:outline-none focus:border-[var(--accent)]/40 w-48"/>
            <button type="button" @click="produitModalShow" class="btn-amber">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/>
              </svg>
              Ajouter produit
            </button>
          </div>
        </div>

        <div v-if="produitLoading" class="animate-pulse px-5 py-4 space-y-3">
          <div v-for="i in 6" :key="i" class="h-8 bg-white/[0.04] rounded"></div>
        </div>

        <table v-else class="w-full">
          <thead>
            <tr class="bg-[#13161f]">
              <th v-for="h in ['Nom','Catégorie','Prix','Stock','Description','']" :key="h"
                  class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="produits.length === 0"><td colspan="6" class="px-4 py-8 text-center text-[#7c83a0] text-sm">Aucun produit trouvé</td></tr>
            <tr v-for="p in produits" :key="p.id" class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors">
              <td class="px-4 py-3 text-[13.5px] font-medium text-[#e8eaf0]">{{ p.nom }}</td>
              <td class="px-4 py-3 text-[12px] text-[#7c83a0]">{{ p.category }}</td>
              <td class="px-4 py-3 font-mono text-[13.5px] text-[#e8eaf0]">{{ Number(p.prix).toLocaleString('fr-FR') }} HTG</td>
              <td class="px-4 py-3 font-mono text-xs text-[#7c83a0]">{{ p.quantite_stock }}</td>
              <td class="px-4 py-3 text-[12px] text-[#7c83a0]">{{ p.description ?? '—' }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2 justify-end">
                  <button type="button" @click="produitModalEdit(p)" class="text-[#7c83a0] hover:text-[var(--accent)] transition-colors" title="Modifier">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897z"/>
                    </svg>
                  </button>
                  <button type="button" @click="deleteProduit(p)" class="text-[#7c83a0] hover:text-red-400 transition-colors" title="Supprimer">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9M19.228 5.79A48.11 48.11 0 0 0 12 5.25c-2.427 0-4.822.166-7.228.44m14.456 0c.34.038.678.078 1.016.122a1 1 0 0 1 .95 1.01l-.44 14.418a2 2 0 0 1-2 1.93H7.226a2 2 0 0 1-1.998-1.93L4.79 7.362a1 1 0 0 1 .95-1.01c.338-.044.676-.084 1.016-.122m9.968 0a48 48 0 0 0-9.968 0M8.25 5.72V4.5a2.25 2.25 0 0 1 2.25-2.25h2.25a2.25 2.25 0 0 1 2.25 2.25v1.22"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="produitMeta.last_page > 1" class="px-5 py-3 border-t border-white/[0.05] flex items-center justify-between">
          <span class="text-xs text-[#7c83a0]">Page {{ produitMeta.current_page }} / {{ produitMeta.last_page }}</span>
          <div class="flex items-center gap-1">
            <button @click="produitPage--; fetchProduits()" :disabled="produitPage <= 1"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">‹</button>
            <template v-for="p in paginationPages(produitMeta)" :key="p">
              <button v-if="p !== '...'" @click="produitPage = p; fetchProduits()"
                :class="['px-2.5 py-1 rounded text-xs transition',
                  p === produitMeta.current_page ? 'bg-[var(--accent)]/20 text-[var(--accent)]' : 'text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06]']">{{ p }}</button>
              <span v-else class="px-1 text-[#7c83a0] text-xs">…</span>
            </template>
            <button @click="produitPage++; fetchProduits()" :disabled="produitPage >= produitMeta.last_page"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">›</button>
          </div>
        </div>
      </div>

      <StyleModal :show="openProduitModal" :max-width="'xl'" @close="produitModalClose">
        <template #title>
          <h5 class="modal-title text-center text-slate-300">
            {{ produitChangeButton ? 'Modifier le produit' : 'Ajouter un produit' }}
          </h5>
        </template>
        <template #content>
          <form @submit.prevent="submitProduit">
            <div class="modal-body">
              <div class="pb-2 w-full">
                <InputLabel for="produit_nom" value="Nom" />
                <TextInput id="produit_nom" v-model="formProduit.nom" type="text" class="py-0" autofocus />
                <InputError class="mt-2" :message="formProduit.errors.nom" />
              </div>

              <div class="pb-2 w-full">
                <InputLabel for="produit_category" value="Catégorie" />
                <div class="flex items-center gap-2">
                  <select id="produit_category" class="input-select" v-model="formProduit.category">
                    <option disabled value="">Catégorie</option>
                    <option v-for="c in categories" :key="c.id" :value="c.nom">{{ c.nom }}</option>
                  </select>
                  <button type="button" @click="showNewCategory = !showNewCategory"
                    class="shrink-0 text-[#7c83a0] hover:text-[var(--accent)] transition-colors" title="Nouvelle catégorie">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="w-5 h-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/>
                    </svg>
                  </button>
                </div>
                <InputError class="mt-2" :message="formProduit.errors.category" />
                <div v-if="showNewCategory" class="flex items-center gap-2 mt-2">
                  <TextInput v-model="newCategoryName" type="text" class="py-0" placeholder="Nom de la nouvelle catégorie" />
                  <PrimaryButton type="button" @click="submitNewCategory" :disabled="creatingCategory">Ajouter</PrimaryButton>
                </div>
                <p v-if="categoryError" class="text-xs text-red-400 mt-1">{{ categoryError }}</p>
              </div>

              <div class="flex flex-col md:flex-row justify-between items-center gap-2">
                <div class="pb-2 w-full">
                  <InputLabel for="produit_prix" value="Prix" />
                  <TextInput id="produit_prix" v-model="formProduit.prix" type="number" step="0.01" class="py-0" />
                  <InputError class="mt-2" :message="formProduit.errors.prix" />
                </div>
                <div class="pb-2 w-full">
                  <InputLabel for="produit_stock" value="Quantité en stock" />
                  <TextInput id="produit_stock" v-model="formProduit.quantite_stock" type="number" step="1" class="py-0" />
                  <InputError class="mt-2" :message="formProduit.errors.quantite_stock" />
                </div>
              </div>

              <div class="pb-2">
                <InputLabel for="produit_description" value="Description" />
                <TextInput id="produit_description" v-model="formProduit.description" type="text" class="py-0" />
                <InputError class="mt-2" :message="formProduit.errors.description" />
              </div>
            </div>
            <div class="flex justify-end gap-4 py-1">
              <DangerButton type="button" @click="produitModalClose">Close</DangerButton>
              <PrimaryButton type="submit" :class="{ 'opacity-25': formProduit.processing }" :disabled="formProduit.processing">
                <span v-if="produitChangeButton">Modifier</span>
                <span v-else>Enregistrer</span>
              </PrimaryButton>
            </div>
          </form>
        </template>
      </StyleModal>
    </div>

    <!-- ══ DÉPENSES ════════════════════════════════════════════════ -->
    <div v-if="activeSub === 'depense'">
      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
        <div v-for="c in depenseCards" :key="c.label" class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
          <p class="text-xs text-[#7c83a0] mb-2">{{ c.label }}</p>
          <p :class="['text-[22px] font-semibold font-mono tracking-tight leading-none', c.color]">
            {{ c.value }} <span class="text-base font-sans font-normal text-[#7c83a0]">HTG</span>
          </p>
        </div>
      </div>

      <!-- Table dépenses -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-white/[0.07] flex items-center justify-between gap-3">
          <span class="text-[13.5px] font-medium text-[#e8eaf0]">
            Dépenses · <span class="text-[#7c83a0] font-mono text-xs">{{ depenseMeta.total ?? 0 }}</span>
          </span>
          <input v-model="depenseSearch" @input="debounceDepense" type="text" placeholder="Rechercher…"
            class="text-[12px] bg-[#0d1117] border border-white/[0.08] rounded-lg px-3 py-1.5 text-[#c9d1d9] focus:outline-none focus:border-[var(--accent)]/40 w-48"/>
        </div>

        <div v-if="depenseLoading" class="animate-pulse px-5 py-4 space-y-3">
          <div v-for="i in 6" :key="i" class="h-8 bg-white/[0.04] rounded"></div>
        </div>

        <table v-else class="w-full">
          <thead>
            <tr class="bg-[#13161f]">
              <th v-for="h in ['Description','Montant dépensé','Date','Enregistré par']" :key="h"
                  class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="depenses.length === 0"><td colspan="4" class="px-4 py-8 text-center text-[#7c83a0] text-sm">Aucune dépense trouvée</td></tr>
            <tr v-for="d in depenses" :key="d.id" class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors">
              <td class="px-4 py-3 text-[13.5px] text-[#e8eaf0]">{{ d.description }}</td>
              <td class="px-4 py-3 font-mono text-[13.5px] text-red-400 font-semibold">
                − {{ Number(d.prix).toLocaleString('fr-FR') }} HTG
              </td>
              <td class="px-4 py-3 font-mono text-xs text-[#7c83a0]">{{ d.date }}</td>
              <td class="px-4 py-3 text-[12px] text-[#7c83a0]">{{ d.user_name ?? '—' }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="depenseMeta.last_page > 1" class="px-5 py-3 border-t border-white/[0.05] flex items-center justify-between">
          <span class="text-xs text-[#7c83a0]">Page {{ depenseMeta.current_page }} / {{ depenseMeta.last_page }}</span>
          <div class="flex items-center gap-1">
            <button @click="depensePage--; fetchDepenses()" :disabled="depensePage <= 1"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">‹</button>
            <template v-for="p in paginationPages(depenseMeta)" :key="p">
              <button v-if="p !== '...'" @click="depensePage = p; fetchDepenses()"
                :class="['px-2.5 py-1 rounded text-xs transition',
                  p === depenseMeta.current_page ? 'bg-[var(--accent)]/20 text-[var(--accent)]' : 'text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06]']">{{ p }}</button>
              <span v-else class="px-1 text-[#7c83a0] text-xs">…</span>
            </template>
            <button @click="depensePage++; fetchDepenses()" :disabled="depensePage >= depenseMeta.last_page"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">›</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ PRÊTS ════════════════════════════════════════════════════ -->
    <div v-if="activeSub === 'pret'">
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-white/[0.07] flex items-center justify-between">
          <span class="text-[13.5px] font-medium text-[#e8eaf0]">Prêts en cours</span>
        </div>
        <table class="w-full">
          <thead>
            <tr class="bg-[#13161f]">
              <th v-for="h in ['Bénéficiaire','Montant','Remboursé','Échéance','Statut']" :key="h"
                  class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!prets.length"><td colspan="5" class="px-4 py-8 text-center text-[#7c83a0] text-sm">Aucun prêt</td></tr>
            <tr v-for="p in prets" :key="p.id" class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors">
              <td class="px-4 py-3 text-[13.5px] font-medium text-[#e8eaf0]">{{ p.user }}</td>
              <td class="px-4 py-3 font-mono text-[13.5px] text-[#e8eaf0]">{{ p.amount }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2.5">
                  <div class="w-20 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                    <div class="h-full rounded-full" :style="{ width: pourcentagePaye(p.amount, p.remaining_balance) + '%', background: 'var(--accent)' }"></div>
                  </div>
                  <span class="font-mono text-xs text-[#7c83a0]">{{ p.pct }}%</span>
                </div>
              </td>
              <td class="px-4 py-3 font-mono text-xs text-[#7c83a0]">{{ p.term_months }} Mois</td>
              <td class="px-4 py-3">
                <span :class="['inline-flex items-center px-2 py-0.5 rounded-full text-[11.5px] font-medium',
                  p.statut === 'Pending' ? 'bg-[var(--accent)]/15 text-[var(--accent)]' : 'bg-emerald-500/15 text-emerald-400']">
                  {{ p.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ══ AUTRES TRANSACTIONS ══════════════════════════════════════ -->
    <div v-if="activeSub === 'autre'">
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-white/[0.07] flex items-center justify-between gap-3">
          <span class="text-[13.5px] font-medium text-[#e8eaf0]">
            Autres transactions · <span class="text-[#7c83a0] font-mono text-xs">{{ autreMeta.total ?? 0 }}</span>
          </span>
          <input v-model="autreSearch" @input="debounceAutre" type="text" placeholder="Rechercher…"
            class="text-[12px] bg-[#0d1117] border border-white/[0.08] rounded-lg px-3 py-1.5 text-[#c9d1d9] focus:outline-none focus:border-[var(--accent)]/40 w-48"/>
        </div>

        <div v-if="autreLoading" class="animate-pulse px-5 py-4 space-y-3">
          <div v-for="i in 6" :key="i" class="h-10 bg-white/[0.04] rounded"></div>
        </div>

        <table v-else class="w-full">
          <thead>
            <tr class="bg-[#13161f]">
              <th v-for="h in ['Description','Élève','Montant','Date','Enregistré par']" :key="h"
                  class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="autresTx.length === 0"><td colspan="5" class="px-4 py-8 text-center text-[#7c83a0] text-sm">Aucune transaction</td></tr>
            <tr v-for="a in autresTx" :key="a.id" class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors">
              <td class="px-4 py-3 text-[13.5px] text-[#e8eaf0]">
                {{ a.description }}
                <span v-if="a.description_supplementaire" class="ml-1 text-xs text-[#7c83a0]">({{ a.description_supplementaire }})</span>
              </td>
              <td class="px-4 py-3 text-[12px] text-[#7c83a0]">
                {{ a.etudiant ? `${a.etudiant.nom ?? ''} ${a.etudiant.prenom ?? ''}`.trim() : '—' }}
              </td>
              <td class="px-4 py-3 font-mono text-[13.5px] text-amber-400 font-semibold">
                {{ Number(a.montant).toLocaleString('fr-FR') }} HTG
              </td>
              <td class="px-4 py-3 font-mono text-xs text-[#7c83a0]">{{ a.date }}</td>
              <td class="px-4 py-3 text-[12px] text-[#7c83a0]">{{ a.utilisateur ?? '—' }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="autreMeta.last_page > 1" class="px-5 py-3 border-t border-white/[0.05] flex items-center justify-between">
          <span class="text-xs text-[#7c83a0]">Page {{ autreMeta.current_page }} / {{ autreMeta.last_page }}</span>
          <div class="flex items-center gap-1">
            <button @click="autrePage--; fetchAutres()" :disabled="autrePage <= 1"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">‹</button>
            <template v-for="p in paginationPages(autreMeta)" :key="p">
              <button v-if="p !== '...'" @click="autrePage = p; fetchAutres()"
                :class="['px-2.5 py-1 rounded text-xs transition',
                  p === autreMeta.current_page ? 'bg-[var(--accent)]/20 text-[var(--accent)]' : 'text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06]']">{{ p }}</button>
              <span v-else class="px-1 text-[#7c83a0] text-xs">…</span>
            </template>
            <button @click="autrePage++; fetchAutres()" :disabled="autrePage >= autreMeta.last_page"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">›</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import axios from 'axios'
import { onMounted, ref, reactive, watch, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import InputError from "@/components/InputError.vue";
import InputLabel from "@/components/InputLabel.vue";
import TextInput from "@/components/TextInput.vue";
import PrimaryButton from "@/components/PrimaryButton.vue";
import StyleModal from "@/components/StyleModal.vue";
import DangerButton from "@/components/DangerButton.vue";

const url = import.meta.env.VITE_APP_BASE_URL
const authStore = useAuthStore()

const ALL_TABS = [
  { key: 'vente',   subId: 'vente.vente',        label: 'Ventes' },
  { key: 'produit', subId: 'vente.produits',      label: 'Produits' },
  { key: 'depense', subId: 'vente.depenses',      label: 'Dépenses' },
  { key: 'pret',    subId: 'vente.prets',         label: 'Prêts' },
  { key: 'autre',   subId: 'vente.transactions',  label: 'Autres transactions' },
]

const tabs = computed(() => {
  const tabIds = authStore.user?.tab_ids ?? null
  if (tabIds === null) return ALL_TABS
  return ALL_TABS.filter(t => tabIds.includes(t.subId))
})

const activeSub = ref('vente')
watch(tabs, (vt) => {
  if (vt.length && !vt.find(t => t.key === activeSub.value)) {
    activeSub.value = vt[0]?.key ?? 'vente'
  }
}, { immediate: true })

// ── Ventes ────────────────────────────────────────────────────────────────
const ventesCards  = ref([])
const ventes       = ref([])
const ventesMeta   = ref({ current_page:1, last_page:1, total:0 })
const ventePage    = ref(1)
const venteSearch  = ref('')
const venteLoading = ref(false)
let venteTimer = null

const fetchVentes = async () => {
  venteLoading.value = true
  try {
    const { data } = await axios.get(`${url}/vente`, {
      params: { page: ventePage.value, per_page: 20, search: venteSearch.value || undefined }
    })
    ventes.value   = data.data
    ventesMeta.value = data.meta
  } catch (e) { console.error('[Ventes]', e) }
  finally { venteLoading.value = false }
}

const debounceVente = () => {
  clearTimeout(venteTimer)
  venteTimer = setTimeout(() => { ventePage.value = 1; fetchVentes() }, 350)
}

// ── Stats ventes ──────────────────────────────────────────────────────────
const fetchVenteStats = async () => {
  try {
    const { data } = await axios.get(`${url}/stats-ventes`)
    ventesCards.value = data.ventesCards ?? []
  } catch (e) { console.error('[VenteStats]', e) }
}

// ── Produits ──────────────────────────────────────────────────────────────
// Équivalent de ProduitState (flutter_version/lib/state/produit_state.dart) :
// CRUD sur GET/POST/PUT/DELETE v1/produits — jamais implémenté côté web
// jusqu'ici malgré l'entrée "vente.produits" déjà présente dans les vues
// configurables (adProfile.vue).
const produits       = ref([])
const produitMeta    = ref({ current_page:1, last_page:1, total:0 })
const produitPage    = ref(1)
const produitSearch  = ref('')
const produitLoading = ref(false)
let produitTimer = null

const categories = ref([])
const showNewCategory = ref(false)
const newCategoryName = ref('')
const creatingCategory = ref(false)
const categoryError = ref('')

const openProduitModal = ref(false)
const produitChangeButton = ref(false)
const formProduit = reactive({
  id: '', nom: '', category: '', prix: '', quantite_stock: 0, description: '',
  processing: false, errors: {},
})

const fetchProduits = async () => {
  produitLoading.value = true
  try {
    const { data } = await axios.get(`${url}/produits`, {
      params: { page: produitPage.value, per_page: 20, search: produitSearch.value || undefined }
    })
    produits.value    = data.data
    produitMeta.value = data.meta
  } catch (e) { console.error('[Produits]', e) }
  finally { produitLoading.value = false }
}

const debounceProduit = () => {
  clearTimeout(produitTimer)
  produitTimer = setTimeout(() => { produitPage.value = 1; fetchProduits() }, 350)
}

const fetchCategories = async () => {
  try {
    const { data } = await axios.get(`${url}/categories-produits`)
    categories.value = data
  } catch (e) { console.error('[CategoriesProduits]', e) }
}

const submitNewCategory = async () => {
  const nom = newCategoryName.value.trim()
  if (!nom) return
  creatingCategory.value = true
  categoryError.value = ''
  try {
    await axios.post(`${url}/categories-produits`, { nom })
    await fetchCategories()
    formProduit.category = nom
    newCategoryName.value = ''
    showNewCategory.value = false
  } catch (e) {
    categoryError.value = e.response?.data?.detail ?? 'Impossible de créer cette catégorie.'
  } finally {
    creatingCategory.value = false
  }
}

const resetFormProduit = () => {
  Object.assign(formProduit, {
    id: '', nom: '', category: '', prix: '', quantite_stock: 0, description: '',
    processing: false, errors: {},
  })
}

const produitModalShow = () => {
  resetFormProduit()
  produitChangeButton.value = false
  openProduitModal.value = true
}

const produitModalEdit = (p) => {
  Object.assign(formProduit, {
    id: p.id, nom: p.nom, category: p.category, prix: p.prix,
    quantite_stock: p.quantite_stock, description: p.description ?? '',
    processing: false, errors: {},
  })
  produitChangeButton.value = true
  openProduitModal.value = true
}

const produitModalClose = () => {
  resetFormProduit()
  showNewCategory.value = false
  newCategoryName.value = ''
  categoryError.value = ''
  openProduitModal.value = false
}

const submitProduit = async () => {
  formProduit.processing = true
  formProduit.errors = {}
  const payload = {
    nom: formProduit.nom,
    category: formProduit.category,
    prix: Number(formProduit.prix),
    quantite_stock: Number(formProduit.quantite_stock),
    description: formProduit.description || null,
  }
  try {
    if (produitChangeButton.value) {
      await axios.put(`${url}/produits/${formProduit.id}`, payload)
    } else {
      await axios.post(`${url}/produits`, payload)
    }
    produitModalClose()
    fetchProduits()
  } catch (error) {
    if (error.response?.status === 422) {
      formProduit.errors = error.response.data.errors ?? {}
    } else {
      console.error('[Produit submit]', error)
    }
  } finally {
    formProduit.processing = false
  }
}

const deleteProduit = async (p) => {
  if (!confirm(`Supprimer le produit "${p.nom}" ?`)) return
  try {
    await axios.delete(`${url}/produits/${p.id}`)
    fetchProduits()
  } catch (e) { console.error('[Produit delete]', e) }
}

// ── Dépenses ──────────────────────────────────────────────────────────────
const depenseCards  = ref([])
const depenses      = ref([])
const depenseMeta   = ref({ current_page:1, last_page:1, total:0 })
const depensePage   = ref(1)
const depenseSearch = ref('')
const depenseLoading= ref(false)
let depenseTimer = null

const fetchDepenses = async () => {
  depenseLoading.value = true
  try {
    const { data } = await axios.get(`${url}/depense`, {
      params: { page: depensePage.value, per_page: 20, search: depenseSearch.value || undefined }
    })
    depenses.value    = data.data
    depenseMeta.value = data.meta
  } catch (e) { console.error('[Depenses]', e) }
  finally { depenseLoading.value = false }
}

const debounceDepense = () => {
  clearTimeout(depenseTimer)
  depenseTimer = setTimeout(() => { depensePage.value = 1; fetchDepenses() }, 350)
}

const fetchDepenseStats = async () => {
  try {
    const { data } = await axios.get(`${url}/stats-depenses`)
    depenseCards.value = data.depenseCards ?? []
  } catch (e) { console.error('[DepenseStats]', e) }
}

// ── Prêts ─────────────────────────────────────────────────────────────────
const prets = ref([])
const fetchPrets = async () => {
  try {
    const { data } = await axios.get(`${url}/get-loans`)
    prets.value = data?.data ?? []
  } catch (e) { console.error('[Prets]', e) }
}

// ── Autres transactions ───────────────────────────────────────────────────
const autresTx    = ref([])
const autreMeta   = ref({ current_page:1, last_page:1, total:0 })
const autrePage   = ref(1)
const autreSearch = ref('')
const autreLoading= ref(false)
let autreTimer = null

const fetchAutres = async () => {
  autreLoading.value = true
  try {
    const { data } = await axios.get(`${url}/other-transactions`, {
      params: { page: autrePage.value, per_page: 20 }
    })
    autresTx.value  = data.data ?? []
    autreMeta.value = {
      current_page: data.current_page ?? 1,
      last_page:    data.last_page    ?? 1,
      total:        data.total        ?? 0,
    }
  } catch (e) { console.error('[Autres]', e) }
  finally { autreLoading.value = false }
}

const debounceAutre = () => {
  clearTimeout(autreTimer)
  autreTimer = setTimeout(() => { autrePage.value = 1; fetchAutres() }, 350)
}

// ── Pagination helper ─────────────────────────────────────────────────────
const paginationPages = (meta) => {
  const cur = meta.current_page, last = meta.last_page
  if (last <= 7) return Array.from({ length: last }, (_, i) => i + 1)
  const pages = [1]
  if (cur > 3) pages.push('...')
  for (let p = Math.max(2, cur - 1); p <= Math.min(last - 1, cur + 1); p++) pages.push(p)
  if (cur < last - 2) pages.push('...')
  pages.push(last)
  return pages
}

// ── Navigation ────────────────────────────────────────────────────────────
watch(activeSub, (val) => {
  if (val === 'vente')   { fetchVenteStats(); fetchVentes() }
  if (val === 'produit') { fetchCategories(); fetchProduits() }
  if (val === 'depense') { fetchDepenseStats(); fetchDepenses() }
  if (val === 'pret')    { fetchPrets() }
  if (val === 'autre')   { fetchAutres() }
})

const pourcentagePaye = (amount, remaining) => {
  const total = amount + remaining
  return total > 0 ? Math.round((amount / total) * 100) : 0
}

onMounted(() => {
  fetchVenteStats()
  fetchVentes()
})
</script>

<style scoped>
@keyframes fadeUp {
  from { opacity:0; transform:translateY(8px) }
  to   { opacity:1; transform:translateY(0)   }
}
</style>
