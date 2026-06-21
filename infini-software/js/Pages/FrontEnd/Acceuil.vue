<script setup>
import Carousel from "@/Components/Carousel.vue";
import GuestLayout from "@/Layouts/GuestLayout.vue";
import { onMounted, Transition } from "vue";
import Swiper from 'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.mjs'
import { Link } from '@inertiajs/vue3';
import ScrollReveal from 'scrollreveal';

defineOptions({
  layout: GuestLayout,
});



// })

onMounted(() => {
  const swiper = new Swiper('.swiper', {

    effect: 'coverflow',
    grabCursor: true,
    centeredSlides: true,
    initialSlides: 5,
    speed: 400,
    preventClicks: true,
    slidesPerView: 'auto',

    coverflowEffect: {
      rotate: 0,
      stretch: 280,
      depth: 80,
      modifier: 1,
      slideShadow: true
    },

    on: {
      click(event) {
        swiper.slideTo(this.clickedIndex)
      },
    },

    autoplay: {
      delay: 2000,
      disableOnInteraction: false
    },

    // If we need pagination
    pagination: {
      el: '.swiper-pagination',
      clickable: true
    },



  });

  window.sr = ScrollReveal({ duration: 1000, distance: '60px', easing: 'ease-out' });

  sr.reveal('.header_text', { origin: 'left', reset: true })
  sr.reveal(`.btn_about, .img_body_about`, { origin: 'right', reset: true })

  sr.reveal('.riview_header', { origin: 'top', reset: true })
  sr.reveal('.join_text', { scale: 0.7, reset: true })

  sr.reveal(`.local_support_header, .text_body_about`, { origin: 'left', reset: true })
  sr.reveal(`.local_support_img, .about_text_title`, { origin: 'top', reset: true })
  sr.reveal(`.btn_boutique, .about_text_text`, { origin: 'bottom', reset: true })

  sr.reveal(`.join_img1, .text_body_about_s`, { scale: 0.8, reset: true })
  sr.reveal('.join_img2', { origin: 'right', reset: true })
  sr.reveal('.join_img3', { origin: 'bottom', reset: true })
  sr.reveal('.join_img4', { origin: 'bottom', reset: true, distance: 'top-7px' })

  const options = {
    root: null, // Utiliser la fenêtre comme racine
    rootMargin: "0px", // Marge autour de la fenêtre
    threshold: 0.1, // Le seuil de visibilité
  };

})

</script>

