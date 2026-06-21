<script>
export default {

}
</script>
<template>
  <div class="bg-gray-100 text-gray-800">
    <!-- Hero Section -->
    <section
      class="relative bg-yellow-400 text-black h-screen flex flex-col justify-center items-center text-center px-6">
      <div class="absolute top-0 left-0 w-full h-full bg-black opacity-20 z-0"></div>
      <div class="z-10 max-w-2xl">
        <h1 class="text-4xl md:text-6xl font-bold mb-6">Bienvenue sur <span class="text-white">Kikip</span></h1>
        <p class="text-lg mb-6">Votre solution de transport rapide, fiable et sécurisée.</p>
        <button
          class="bg-black text-yellow-400 px-6 py-3 rounded-full font-semibold hover:bg-yellow-500 hover:text-black transition">
          Réserver une course
        </button>
      </div>
    </section>

    <!-- Pourquoi Kikip -->
    <section class="py-16 px-6 text-center bg-white">
      <h2 class="text-3xl font-bold mb-10">Pourquoi choisir Kikip ?</h2>
      <div class="grid md:grid-cols-3 gap-8">
        <div class="bg-gray-50 p-6 rounded-lg shadow hover:shadow-lg transition">
          <img src="https://img.icons8.com/dusk/64/car--v1.png" class="mx-auto mb-4" alt="Voiture">
          <h3 class="text-xl font-semibold">Service rapide</h3>
          <p class="text-gray-600">Trouvez un chauffeur en quelques secondes, où que vous soyez.</p>
        </div>
        <div class="bg-gray-50 p-6 rounded-lg shadow hover:shadow-lg transition">
          <img src="https://img.icons8.com/dusk/64/driver.png" class="mx-auto mb-4" alt="Chauffeur">
          <h3 class="text-xl font-semibold">Chauffeurs qualifiés</h3>
          <p class="text-gray-600">Tous nos conducteurs sont formés et certifiés.</p>
        </div>
        <div class="bg-gray-50 p-6 rounded-lg shadow hover:shadow-lg transition">
          <img src="https://img.icons8.com/dusk/64/price-tag-euro.png" class="mx-auto mb-4" alt="Tarif">
          <h3 class="text-xl font-semibold">Tarifs accessibles</h3>
          <p class="text-gray-600">Des prix compétitifs pour tous vos déplacements.</p>
        </div>
      </div>
    </section>

    <!-- Témoignages -->
    <section class="py-16 px-6 bg-yellow-100">
      <h2 class="text-3xl font-bold text-center mb-12">Ils nous font confiance</h2>
      <div class="flex flex-col md:flex-row justify-center gap-8">
        <div class="bg-white p-6 rounded-lg shadow w-full md:w-1/3">
          <p class="text-gray-700 italic">“Kikip a changé ma manière de me déplacer en ville. C'est rapide et fiable !”
          </p>
          <p class="text-right mt-4 font-semibold">— Aïcha, Dakar</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow w-full md:w-1/3">
          <p class="text-gray-700 italic">“J’ai pu aller au boulot chaque matin à l’heure sans stress.”</p>
          <p class="text-right mt-4 font-semibold">— Karim, Abidjan</p>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-black text-white py-6 px-6 text-center">
      <p>&copy; 2025 Kikip. Tous droits réservés.</p>
    </footer>
  </div>
</template>

<script setup>
// Pas de JS particulier ici pour cette version statique
</script>

<style scoped>
/* Ajout d'un effet de zoom subtil */
img:hover {
  transform: scale(1.05);
  transition: transform 0.3s;
}
</style>