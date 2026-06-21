<script setup>
import GuestLayout from "@/Layouts/GuestLayout.vue";
import { Transition, onMounted, ref } from 'vue';

let openAccordionIndex = ref(1);

defineOptions({
    layout: GuestLayout,
});





</script>

<template>
    <div class="img">
        <div style="position: relative; z-index: 1;">
           
        </div>
    </div>
    <div class="max-w-4xl px-4 mx-auto sm:px-6 lg:px-8 pt-8">
        <div class="flex flex-col md:gap-8 text-slate-600">
            <div>
                <p class="font-bold text-slate-500 text-lg">L’expertise numérique au service de votre transformation</p>
                <p class="text-slate-500">
                    Chez Infini Software, nous croyons que la technologie ne doit pas être un luxe inaccessible, mais un
                    véritable levier de croissance, de gestion et d’impact. Notre mission est simple : offrir à chaque
                    organisation, petite ou grande, les moyens numériques adaptés à ses réalités, ses défis et ses
                    ambitions.
                </p>
            </div>

            <div>
                <p class="font-bold text-slate-500 text-lg">💼 Qui sommes-nous ?</p>
                <p class="text-slate-500">
                    Fondée par des passionnés de technologie et d’innovation, Infini Software est une entreprise
                    spécialisée dans le développement de solutions logicielles sur mesure. Nous intervenons dans des
                    domaines variés : éducation, gestion administrative, transport, finance, santé et bien plus encore.

                    Notre approche repose sur l’écoute, la co-construction et la rigueur technique. Chaque solution que
                    nous développons est pensée pour durer, évoluer et s’intégrer harmonieusement dans votre
                    environnement existant.
                </p>
            </div>

            <div>
                <p class="font-bold text-slate-500 text-lg">🌍 Notre vision</p>
                <p class="text-slate-500">
                    Nous aspirons à devenir un acteur de référence dans l’accompagnement numérique, en misant sur
                    l’agilité, la transparence et la qualité.
                    Nous ne créons pas des outils génériques : nous bâtissons des solutions évolutives, adaptées, et
                    surtout, utiles.
                </p>
            </div>

            <div>
                <p class="font-bold text-slate-500 text-lg">🚀 Ce qui nous distingue</p>
                <p class="text-slate-500 py-2">
                    <strong>Une expertise technique solide </strong> : nos développeurs maîtrisent les technologies
                    modernes, en local comme en ligne.
                </p>
                <p class="text-slate-500 py-2">
                    <strong>Une approche humaine et personnalisée </strong> : : chaque client est unique, et nous
                    avançons à votre rythme.
                </p>

                <p class="text-slate-500 py-2">
                    <strong>Une structure flexible </strong> : capable d’intervenir aussi bien en local (client-serveur)
                    qu’en mode hébergé (cloud).
                </p>

                <p class="text-slate-500 py-2">
                    <strong>Une synchronisation en temps réel </strong> : nos solutions permettent à vos équipes de
                    rester connectées, où qu’elles soient.
                </p>







            </div>


            <div>
                <p class="font-bold text-slate-500 text-lg">🤝 Une collaboration durable</p>
                <p class="text-slate-500">
                    Travailler avec Infini Software, c’est choisir un partenaire engagé à vos côtés, du premier
                    rendez-vous jusqu’au déploiement, et au-delà.
                </p>
                <p class="text-slate-500 pt-2">
                    Nous accompagnons nos clients dans la prise en main, la formation, la maintenance, et nous restons
                    présents pour faire évoluer votre solution selon vos besoins futurs.
                </p>



            </div>

            <div class="mt-4">
                <p class="font-bold text-slate-500 text-lg">Infini Software, c’est :</p>
                <p class="text-slate-500">
                    ✔ Une expertise technologique à la pointe
                </p>
                <p class="text-slate-500 pt-1">
                    ✔ Des solutions fiables, robustes et sécurisées
                </p>

                <p class="text-slate-500 pt-1">
                    ✔ Un accompagnement humain et de proximité
                </p>
                <p class="text-slate-500 pt-1">
                    ✔ Un engagement pour la réussite de vos projets numériques
                </p>

            </div>

        </div>


    </div>

</template>