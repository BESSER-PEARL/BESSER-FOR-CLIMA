<script setup>
import { ref, onMounted } from 'vue';

import { useI18n } from 'vue-i18n';
const { locale } = useI18n();

const name = ref("")
const password = ref("")



const rules = [value => {
    if (value == "") {
        return "Please enter an email address!"
    }
    return true
}]


const login = async () => {

    try {
        console.log("attempting log in")
        const response = await fetch('http://localhost:8000/user/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: name.value,
                password: password.value
            })
        })
        console.log("this is respone")
        console.log(response)
        if (response.ok) {
            console.log("got log in response")
            const data = await response.json()
            console.log("this is the data", data)
            if (data && 'access_token' in data) {
                window.alert("Successful login")
                localStorage.setItem("login", data["firstName"])
                localStorage.setItem("loginToken", data["access_token"])
                localStorage.setItem("userType", data["type_spec"])
                localStorage.setItem("userCityName", data["city_name"])
                window.location.reload();
            } else {
                window.alert("Wrong Credentials")
            }
        } else {
            window.alert("Wrong Credentials")
        }
    } catch (err) {
        console.error(err)
    }
}

const menu = ref(false)

const toggleLogin = () => {
  window.history.back()
}

</script>

<template>
    <div>

        <div class="popup">
            
            <div class="popup-inner">


                <v-sheet class="mx-auto" width="300">
                    <h4 class="text-h5 font-weight-bold mb-4" style>{{$t('login.login')}}</h4>
                    <v-form fast-fail @submit.prevent>
                        <v-text-field v-model=name :rules :label="$t('login.email')"></v-text-field>

                        <v-text-field v-model=password type="password" :label="$t('login.password')"></v-text-field>

                        <v-btn class="mt-2" type="submit" block @click="login">{{$t('login.submit')}}</v-btn>
                        <v-btn class="mt-2" block @click="toggleLogin">{{$t('login.cancel')}}</v-btn>
                    </v-form>
                </v-sheet>
            </div>
        </div>

    </div>
</template>



<style lang="scss" scoped>


.popup {
    border-color: #636363 ;
    border-style: solid;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.2);



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

}
</style>