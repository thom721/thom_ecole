<script setup>
import GuestLayout from "@/Layouts/GuestLayout.vue";
import { Transition, onMounted, ref } from 'vue';

let openAccordionIndex = ref(1);

defineOptions({
    layout: GuestLayout,
});


onMounted(() => {
    // window.addEventListener('DOMContentLoaded', () => {
    const defaultContent = document.getElementById(`content-${openAccordionIndex.value}`);
    const defaultIcon = document.getElementById(`icon-${openAccordionIndex.value}`);

    if (defaultContent && defaultIcon) {
        defaultContent.style.maxHeight = defaultContent.scrollHeight + 'px';
        defaultIcon.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
            <path d="M3.75 7.25a.75.75 0 0 0 0 1.5h8.5a.75.75 0 0 0 0-1.5h-8.5Z" />
          </svg>
        `;
    }
    // });
});



const toggleAccordion = (index) => {
    const content = document.getElementById(`content-${index}`);
    const icon = document.getElementById(`icon-${index}`);

    const minusSVG = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
        <path d="M3.75 7.25a.75.75 0 0 0 0 1.5h8.5a.75.75 0 0 0 0-1.5h-8.5Z" />
      </svg>
    `;

    const plusSVG = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
        <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
      </svg>
    `;

    if (openAccordionIndex.value === index) {
        content.style.maxHeight = '0';
        icon.innerHTML = plusSVG;
        openAccordionIndex.value = null;
        return;
    }

    if (openAccordionIndex.value !== null) {
        const previousContent = document.getElementById(`content-${openAccordionIndex.value}`);
        const previousIcon = document.getElementById(`icon-${openAccordionIndex.value}`);
        if (previousContent) {
            previousContent.style.maxHeight = '0';
            previousIcon.innerHTML = plusSVG;
        }
    }

    content.style.maxHeight = content.scrollHeight + 'px';
    icon.innerHTML = minusSVG;
    openAccordionIndex.value = index;
};



</script>

<template>
    <div class="img">
        <div style="position: relative; z-index: 1;">
            <!-- Ton contenu ici -->
        </div>
    </div>
    <div class="max-w-4xl px-4 mx-auto sm:px-6 lg:px-8 pt-8">
        <div class="flex flex-col md:gap-8 text-slate-600">

            <div>
                📄 Conditions Générales de Service – Infini Software
                <p class="text-slate-600 text-md font-bold mt-2">1. Présentation de l’entreprise </p>
                Infini Software est une entreprise spécialisée dans le développement de solutions logicielles sur
                mesure, l’intégration de systèmes, la mise en place d’applications hybrides (locales ou en ligne), et
                l’accompagnement numérique des organisations.

                Nous proposons des services personnalisés pour les établissements scolaires, entreprises et
                institutions, avec un accent sur la sécurité, la fiabilité, et la synchronisation des données en temps
                réel.

                <p class="text-slate-600 text-md font-bold mt-2">2. Nature des services </p>
                Infini Software propose notamment :

                La conception d’applications web, mobiles ou desktop

                Le déploiement en mode local (client-serveur sur site) ou en ligne (cloud sur demande)

                La synchronisation des données en temps réel

                L’assistance, la maintenance, les mises à jour et le support technique

                Chaque service fait l’objet d’un devis et d’un contrat spécifique précisant les modalités d’exécution,
                les délais, la tarification et les responsabilités respectives.

                <p class="text-slate-600 text-md font-bold mt-2">3. Conditions d’utilisation des logiciels livrés</p>
                Les logiciels ou systèmes livrés par Infini Software sont soumis à une licence d’utilisation définie
                dans le contrat signé avec le client. Sauf accord contraire, les droits de propriété intellectuelle
                restent la propriété d’Infini Software.

                Toute reproduction, revente ou diffusion sans autorisation est interdite.

                <p class="text-slate-600 text-md font-bold mt-2">4. Modalités de paiement </p>
                Sauf indication contraire, les paiements sont exigibles selon les étapes prévues dans le devis ou
                contrat. Des pénalités de retard peuvent s’appliquer conformément à la réglementation en vigueur.

                <p class="text-slate-600 text-md font-bold mt-2">5. Période d’essai</p>
                Infini Software peut proposer, selon les projets, une période d’essai gratuite pour certains
                logiciels développés :

                Jusqu’au 31 août 2025 : période d’essai de deux (2) mois

                À partir du 1er septembre 2025 : période d’essai réduite à un (1) mois

                Cette période permet aux clients de tester les fonctionnalités avant validation définitive ou
                souscription à un contrat de service complet.

                <p class="text-slate-600 text-md font-bold mt-2">6. Confidentialité </p>
                Infini Software s’engage à ne divulguer aucune information confidentielle fournie par le client. Les
                données manipulées restent la propriété exclusive du client, et ne sont utilisées que dans le cadre
                strict des prestations prévues.

                <p class="text-slate-600 text-md font-bold mt-2">7. Responsabilité </p>
                Infini Software s’engage à mettre en œuvre les moyens nécessaires pour assurer la qualité de ses
                services. Toutefois, sa responsabilité ne pourra être engagée en cas de mauvaise utilisation des
                logiciels, d’altération des données due à des causes externes (coupure électrique, mauvaise
                manipulation, etc.), ou d’indisponibilité due à des circonstances indépendantes de sa volonté.

                <p class="text-slate-600 text-md font-bold mt-2">8. Modification des conditions </p>
                Infini Software se réserve le droit de modifier les présentes Conditions Générales. La version en
                vigueur au moment de la signature d’un contrat fait foi.
            </div>


            <!-- <div class="w-full">
                📄 Conditions Générales d’Utilisation (CGU)
                <p class="text-slate-600 text-md font-bold mt-2"> 1. Présentation </p>
                <p class="ms-4 text-justify"> Infini Software est une plateforme numérique développée par <span
                        class="text-slate-700 font-semibold">Infini Software</span>, visant à fournir des solutions
                    logicielles
                    performantes et accessibles aux utilisateurs
                    professionnels ou institutionnels. </p>

                <p class="text-slate-600 text-md font-bold mt-2"> 2. Acceptation des conditions </p>
                <p class="ms-4 text-justify"> En accédant à l’application ou en l’utilisant, vous acceptez
                    pleinement et sans réserve les présentes
                    Conditions Générales d’Utilisation. Si vous n’acceptez pas tout ou partie de ces conditions,
                    vous êtes
                    prié(e) de ne pas utiliser l'application. </p>

                <p class="text-slate-600 text-md font-bold mt-2"> 3. Accès au service </p>
                <p class="ms-4 text-justify"> L’accès à Infini Software peut nécessiter une inscription. Vous
                    vous engagez à fournir des informations
                    exactes, à jour et complètes lors de votre inscription. </p>

                <p class="text-slate-600 text-md font-bold mt-2"> 8. Période d’essai</p>
                <div class="ms-4 text-justify">Infini Software propose une version d’essai gratuite à tous les nouveaux
                    utilisateurs afin de leur permettre de découvrir les fonctionnalités de la plateforme.
                    <p>
                        <span class="ms-2 font-bold p-1">Jusqu’au 31 août 2025</span>, chaque nouvel utilisateur
                        bénéficie
                        d’une période d’essai de deux (2) mois à compter de la date de création de son compte.
                    </p>
                    <p>
                        <span class="ms-2 font-bold p-1">À partir du 1er septembre 2025</span>, la période d’essai est
                        réduite à un
                        (1) mois.
                    </p>

                    Pendant la période d’essai, l’utilisateur dispose d’un accès complet ou partiel aux fonctionnalités
                    de l'application, sauf indication contraire. À l’expiration de la période d’essai, l’utilisateur
                    devra souscrire à un abonnement pour continuer à utiliser le service sans interruption.

                    Infini Software se réserve le droit de modifier les modalités de l’essai gratuit à tout moment, avec
                    ou sans préavis, sans effet rétroactif sur les périodes déjà entamées.
                </div>

                <p class="text-slate-600 text-md font-bold mt-2"> 4. Utilisation responsable </p>
                <p class="ms-4 text-justify"> Vous vous engagez à utiliser Infini Software dans le respect
                    de la loi, de l’ordre public et des bonnes
                    mœurs. Toute tentative d’intrusion, d’usage frauduleux ou de détournement du service
                    entraînera la
                    suspension immédiate de votre compte. </p>

                <p class="text-slate-600 text-md font-bold mt-2"> 5. Propriété intellectuelle </p>
                <p class="ms-4 text-justify"> Tous les contenus, marques, logos, textes, images,
                    éléments graphiques et codes sources présents sur
                    Infini Software sont protégés par le droit de la propriété intellectuelle. Toute
                    reproduction,
                    représentation ou exploitation est strictement interdite sans autorisation
                    préalable. </p>

                <p class="text-slate-600 text-md font-bold mt-2"> 6. Responsabilité </p>
                <p class="ms-4 text-justify"> Infini Software met tout en œuvre pour assurer la
                    disponibilité, la sécurité et la fiabilité de ses
                    services. Toutefois, nous ne pourrons être tenus responsables des interruptions
                    de service ou de tout
                    dommage indirect lié à l’utilisation de la plateforme. </p>

                <p class="text-slate-600 text-md font-bold mt-2"> 7. Modification des conditions
                </p>
                <p class="ms-4 text-justify"> Infini Software se réserve le droit de modifier
                    les présentes conditions à tout moment. Les utilisateurs
                    seront informés par email ou notification. L'utilisation continue de la
                    plateforme vaut acceptation des
                    nouvelles conditions. </p>


            </div> -->
        </div>
    </div>

</template>