<template>
  <div>
    <div class="relative overflow-hidden" style="height:32vh;min-height:220px;background:#0B1F3A">
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <p class="text-xs font-bold mb-3" style="color:#fde68a;letter-spacing:.3em;text-transform:uppercase">Informations légales</p>
        <h1 class="font-serif text-white" style="font-size:clamp(1.8rem,4vw,2.6rem)">Mentions légales</h1>
      </div>
    </div>

    <section class="py-16" style="background:#EFECE5">
      <div class="max-w-2xl mx-auto px-6">
        <nav class="flex flex-wrap gap-x-6 gap-y-2 mb-14 text-sm font-semibold" style="color:#1A7A6E">
          <a href="#mentions" class="no-underline">Mentions légales</a>
          <a href="#confidentialite" class="no-underline">Confidentialité</a>
          <a href="#cookies" class="no-underline">Cookies</a>
        </nav>

        <section id="mentions" class="mb-16 reveal" style="scroll-margin-top:100px">
          <h2 class="font-serif text-2xl mb-6" style="color:#0B1F3A">Mentions légales</h2>

          <h3 class="font-serif text-base mb-2 mt-6" style="color:#0B1F3A">Éditeur du site</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            Institut Universitaire des Sciences et des Technologies d'Haïti (IUSTH), institution privée
            d'enseignement supérieur et de recherche à but non lucratif, reconnue d'utilité publique par
            l'État haïtien.<br>
            Adresse : #5, Impasse Cantave, Delmas 75, Haïti.<br>
            Email : <a href="mailto:contact@iusth.edu.ht" style="color:#1A7A6E">contact@iusth.edu.ht</a><br>
            Téléphone : +509 3755-9811 / +509 3247-1571
          </p>

          <h3 class="font-serif text-base mb-2 mt-6" style="color:#0B1F3A">Direction de la publication</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            La direction de la publication est assurée par le Conseil d'Administration de l'IUSTH.
          </p>

          <h3 class="font-serif text-base mb-2 mt-6" style="color:#0B1F3A">Hébergement et développement</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            Le site et la plateforme de gestion associée sont développés et opérés par Infini Software
            (plateforme Lekol360), sur un serveur dédié.
          </p>

          <h3 class="font-serif text-base mb-2 mt-6" style="color:#0B1F3A">Propriété intellectuelle</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            L'ensemble des contenus présents sur ce site (textes, images, logo, mise en page) est la
            propriété de l'IUSTH, sauf mention contraire. Toute reproduction sans autorisation préalable
            est interdite.
          </p>
        </section>

        <section id="confidentialite" class="mb-16 reveal" style="scroll-margin-top:100px">
          <h2 class="font-serif text-2xl mb-6" style="color:#0B1F3A">Politique de confidentialité</h2>

          <h3 class="font-serif text-base mb-2 mt-6" style="color:#0B1F3A">Données collectées</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            Ce site collecte des données personnelles uniquement lorsque vous les transmettez
            volontairement, via&nbsp;:
          </p>
          <ul class="list-disc pl-5 text-gray-500 text-sm leading-relaxed space-y-1 mt-2">
            <li>le formulaire de demande d'admission (identité, coordonnées, parcours scolaire, pièces justificatives) ;</li>
            <li>le formulaire de contact (nom, email, téléphone, objet et contenu du message).</li>
          </ul>

          <h3 class="font-serif text-base mb-2 mt-6" style="color:#0B1F3A">Utilisation des données</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            Ces informations sont utilisées exclusivement pour traiter votre demande (dossier d'admission
            ou réponse à votre message) et ne sont ni vendues, ni transmises à des tiers à des fins
            commerciales.
          </p>

          <h3 class="font-serif text-base mb-2 mt-6" style="color:#0B1F3A">Conservation</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            Les données des dossiers d'admission acceptés sont conservées pour la durée du parcours
            académique de l'étudiant. Les messages de contact sont conservés le temps nécessaire pour y
            répondre.
          </p>

          <h3 class="font-serif text-base mb-2 mt-6" style="color:#0B1F3A">Vos droits</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            Vous pouvez demander l'accès, la correction ou la suppression de vos données personnelles en
            écrivant à <a href="mailto:contact@iusth.edu.ht" style="color:#1A7A6E">contact@iusth.edu.ht</a>.
          </p>
        </section>

        <section id="cookies" class="reveal" style="scroll-margin-top:100px">
          <h2 class="font-serif text-2xl mb-6" style="color:#0B1F3A">Politique de cookies</h2>
          <p class="text-gray-500 text-sm leading-relaxed">
            Ce site n'utilise pas de cookies publicitaires ou de traceurs tiers. Il n'y a pas de suivi
            statistique ni de partage de données de navigation avec des services externes.
          </p>
          <p class="text-gray-500 text-sm leading-relaxed mt-4">
            Le seul stockage effectué par le site est technique&nbsp;: lorsque vous vous connectez à
            votre espace (administration, enseignant, étudiant), un identifiant de session est conservé
            dans le stockage local de votre navigateur afin de vous garder connecté·e. Cette donnée reste
            sur votre appareil et est supprimée à la déconnexion.
          </p>
        </section>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { initReveal } from '@/composables/useReveal.js'

const route = useRoute()

onMounted(() => {
  if (route.hash) {
    const el = document.querySelector(route.hash)
    if (el) { el.scrollIntoView({ behavior: 'smooth' }); initReveal(); return }
  }
  window.scrollTo(0, 0)
  initReveal()
})
</script>