<template>

  <div class="swiper">
    <div class="absolute inset-0 bg-black/70 w-full h-[500px] md:h-[400px] z-20"></div>

    <div class="absolute inset-0 z-30">
      <div class="flex justify-center items-center h-[500px] md:h-[400px]">
        <div class="md:w-5/12 mt-8">
          <p class="text-xl font-bold text-sky-600 px-4">🌐 Bienvenue chez Infini Software</p>
          <p class="text-white text-md md:text-lg px-4 leading-3 header_text text-justify">
            <span class="py-1 block">L'innovation logicielle au service de votre réussite.</span>
            Chez Infini Software, nous concevons des solutions numériques sur mesure, pensées pour s’adapter à vos
            besoins, votre environnement et vos ambitions. Que vous soyez une école, une entreprise, une institution ou
            un professionnel indépendant, notre mission est de vous accompagnons avec des outils performants, sécurisés
            et durables.

          </p>
          <div class="mt-2 flex justify-center">


            <div class="flex flex-col md:flex-row justify-center items-center gap-4 md:gap-10 mt-4 animate">
              <div class="btn_boutique">
                <a href="#boutique"
                  class="px-2 sm:px-4 py-2 rounded-lg font-extrabold text-lg text-white bg-sky-600 hover:bg-sky-800  transition-all duration-300 animate-pulse">Infini-software
                  Boutique</a>
              </div>

              <div class="btn_about">
                <Link :href="route('about')"
                  class="inline-flex justify-center items-center px-4 py-2  border border-[#fedd52] rounded-md font-semibold text-xs text-[#ffd709] hover:text-[#0f705d] uppercase tracking-widest hover:bg-[#ffd709] focus:bg-[#ffd709] active:bg-[#ffd709] focus:outline-none focus:ring-0 focus:ring-[#ffd709] focus:ring-offset-2 disabled:opacity-50 transition ease-in-out duration-150 ">
                En Savoir Plus</Link>
              </div>


            </div>


          </div>
        </div>
      </div>
    </div>
    <div class="swiper-wrapper">
      <div class="swiper-slide ">
        <img loading="lazy" class="h-[500px] md:h-[400px] w-full bg-no-repeat object-cover object-"
          src="./../../../../public/images/gif2.webp" alt="" srcset="" style="object-position: 20% 55%;">

      </div>

      <div class="swiper-slide h-[26rem]">


        <img loading="lazy" class="h-[500px] md:h-[400px] w-full bg-no-repeat object-cover "
          src="./../../../../public/images/gif3.webp" alt="" srcset="" style="object-position: 20% 60%;">
      </div>

      <div class="swiper-slide">
        <img loading="lazy" class="h-[500px] md:h-[400px] w-full bg-no-repeat object-cover "
          src="./../../../../public/images/gif4.webp" alt="" srcset="">
      </div>

      <div class="swiper-slide ">
        <img loading="lazy" class="h-[500px] md:h-[400px] w-full bg-no-repeat object-cover "
          src="./../../../../public/images/gif5.webp" alt="" srcset="">
      </div>

    </div>
  </div>

  <div class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 space-y-12 overflow-hidden">
    <div class="flex flex-col md:flex-row md:gap-8 gap-4 items-center">
      <img loading="lazy" src="./../../../../public/images/coding_image.webp"
        class="w-full md:w-80 h-44 object-cover rounded-lg local_support_img" alt="" sizes="" srcset="">
      <div class="join_img3">
        <p class="mb-1 font-bold text-xl text-slate-700">Développement d’applications web, mobile et desktop</p>
        <p class="text-slate-500 text-justify">
          Chez Infini Software, nous transformons vos idées en solutions concrètes. Notre équipe conçoit des
          applications robustes et modernes, qu'elles soient destinées au web, aux smartphones ou aux ordinateurs de
          bureau. Chaque projet est développé sur mesure, avec une attention particulière à l’ergonomie, la performance
          et la maintenabilité. Nous utilisons des technologies de pointe pour garantir des interfaces fluides, une
          expérience utilisateur optimisée et un fonctionnement stable sur tous les appareils. Nos applications ne sont
          pas seulement belles : elles sont pensées pour répondre à vos objectifs métier avec précision et efficacité.
        </p>
      </div>
    </div>

    <div class="flex flex-col md:flex-row md:gap-8 gap-4 items-center mt-4">
      <img loading="lazy" src="./../../../../public/images/cloud.webp"
        class="w-full md:w-80 h-44 object-cover rounded-lg join_img2" alt="" sizes="" srcset="">
      <div class="join_img3">
        <p class="mb-1 font-bold text-xl text-slate-700">Solutions hybrides : locales (client-serveur) ou hébergées en
          ligne</p>
        <p class="text-slate-500 text-justify">
          Chaque organisation a ses contraintes : budget, infrastructure, politique de sécurité, connectivité. C’est
          pourquoi nous proposons des solutions hybrides, déployables en local ou en ligne selon vos préférences. Vous
          pouvez héberger vos données dans vos propres serveurs pour un contrôle total, ou opter pour un hébergement
          cloud sécurisé accessible partout. Quelle que soit l’option choisie, notre architecture garantit la
          continuité, la performance et l’évolutivité. Nous vous donnons la liberté de choisir votre mode de
          fonctionnement, sans compromis sur la qualité.
        </p>
      </div>
    </div>

    <div class="flex flex-col md:flex-row md:gap-8 gap-4 items-center">

      <img loading="lazy" src="./../../../../public/images/2997438_.webp"
        class="w-full md:w-80 h-44 object-cover rounded-lg btn_about" alt="" sizes="" srcset="">


      <div class="join_img2">
        <p class="mb-1 font-bold text-xl text-slate-700">Systèmes synchronisés en temps réel</p>
        <p class="text-slate-500 text-justify">
          Vos utilisateurs n’ont pas le temps d’attendre, et votre organisation ne peut pas se permettre de travailler
          sur des informations obsolètes. Nos solutions assurent une synchronisation rapide et sécurisée des données en
          temps réel, que ce soit entre plusieurs appareils, entre un site local et un serveur distant, ou entre
          plusieurs utilisateurs. Vous bénéficiez d’un flux de travail harmonisé, d’une prise de décision instantanée et
          d’une transparence totale. C’est la promesse d’une collaboration fluide, sans délai, sans duplication, sans
          confusion.
        </p>
      </div>
    </div>


    <div class="flex flex-col md:flex-row md:gap-8 gap-4 items-center">
      <img loading="lazy" src="./../../../../public/images/traning_2.webp"
        class="w-full md:w-80 h-44 object-cover rounded-lg join_img3" alt="" sizes="" srcset="">
      <div class="local_support_header">
        <p class="mb-1 font-bold text-xl text-slate-700">Déploiement sur mesure et formation</p>
        <p class="text-slate-500 text-justify">
          Vos utilisateurs n’ont pas le temps d’attendre, et votre organisation ne peut pas se permettre de travailler
          sur des informations obsolètes. Nos solutions assurent une synchronisation rapide et sécurisée des données en
          temps réel, que ce soit entre plusieurs appareils, entre un site local et un serveur distant, ou entre
          plusieurs utilisateurs. Vous bénéficiez d’un flux de travail harmonisé, d’une prise de décision instantanée et
          d’une transparence totale. C’est la promesse d’une collaboration fluide, sans délai, sans duplication, sans
          confusion.
        </p>
      </div>
    </div>

    <div class="flex flex-col md:flex-row md:gap-8 gap-4 items-center">
      <img loading="lazy" src="./../../../../public/images/support.webp"
        class="w-full md:w-80 h-44 object-cover rounded-lg local_support_header" alt="" sizes="" srcset="">
      <div class="join_img3">
        <p class="mb-1 font-bold text-xl text-slate-700"> Assistance technique et maintenance continue</p>
        <p class="text-slate-500 text-justify">
          Votre tranquillité d’esprit, c’est notre mission. Après le déploiement, nous restons à vos côtés pour répondre
          à vos
          questions, corriger les éventuelles anomalies, et faire évoluer la solution selon vos besoins. Grâce à notre
          service
          d’assistance réactif et à notre système de maintenance proactive, vos outils restent performants, sécurisés et
          à
          jour. Vous bénéficiez d’un véritable contrat de confiance, basé sur la disponibilité, la transparence et la
          qualité
          du service.
        </p>
      </div>
    </div>



  </div>

  <div class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 space-y-12 overflow-hidden transition-all duration-500"
    id="boutique">

    <!-- <div class="flex">
      <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Illum sequi totam assumenda voluptates, repellendus
        sapiente delectus sed est, aliquid, similique blanditiis ea rem aliquam explicabo neque officia laudantium
        tenetur natus?</p>
      <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Illum sequi totam assumenda voluptates, repellendus
        sapiente delectus sed est, aliquid, similique blanditiis ea rem aliquam explicabo neque officia laudantium
        tenetur natus?</p>

      <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Illum sequi totam assumenda voluptates, repellendus
        sapiente delectus sed est, aliquid, similique blanditiis ea rem aliquam explicabo neque officia laudantium
        tenetur natus?</p>

      <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Illum sequi totam assumenda voluptates, repellendus
        sapiente delectus sed est, aliquid, similique blanditiis ea rem aliquam explicabo neque officia laudantium
        tenetur natus?</p>
    </div> -->

  </div>

  <!-- 💡 Pourquoi choisir Infini Software ?
