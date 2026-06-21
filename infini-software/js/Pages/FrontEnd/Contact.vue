<script setup>
import GuestLayout from "@/Layouts/GuestLayout.vue";
import InputError from "@/Components/InputError.vue";
import InputLabel from "@/Components/InputLabel.vue";
import TextInput from "@/Components/TextInput.vue";
import { useForm } from "@inertiajs/vue3";
import PrimaryButton from "@/Components/PrimaryButton.vue";

defineOptions({
  layout: GuestLayout,
});

const formContact = useForm({
  nom: "",
  email: "",
  message: "",
});

const sumitFormContact = () => {
  console.log('000');
}
</script>

<template>
  <div class="max-w-6xl px-4 mx-auto sm:px-6 lg:px-8 pt-4 pb-16">

    <div class="pt-28 flex justify-center">
      <h1 class="text-lg md:text-3xl text-gray-700 font-bold text-center">Avez-vous une question ?<span
          class="text-[#ff9e37] ms-2">
          Contactez-nous !</span>
      </h1>
    </div>

    <div class="flex justify-center pb-4">

      <div class="flex flex-col justify-center md:w-8/12 text-slate-500 text-md">
        <p style="text-align: justify;"> Une question, un besoin spécifique ou simplement envie d’échanger avec nous ?
          Notre équipe est à votre écoute et s'engage à vous répondre dans les plus brefs délais.</p>
        <p style="text-align: justify;" class="py-1 text-slate-600">
          Remplissez le formulaire ci-dessous ou utilisez les coordonnées fournies — chez Infini Software, chaque
          message compte, et chaque client est important.
        </p>

        <!-- Nous sommes là pour vous accompagner.
