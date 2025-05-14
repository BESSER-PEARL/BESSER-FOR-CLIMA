<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import { jwtDecode } from 'jwt-decode'

import { useI18n } from 'vue-i18n';
const { locale } = useI18n();

locale.value = "en"

const loginBool = ref(false)

const name = ref("")
const password = ref("")
const city = ref("");
const userType = ref("");

const loggedIn = ref(false)

const checkIfLogged = () => {
  var userName = localStorage.getItem("login")
  var loginToken = localStorage.getItem("loginToken")
  var userCityName = localStorage.getItem("userCityName");
  var userAccountType = localStorage.getItem("userType");

  if (userName && loginToken) {
    var decoded = jwtDecode(loginToken)
    if (decoded.expires * 1000 > Date.now()) {
      name.value = userName;
      city.value = userCityName || "";
      userType.value = userAccountType || "";
      loggedIn.value = true;
    } else {
      console.log("login token expired, login again");
      localStorage.removeItem("login");
      localStorage.removeItem("loginToken");
      localStorage.removeItem("userCityName");
      localStorage.removeItem("userType");
      loggedIn.value = false;
    }
  } else {
    localStorage.removeItem("login");
    localStorage.removeItem("loginToken");
    localStorage.removeItem("userCityName");
    localStorage.removeItem("userType");
    loggedIn.value = false;
    console.log("not logged in");
  }
}

checkIfLogged()
const tokenCheckInterval = ref(null);
const startTokenCheck = () => {
  tokenCheckInterval.value = setInterval(async () => {
    const token = localStorage.getItem("loginToken");
    if (token) {
      var decoded = jwtDecode(token)
      if (decoded.expires * 1000 > Date.now()) {
        if (decoded.expires * 1000 < Date.now() + 6 * 60 * 1000) {
          try {
            const response = await fetch('http://localhost:8000/user/refresh', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem("loginToken")
              },
              body: JSON.stringify({
                access_token: token
              })
            })
            if (response.ok) {
              const data = await response.json()
              if (data) {
                if ('access_token' in data) {
                  localStorage.setItem("loginToken", data["access_token"])
                } else {
                  window.alert("Problem occured")
                }

              } else {
                window.alert("Problem occured")

              }
            } else {

            }
          } catch (err) {

            console.error(err)
          }
        }
      } else {
        checkIfLogged()
      }
    }

  }, 5 * 60 * 1000); // Check every 5 minutes
};


const rules = [value => {
  if (value == "") {
    return "Please enter an email address!"
  }
}]

const toggleLogin = () => {
  loginBool.value = !loginBool.value
}

const login = async () => {
  try {
    console.log("attempting log in");
    const response = await fetch('http://localhost:8000/user/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: name.value,
        password: password.value,
      }),
    });
    
    if (response.ok) {
      console.log("got login response");
      const data = await response.json();
      if (data) {
        if ('access_token' in data) {
          // window.alert("Successful login");

          // Stocker les informations de l'utilisateur dans le localStorage
          localStorage.setItem("login", data["firstName"]);
          localStorage.setItem("loginToken", data["access_token"]);
          localStorage.setItem("userCityName", data["city_name"] || ""); // Stocker le nom de la ville (si disponible)
          localStorage.setItem("userType", data["type_spec"]); // Stocker le type d'utilisateur (par exemple, admin, cityuser)
          
          // Mettre à jour les variables réactives
          name.value = data["firstName"];
          city.value = data["city_name"] || ""; // Mise à jour de la ville si elle est disponible
          userType.value = data["type_spec"];
          loggedIn.value = true;
          //window.alert(userType.value);
          //window.alert(city.value);
          loginBool.value = false;
          window.location.reload();
        } else {
          window.alert("Wrong Credentials");
        }
      } else {
        window.alert("Wrong Credentials");
      }
    } else {
      console.error("Failed to log in. Response not OK.");
      window.alert("Wrong Credentials");
    }
  } catch (err) {
    console.error(err);
    window.alert("An error occurred while trying to log in.");
  }
};


const logOff = () => {
  localStorage.removeItem("login");
  localStorage.removeItem("loginToken");
  localStorage.removeItem("userCityName"); 
  localStorage.removeItem("userType"); 

  name.value = "";
  city.value = "";
  userType.value = "";
  loggedIn.value = false;

  window.location.reload();
};

