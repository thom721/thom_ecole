<template>
  <div class="dashboard-container">
    <aside class="sidebar">
      <h2>Administration</h2>
      <nav>
        <ul>
          <li><RouterLink to="/admin/dashboard">Tableau de bord</RouterLink></li>
          <!-- <li><RouterLink to="/admin/transactions">Transactions</RouterLink></li>
          <li><RouterLink to="/admin/etudiants">Gestion Étudiants</RouterLink></li> -->
        </ul>
      </nav>
    </aside>

    <main class="content">
      <header>
        <h1>Bienvenue, {{ authStore.user?.username || 'Administrateur' }}</h1>
        <p>Voici l'état actuel de votre système scolaire.</p>
      </header>

      <section class="stats-grid">
        <div class="stat-card">
          <h3>Transactions</h3>
          <p class="number">128</p>
        </div>
        <div class="stat-card">
          <h3>Étudiants</h3>
          <p class="number">1,050</p>
        </div>
        <div class="stat-card">
          <h3>Alertes</h3>
          <p class="number text-red">3</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '../../stores/auth'
import { RouterLink } from 'vue-router'

const authStore = useAuthStore()
</script>

<style scoped>
.dashboard-container {
  display: flex;
  min-height: 80vh;
  gap: 20px;
}

.sidebar {
  width: 250px;
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.sidebar ul {
  list-style: none;
  padding: 0;
}

.sidebar li {
  margin: 10px 0;
}

.sidebar a {
  text-decoration: none;
  color: #333;
  display: block;
  padding: 10px;
  border-radius: 4px;
}

.sidebar a.router-link-active {
  background-color: #42b983;
  color: white;
}

.content {
  flex: 1;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.number {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
}

.text-red {
  color: #e74c3c;
}
</style>