<template>
    <div>
        <NavBar :authenticated="this.authenticated"/>
        <div class="container">
            <div class="row">
                <div class="col-lg-6">
                    <div class="card mt-5">
                        <div class="card-header">
                            <h2>Register to MyYoutube</h2>
                            <p>And start enjoying the world's biggest video platform !</p>
                        </div>
                        <div class="card-body">
                            <div class="form-group">
                                <label for="username">Username</label>
                                <input type="text" class="form-control" id="username" v-model="registration.username" aria-describedby="username" required>
                            </div>
                            <div class="form-group">
                                <label for="pseudo">Pseudo</label>
                                <input type="text" class="form-control" id="pseudo" v-model="registration.pseudo" aria-describedby="pseudo" required>
                            </div>
                            <div class="form-group">
                                <label for="email">Email address</label>
                                <input type="email" class="form-control" id="email" v-model="registration.email" aria-describedby="email" required>
                            </div>
                            <div class="form-group">
                                <label for="password">Password</label>
                                <input type="password" class="form-control" id="password" v-model="registration.password" placeholder="Password" required>
                            </div>
                            <div class="form-group">
                                <label for="cpassword">Confirm password</label>
                                <input type="password" class="form-control" id="cpassword" v-model="registration.cpassword" placeholder="Confirm password" required>
                            </div>
                            <button class="btn btn-primary" v-on:click="register()">Register</button>
                            <notifications group="auth" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import NavBar from '~/components/NavBar.vue'
import Session from '~/middleware/authentication.js'
import User from '~/middleware/user.js'

export default {
    components: {
        NavBar
    },
    data () {
        return {
            session: false,
            authenticated: false,
            registration: {
                username: "",
                pseudo: "",
                email: "",
                password: "",
                cpassword: ""
            }
        }
    },
    mounted() {
        Session.checkAuthentication().then(isAuthenticated => {
            if (isAuthenticated) {
                this.authenticated = true
                this.$router.replace({ name: "dashboard" })
            }
        })
    },
    methods: {
        register() {
            if (this.registration.password != this.registration.cpassword)
                return this.$notify({
                    type: 'error',
                    group: 'auth',
                    title: 'Registration',
                    text: "Passwords don't match"
                })
            
            var user_details = {}
            for (const [key, value] of Object.entries(this.registration))
                if (value.length)
                    user_details[key] = value
            
            if (Object.keys(user_details).length == 5) {
                User.registerUser(user_details).then(response => {
                    const error = ("error" in response && response.error == false) ? false : true
                    // Firing notification
                    this.$notify({
                        type: (error) ? "error" : "success",
                        group: 'auth',
                        title: 'Registration',
                        text: response.message
                    })
                    if (!error) {
                        // Registered : logging in
                        Session.performLogin(this.registration.username, this.registration.password).then(response => {
                            if("error" in response && response.error == false)
                                this.$router.replace({ name: "dashboard" })
                            else
                                this.$notify({
                                    type: 'error',
                                    group: 'auth',
                                    title: 'Authentication',
                                    text: response.message
                                })
                        })
                    }
                })
            } else {
                this.$notify({
                    type: 'warn',
                    group: 'auth',
                    title: 'Registration',
                    text: "Please fill all the fields"
                })
            }
        },
    }
}
</script>