const selectedLanguage = ref('EN') // Default language
const languages = ref(
  [{
    "iso639": "EN",
    "name": "English",
    "flag": "openmoji:flag-england"
  },
  {
    "iso639": "IT",
    "name": "Italiano",
    "flag": "openmoji:flag-italy"
  },
  {
    "iso639": "FR",
    "name": "Français",
    "flag": "openmoji:flag-france"
  },
  {
    "iso639": "LU",
    "name": "Lëtzebuergesch",
    "flag": "openmoji:flag-luxembourg"
  },
  {
    "iso639": "SL",
    "name": "Slovenščina",
    "flag": "openmoji:flag-slovenia"
  },
  {
    "iso639": "EL",
    "name": "Ελληνικά",
    "flag": "openmoji:flag-greece"
  },
  {
    "iso639": "PL",
    "name": "Polski",
    "flag": "openmoji:flag-poland"
  },
  {
    "iso639": "CNR",
    "name": "Crnogorski",
    "flag": "openmoji:flag-montenegro"
  },
  {
    "iso639": "CS",
    "name": "Čeština",
    "flag": "openmoji:flag-czechia"
  },
  {
    "iso639": "BS",
    "name": "Bosanski",
    "flag": "openmoji:flag-bosnia-and-herzegovina"
  },
  {
    "iso639": "BG",
    "name": "Български",
    "flag": "openmoji:flag-bulgaria"
  },
  ]
)
function getLanguage() {
  var lang = localStorage.getItem("lang")
  if (lang != null) {
    selectedLanguage.value = lang
    locale.value = lang.toLocaleLowerCase()
  }
}
getLanguage()

const setLanguage = (language) => {
  selectedLanguage.value = language;
  localStorage.setItem("lang", selectedLanguage.value)
  locale.value = selectedLanguage.value.toLocaleLowerCase()

}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

onMounted(() => {
  startTokenCheck();
});



const menu = ref(false)
const isMobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

</script>