🔒 Fiabilité & Sécurité
📸 Image suggérée : Un cadenas numérique intégré dans une interface de sécurité.
📝 Description longue :
La sécurité est au cœur de notre ADN. Dès les premières lignes de code, nous mettons en place des pratiques rigoureuses pour protéger vos données, vos utilisateurs et vos activités. Nos systèmes sont construits avec des mécanismes de chiffrement, des pare-feux intelligents, des audits réguliers et des sauvegardes automatisées. Vous pouvez dormir tranquille : vos informations sensibles ne seront jamais exposées. Chez Infini Software, nous croyons qu’un bon logiciel commence par une bonne défense.

⚡ Réactivité & Support humain
📸 Image suggérée : Une équipe de support en pleine discussion ou un agent au téléphone avec un client.
📝 Description longue :
Nous savons que le temps est une ressource précieuse. C’est pourquoi notre support technique est accessible, réactif et toujours humain. Pas de réponses automatiques impersonnelles : chez Infini Software, vous échangez avec de vraies personnes, compétentes et à l’écoute, qui comprennent vos enjeux et vous apportent des solutions concrètes. Que ce soit pour une question urgente ou un simple conseil, vous pouvez compter sur nous.

🎯 Solutions adaptées à votre réalité métier
📸 Image suggérée : Une cible atteinte, entourée d’icônes représentant différents secteurs d’activité.
📝 Description longue :
Chaque organisation est unique, et nous en tenons compte à chaque étape de notre démarche. Avant de développer, nous prenons le temps de comprendre vos processus, vos contraintes et vos objectifs. C’est ce qui nous permet de créer des outils vraiment utiles, qui s’intègrent à votre environnement sans perturber votre façon de travailler. Avec Infini Software, vous ne vous adaptez pas au logiciel : c’est le logiciel qui s’adapte à vous.

🌱 Accompagnement sur le long terme
📸 Image suggérée : Une plante qui pousse dans une main, symbolisant l’évolution et la pérennité.
📝 Description longue :
Nous ne cherchons pas à vous vendre un service ponctuel, mais à établir une relation durable. Nous construisons avec vous une vision à long terme, en faisant évoluer les outils au fil de vos besoins. En choisissant Infini Software, vous investissez dans un partenariat technique fiable, capable de grandir avec vous. C’est la promesse d’un suivi continu, d’un dialogue ouvert et d’un engagement constant à vos côtés.

🤝 Un partenaire de confiance
📸 Image suggérée : Deux personnes se serrant la main devant un fond numérique ou une interface projetée.
📝 Description longue :
Chez Infini Software, nous croyons que la technologie doit avant tout servir la relation humaine. Derrière chaque solution que nous développons, il y a un dialogue, une compréhension mutuelle, une volonté sincère de résoudre vos défis. Plus qu’un prestataire technique, nous sommes un partenaire stratégique, engagé, rigoureux et à l’écoute. Notre mission : construire des solutions durables, fiables et utiles, qui vous rendent plus autonome et plus fort. -->

</template>