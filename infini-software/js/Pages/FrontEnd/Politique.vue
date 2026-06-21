<script setup>
import GuestLayout from "@/Layouts/GuestLayout.vue";
import { Transition, onMounted, ref } from 'vue';


defineOptions({
    layout: GuestLayout,
});

</script>

<template>
    <div class="img">
        <div style="position: relative; z-index: 1;">
            <!-- Ton contenu ici -->
        </div>
    </div>
    <div class="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8 pt-8">
        <div class="flex flex-col md:flex-row items-center gap-10">

            <div class="w-full text-slate-500">
                🔐 Politique de Confidentialité – Infini Software
                Dernière mise à jour : 23/07/2025

                <p class="text-slate-600 text-md font-bold mt-2">1. Introduction </p>
                Infini Software attache une grande importance à la confidentialité des données personnelles de ses
                clients, utilisateurs finaux, partenaires et visiteurs. La présente Politique de Confidentialité
                explique quelles données sont collectées, comment elles sont utilisées, stockées, et protégées dans le
                cadre des services que nous proposons.

                <p class="text-slate-600 text-md font-bold mt-2">2. Qui sommes-nous ? </p>
                Infini Software est une entreprise spécialisée dans le développement et la fourniture de solutions
                logicielles, localement ou via des serveurs en ligne sur demande.

                📍 Siège :#70 Delmas 75, Port-au-Prince, Haïti
                📧 Contact : privacy@infini-software.com

                <p class="text-slate-600 text-md font-bold mt-2">3. Données collectées </p>
                Dans le cadre de nos prestations, nous pouvons collecter les types de données suivants :

                a. Données des clients professionnels :
                Nom, prénom

                , fonction

                Email professionnel, téléphone

                Détails du projet ou des besoins techniques

                b. Données d'utilisation des logiciels :
                Données de connexion (IP, logs, identifiants anonymes)

                Données de navigation ou d’interaction avec les interfaces

                Données des utilisateurs finaux (si vous nous confiez l’hébergement ou le support technique)

                c. Données techniques :
                Informations sur le système ou appareil utilisé

                Données synchronisées entre l’environnement local et le serveur distant

                <p class="text-slate-600 text-md font-bold mt-2">4. Finalité du traitement </p>
                Les données collectées sont utilisées uniquement pour :

                Fournir, sécuriser et maintenir les services proposés

                Gérer la relation client et le support technique

                Effectuer des sauvegardes et synchronisations en temps réel

                Améliorer les performances et la sécurité des systèmes

                Aucune donnée n’est vendue ou louée.

                <p class="text-slate-600 text-md font-bold mt-2">5. Hébergement et sécurité </p>
                Les données peuvent être hébergées localement chez le client ou dans un environnement cloud sécurisé sur
                demande.

                Toutes les données transitent via des protocoles sécurisés (ex. : HTTPS, SFTP).

                Des mesures techniques (chiffrement, pare-feu, contrôles d’accès) et organisationnelles (contrats,
                engagements de confidentialité) sont en place pour protéger les données.

                <p class="text-slate-600 text-md font-bold mt-2">6. Partage des données </p>
                Nous ne partageons vos données qu’avec :

                Des sous-traitants techniques de confiance (hébergeurs, prestataires cloud, etc.), uniquement dans le
                cadre du service

                Les autorités compétentes en cas d’obligation légale

                Chaque tiers est tenu par un accord de confidentialité et ne peut utiliser les données que pour exécuter
                sa mission.

                <p class="text-slate-600 text-md font-bold mt-2">7. Vos droits </p>
                Conformément à la réglementation sur la protection des données (RGPD ou législation locale équivalente),
                vous disposez de :

                Droit d’accès à vos données

                Droit de rectification

                Droit à l’effacement

                Droit d’opposition ou de limitation du traitement

                Droit à la portabilité

                📧 Pour exercer ces droits : privacy@infini-software.com

                <p class="text-slate-600 text-md font-bold mt-2">8. Durée de conservation </p>
                Les données personnelles sont conservées uniquement le temps nécessaire à la finalité pour laquelle
                elles ont été collectées, et conformément aux obligations légales.

                <p class="text-slate-600 text-md font-bold mt-2">9. Cookies et données de navigation </p>
                Notre site web peut utiliser des cookies techniques strictement nécessaires à son bon fonctionnement.
                Aucun cookie de suivi publicitaire ou tiers n’est installé sans votre consentement explicite.

                <p class="text-slate-600 text-md font-bold mt-2">10. Modification de cette politique </p>
                Infini Software se réserve le droit de modifier cette politique à tout moment. En cas de modification
                majeure, nous informerons nos clients par email ou via notre site web.

            </div>


        </div>
    </div>
</template>