<template>
    <div>
        <NavBar :authenticated="this.authenticated"/>
        <div class="container">
            <div class="row">
                <div class="col-lg-6">
                    <div class="card mt-5">
                        <div class="card-header">
                            <h2>Sign in</h2>
                        </div>
                        <div class="card-body">
                            <div class="form-group">
                                <label for="username">Username</label>
                                <input type="text" class="form-control" id="username" v-model="username" aria-describedby="username" placeholder="Enter username">
                                <small id="username" class="form-text text-muted">Make sure to enter your username, not your pseudo.</small>
                            </div>
                            <div class="form-group">
                                <label for="password">Password</label>
                                <input type="password" class="form-control" id="password" v-model="password" placeholder="Password">
                            </div>
                            <button class="btn btn-primary" v-on:click="login()">Sign in</button>
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

export default {
    components: {
        NavBar
    },
    data () {
        return {
            authenticated: false, 
            username: "",
            password: ""
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
        login() {
            if(this.username != "" && this.password != "") {
                Session.performLogin(this.username, this.password).then(response => {
                    if("error" in response && response.error == false)
                        this.$router.replace({ name: "dashboard" })
                    else
                        this.$notify({
                            type: 'error',
                            group: 'auth',
                            title: 'Authentication',
                            text: "The username and / or password is incorrect"
                        })
                })
            } else {
                this.$notify({
                    type: 'warn',
                    group: 'auth',
                    title: 'Authentication',
                    text: "A username and password must be present"
                })
            }
        }
    }
}
</script>