Infini Software — votre partenaire de confiance en solutions numériques. -->
      </div>
    </div>

    <div class="flex flex-col md:flex-row justify-between items-center py-6 gap-4">

      <div class="flex items-center gap-4 w-full">
        <i
          class="ri-mail-line text-white text-2xl bg-[#0f705d] w-8 h-8 p-6 rounded-full flex justify-center items-center"></i>


        <div class=" w-full">
          <p class="text-slate-500 font-bold text-xl">Contactez-nous</p>
          <p class="text-slate-500 ">T&eacute;l&eacute;phone: <span class="text-[#000] ms-2 font-bold"> <span>(+509)
                00000000</span> </span></p>
          <p class="text-slate-500 ">Email: <span>email@gmail.com</span></p>
        </div>

      </div>

      <div class="flex items-center gap-4 w-full">
        <i
          class="ri-time-line text-white text-2xl  bg-[#0f705d] w-8 h-8 p-6 rounded-full flex justify-center items-center"></i>
        <div class="w-full">
          <p class="text-slate-500 font-bold text-xl">Horaires d'ouverture</p>
          <p class="text-slate-500 ">Lundi - Ven: 7.00 am - 4.00 pm</p>
          <!-- <p class="text-slate-500">Sunday: 8.00 am - 6.00 pm</p> -->
        </div>
      </div>

      <div class="flex items-center gap-4 w-full">
        <i
          class="ri-map-pin-line text-white text-2xl bg-[#0f705d] w-8 h-8 p-6 rounded-full flex justify-center items-center "></i>
        <div class=" w-full">
          <p class="text-slate-500 font-bold text-xl">Notre emplacement</p>
          <p class="text-slate-500 font-mediums">adresse---</p>
        </div>
      </div>
    </div>

    <div class="py-2 w-full rounded relative">
      <!-- <div class="absolute inset-0 bg-black/15 z-10 rounded"></div> -->
      <iframe
        src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3783.540663916702!2d-72.6205054898821!3d18.504454169594933!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8eb9cd6ca3f40cc3%3A0x181ab0cbaefd79ef!2sDarbone!5e0!3m2!1sfr!2sht!4v1738351385206!5m2!1sfr!2sht"
        width="100%" height="400" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"
        class="w-full border rounded"></iframe>

    </div>

    <div class="flex flex-col md:flex-row justify-between pt-4 pb-14 gap-4 items-center ">
      <div class="w-full md:w-5/12 h-full relative">
        <div class="absolute inset-0 bg-black/35 z-10 rounded"></div>


        <!-- <img src="./../../../../public/images/contact.jpg" class="w-full rounded object-cover" alt="" srcset=""> -->
      </div>

      <div class="w-full md:w-7/12 md:border md:px-6 py-2 rounded bg-white">
        <form action="" @submit.prevent="sumitFormContact">
          <!-- <div class="d-flex justify-content-center"> -->
          <div class="flex flex-col md:flex-row items-center md:gap-4">

            <div class="mb-3 w-full">
              <InputLabel for="nom" value="Nom Complet" />
              <TextInput id="nom" v-model="formContact.nom" type="text" class="w-full" autocomplete="nom" />
              <InputError class="mt-2" :message="formContact.errors.nom" />
            </div>


            <div class="mb-3 w-full">
              <InputLabel for="mail" value="Votre Email" />
              <TextInput id="mail" v-model="formContact.email" type="text" class="w-full" autocomplete="mail" />
              <InputError class="mt-2" :message="formContact.errors.mail" />
            </div>
          </div>

          <div class="mb-3">
            <InputLabel for="message" value="Votre Message" />
            <textarea
              class="border-gray-300 focus:border-sky-600 focus:ring-sky-600 py-[2px] rounded-md shadow-sm w-full text-lg text-gray-600 resize-none"
              v-model="formContact.message" name="" id="message" rows="4"></textarea>
            <InputError class="mt-2" :message="formContact.errors.message" />

          </div>


          <div class="flex justify-end">
            <PrimaryButton>Envoyer</PrimaryButton>
          </div>
          <!-- </div> -->

        </form>
      </div>
    </div>


    <div class="flex flex-col md:flex-row mt-4 mb-2 justify-between gap-4">
      <div class="w-full mb-5">
        <div class="card border border-success relative rounded-lg">

          <div class="absolute inset-x-0 -top-7 flex justify-center">
            <img width="50" height="50" src="https://u-paris.fr/wp-content/uploads/2022/03/SiegeUP_1920-1.jpg"
              class="object-cover rounded-full w-14 h-14 shadow-lg" alt="Ayesha Ravi">
          </div>

          <div class="card-body hover-overlay overflow-x-auto pt-8" style="height: 200px;">
            <h5 class="text-center"><strong>Président Directeur Général</strong></h5>
            <p class="text-center text-success  mb-1 font-bold fs-6">Directeur Général</p>
            <p class="text-center  mb-1">generalorg@yahoo.fr</p>
            <p class="text-center  mb-1">(+509)3117-8039</p>
          </div>
        </div>
      </div>
      <div class="w-full mb-5">
        <div class="card border border-success relative rounded-lg">

          <div class="absolute inset-x-0 -top-7 flex justify-center">
            <img width="50" height="50" src="https://u-paris.fr/wp-content/uploads/2022/03/SiegeUP_1920-1.jpg"
              class="object-cover rounded-full w-14 h-14 shadow-lg" alt="Ayesha Ravi">
          </div>

          <div class="card-body hover-overlay overflow-x-auto pt-8" style="height: 200px;">
            <h5 class="text-center"><strong>Directrice Exécutif</strong></h5>
            <p class="text-center text-warning  mb-1 font-bold fs-6">Directrice Exécutif Eloi</p>
            <p class="text-center  mb-1">directtalorg@yahoo.fr</p>
            <p class="text-center  mb-1">(+509)3007-8039</p>
          </div>
        </div>
      </div>
      <div class="w-full mb-5">
        <div class="card border border-success relative rounded-lg">

          <div class="absolute inset-x-0 -top-7 flex justify-center">
            <img width="50" height="50" src="https://u-paris.fr/wp-content/uploads/2022/03/SiegeUP_1920-1.jpg"
              class="object-cover rounded-full w-14 h-14 shadow-lg" alt="Ayesha Ravi">
          </div>

          <div class="card-body hover-overlay overflow-x-auto pt-8" style="height: 200px;">
            <h5 class="text-center"><strong>Responsable Financier</strong></h5>
            <p class="text-center text-info  mb-1 font-bold fs-6">Responsable Financier Mireille</p>
            <p class="text-center  mb-1">email@yahoo.fr</p>
            <p class="text-center  mb-1">phone</p>
          </div>
        </div>
      </div>

    </div>

    <!-- <div class="flex mt-8">
      <div class="w-full mb-5">
        <div class="card border border-success relative rounded-lg">

          <div class="absolute inset-x-0 -top-7 flex justify-center">
            <img width="50" height="50" src="https://u-paris.fr/wp-content/uploads/2022/03/SiegeUP_1920-1.jpg"
              class="object-cover rounded-full w-14 h-14 shadow-lg" alt="Ayesha Ravi">
          </div>

          <div class="card-body hover-overlay overflow-x-auto pt-8" style="height: 200px;">
            <h5 class="text-center"><strong>Responsable /technique</strong></h5>
            <p class="text-center text-primary mb-1 font-bold fs-6">Responsable /technique</p>
            <p class="text-center mb-1">email@yahoo.fr</p>
            <p class="text-center mb-1">(509) 08059-7091</p>

          </div>
        </div>
      </div>
      <div class="w-full mb-5">
        <div class="card border border-danger">
          <div class="card-body overflow-y-auto" style="height: 200px;">
            <div class="position-absolute top-0 start-50 translate-middle">
              <img width="50" height="50" src="https://u-paris.fr/wp-content/uploads/2022/03/SiegeUP_1920-1.jpg"
                class="rounded-full h-20 w-20" alt="" srcset="">
            </div>
            <h5 class="text-center"><strong>Responsable Informatique</strong></h5>
            <p class="text-center mb-1 text-danger font-bold fs-6">Responsable Informatique</p>
            <p class="text-center mb-1">responsable@hotmail.fr</p>
            <p class="text-center mb-1">(+509) 37003690</p>

          </div>
        </div>
      </div>
    </div> -->

  </div>
</template>