<template>
  <div>
    <header>
      <nav class="container">
        <div class="branding">
          <RouterLink to="/"><img class="logo" src="../assets/clima.png" alt=""> </RouterLink>
        </div>
        
        <!-- Add hamburger menu button -->
        <div class="mobile-menu-button" @click="toggleMobileMenu">
          <Icon :icon="isMobileMenuOpen ? 'mdi:close' : 'mdi:menu'" width="30" height="30" />
        </div>

        <ul class="nav-routes" :class="{ 'mobile-menu-active': isMobileMenuOpen }">
          <RouterLink @click="closeMobileMenu" to="/">{{ $t('header.home') }}</RouterLink>
          <!-- <RouterLink @click="closeMobileMenu" to="/demo">DEMO Dashboard</RouterLink> -->
          <RouterLink @click="closeMobileMenu" to="/projects">Dashboard</RouterLink>
          <RouterLink to="/bot">ClimaBot</RouterLink>
          <RouterLink @click="closeMobileMenu" to="/about">{{ $t('header.About') }}</RouterLink>
          <div class="user" @click="toggleLogin">
            <div v-if=!loggedIn class="unauthenticated">
              <Icon icon="mingcute:user-4-fill" width="30" height="30" style="color: #aec326; margin-right: 5px" />
              <p id="login">{{ $t('header.Login') }}</p>
            </div>
            <div v-else class="authenticated">
              <v-menu v-model="menu" :close-on-content-click="false" location="end">
                <template v-slot:activator="{ props }">
                  <Icon icon="mingcute:user-4-fill" width="30" height="30" style="color: #0177a9; margin-right: 5px"
                    v-bind="props" />
                  <p id="login" v-bind="props">{{ name }}</p>
                </template>

                <v-card min-width="300">
                  <v-list>
                    <v-list-item>
                      <div style="display: flex; align-items: center;">
                        <Icon icon="mingcute:user-4-fill" width="30" height="30"/>
                        <p style="margin: 0; margin-left: 8px;">{{ name }}</p>
                      </div>
                    </v-list-item>
                  </v-list>

                  <v-divider></v-divider>

                  <v-list>
                    <v-list-item v-if="userType === 'admin'">
                      <v-btn color="primary" variant="text" @click="$router.push('/admin')">
                        Admin Dashboard
                      </v-btn>
                    </v-list-item>
                    <v-list-item>
                      <v-btn color="primary" variant="text" @click="logOff">
                        Log out
                      </v-btn>
                    </v-list-item>

                  </v-list>
                </v-card>
              </v-menu>
            </div>


          </div>
          <li class="separator"></li> <!-- Separator line -->
          <v-menu>
            <template v-slot:activator="{ props }">
              <p id="language" v-bind="props" @click="closeMobileMenu">
                {{ selectedLanguage }}</p>
            </template>
            <v-list>
              <v-list-item v-for="(item, index) in languages" :key="index" :value="index"
                @click="setLanguage(item.iso639)">
                <v-list-item-title style="display: flex; align-items: center;">
                  <Icon :icon="item.flag" width='30' height='30'
                    style="display: flex; align-items: center; margin-right: 8px;" />
                  {{ item.name }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </ul>
      </nav>
    </header>
    <div v-if=loginBool class="popup">
      <div class="popup-inner">
        <v-sheet class="mx-auto" width="300">
          <v-form fast-fail @submit.prevent>
            <v-text-field v-model=name :rules label="Email Address"></v-text-field>

            <v-text-field v-model=password type="password" label="Password"></v-text-field>

            <v-btn class="mt-2" type="submit" block @click="login">Submit</v-btn>
            <v-btn class="mt-2" block @click="toggleLogin">Cancel</v-btn>
          </v-form>
        </v-sheet>
      </div>
    </div>

  </div>
</template>



<style lang="scss" scoped>
header {
  background-color: hsl(0, 0%, 100%);
  color: #086494;
  position: sticky;
  top: 0;
  z-index: 100;
  max-height: 100vh;
  border-bottom: 2px solid #aec326;
  nav {
    display: flex;
    align-items: center;
    padding: 20px 16px;
    overflow-x: auto;

    .branding {
      display: flex;
      align-items: center;
      gap: 8px;

      img {
        max-width: 200px;
      }

      h1 {
        font-size: 24px;
      }
    }

    .nav-routes {
      display: flex;
      flex: 1;
      justify-content: flex-end;
      gap: 40px;
      list-style: none;
      margin: 0 15px 0 10px;
      align-items: center;


      .user:hover {
        cursor: pointer;
      }

      a {
        text-decoration: none;
        color: inherit;
        font-weight: bold;
        font-size: 20px;
        transition: all 0.3s ease;
        padding: 5px 10px;
        border-radius: 4px;

        &:hover {
          background-color: rgba(0, 0, 0, 0.1);
          transform: translateY(-2px);
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
      }

      #login, a{
        text-decoration: none;
        color: inherit;
        font-weight: bold;
        font-size: 20px;
      }

      #language {
        text-decoration: none;
        font-weight: bold;
        font-size: 20px;
        margin-left: -25px;
        margin-right: -15px;
        align-self: center;
      }

      #language:hover {
        cursor: pointer;
      }

      .user {
        padding-right: 5px;


        .unauthenticated {
          display: flex;
          padding-right: 5px;
          align-items: center;
        }

        .authenticated {
          display: flex;
          padding-right: 5px;
          align-items: center;
        }
      }

      .separator {
        width: 2px;
        /* Thin line */
        height: 30px;
        /* Adjust height as needed */
        background-color: #0177a9;
        /* Adjust color as needed */
        margin-left: -25px;
        /* Adjust spacing as needed */
      }

    }

    .mobile-menu-button {
      display: none;
      cursor: pointer;
      margin-left: auto;
      color: #086494;
    }

    @media (max-width: 768px) {
      .mobile-menu-button {
        display: block;
      }

      .nav-routes {
        display: none;
        position: fixed;
        top: 80px;
        left: 0;
        right: 0;
        background: white;
        flex-direction: column;
        padding: 20px;
        gap: 20px;
        border-bottom: 2px solid #aec326;
        
        &.mobile-menu-active {
          display: flex;
        }

        a {
          width: 100%;
          text-align: center;
          padding: 10px;
        }

        .separator {
          width: 100%;
          height: 2px;
          margin: 10px 0;
        }

        .user {
          width: 100%;
          justify-content: center;
          
          .unauthenticated, .authenticated {
            justify-content: center;
          }
        }
      }
    }
  }
}

.branding {
  @media (max-width: 768px) {
    img {
      max-width: 150px !important;
    }
  }
}

.popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99;
  background-color: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;

  .popup-inner {
    background: #ffffff;
    padding: 50px;
  }

  #label {
    font-weight: bold;
  }

  .label {
    font-weight: bold;
    margin-bottom: 5px;
  }

  @media (max-width: 768px) {
    .popup-inner {
      width: 90%;
      padding: 20px;
    }
  }
}

.language-dropdown {
  background-color: #fff;
  border: 1px solid #ccc;
  border-top: none;
  list-style-type: none;
  padding: 0;
  margin: 0;
  cursor: pointer;
  background-color: #f0f0f0;
}

.language-dropdown ul {
  padding: 0;
  margin: 0;
}

.language-dropdown li {
  cursor: pointer;
  padding: 10px;
}

.language-dropdown li:hover {
  background-color: #f0f0f0;
}
</style>