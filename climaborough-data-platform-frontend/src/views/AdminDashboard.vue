<script setup>
import { ref, onMounted } from 'vue';

const newUser = ref({
  email: '',
  password: '',
  firstName: '',
  lastName: '',
  type_spec: 'cityuser',
  city_id: null
});

const cities = ref([
  { id: 1, name: 'Torino' },
  { id: 2, name: 'Cascais' },
  { id: 3, name: 'Differdange' },
  { id: 4, name: 'Sofia' }
]);

const userTypes = [
  { value: 'admin', label: 'Admin' },
  { value: 'cityuser', label: 'City User' },
  { value: 'cityangel', label: 'City Angel' },
  { value: 'solutionprovider', label: 'Solution Provider' },
  { value: 'citizen', label: 'Citizen' }
];

const showCitySelect = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

const handleTypeChange = () => {
  showCitySelect.value = newUser.value.type_spec === 'cityuser';
  if (!showCitySelect.value) {
    newUser.value.city_id = null;
  }
};

const createUser = async () => {
  try {
    const token = localStorage.getItem('loginToken');
    const userData = {
      email: newUser.value.email,
      password: newUser.value.password,
      firstName: newUser.value.firstName,
      lastName: newUser.value.lastName,
      type_spec: newUser.value.type_spec
    };

    // Build query parameters for city_id
    let url = 'http://localhost:8000/user/signup';
    if (newUser.value.type_spec === 'cityuser' && newUser.value.city_id) {
      url += `?city_id=${newUser.value.city_id}`;
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(userData)
    });

    const data = await response.json();

    if (data.error) {
      errorMessage.value = data.error;
      successMessage.value = '';
    } else {
      successMessage.value = 'User created successfully!';
      errorMessage.value = '';
      // Reset form
      newUser.value = {
        email: '',
        password: '',
        firstName: '',
        lastName: '',
        type_spec: 'cityuser',
        city_id: null
      };
    }
  } catch (error) {
    console.error('Error:', error);
    errorMessage.value = 'An error occurred while creating the user.';
    successMessage.value = '';
  }
};
</script>

<template>
  <div class="admin-dashboard">
    <h1>Admin Dashboard - Create User</h1>
    
    <div class="form-container">
      <v-form @submit.prevent="createUser">
        <v-text-field
          v-model="newUser.email"
          label="Email"
          required
        ></v-text-field>

        <v-text-field
          v-model="newUser.password"
          label="Password"
          type="password"
          required
        ></v-text-field>

        <v-text-field
          v-model="newUser.firstName"
          label="First Name"
          required
        ></v-text-field>

        <v-text-field
          v-model="newUser.lastName"
          label="Last Name"
          required
        ></v-text-field>

        <v-select
          v-model="newUser.type_spec"
          :items="userTypes"
          item-title="label"
          item-value="value"
          label="User Type"
          @update:model-value="handleTypeChange"
          required
        ></v-select>

        <v-select
          v-if="showCitySelect"
          v-model="newUser.city_id"
          :items="cities"
          item-title="name"
          item-value="id"
          label="City"
          :rules="[(v) => !!v || 'City is required for city users']"
          required
        ></v-select>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <v-btn type="submit" color="primary" class="mt-4">
          Create User
        </v-btn>
      </v-form>
    </div>
  </div>
</template>

<style scoped>
.admin-dashboard {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.form-container {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.success-message {
  color: #4caf50;
  margin: 10px 0;
  padding: 10px;
  background-color: #e8f5e9;
  border-radius: 4px;
}

.error-message {
  color: #f44336;
  margin: 10px 0;
  padding: 10px;
  background-color: #ffebee;
  border-radius: 4px;
}
</style>
