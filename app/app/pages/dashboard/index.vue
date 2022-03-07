<template>
    <div>
        <NavBar :authenticated="this.authenticated"/>
        <div v-if="this.authenticated == true" class="container">
            <div class="row">
                <div class="col-lg-12">
                    <div class="jumbotron">
                        <h1 class="display-4">Welcome, {{this.user_details.username}} <i>aka</i> {{this.user_details.pseudo}} !</h1>
                        <p class="lead">Start exploring now.</p>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-lg-6">
                    <div class="card mt-5">
                        <div v-if="this.user_details != false" class="card-header">
                            <h2>Edit your details</h2>
                        </div>
                        <div v-if="this.user_details != false" class="card-body">
                            <div class="form-group">
                                <label for="username">Username</label>
                                <input type="text" class="form-control" id="username" v-model="user_update.username" aria-describedby="username" required>
                            </div>
                            <div class="form-group">
                                <label for="pseudo">Pseudo</label>
                                <input type="text" class="form-control" id="pseudo" v-model="user_update.pseudo" aria-describedby="pseudo" required>
                            </div>
                            <div class="form-group">
                                <label for="email">Email address</label>
                                <input type="email" class="form-control" id="email" v-model="user_update.email" aria-describedby="email" required>
                            </div>
                            <div class="form-group">
                                <label for="password">Password</label>
                                <input type="password" class="form-control" id="password" v-model="user_update.password" placeholder="Password" required>
                                <small id="password" class="form-text text-muted">Please fill all fields</small>
                            </div>
                            <button class="btn btn-primary" v-on:click="updateProfile()">Update profile</button>
                            <notifications group="auth" />
                            <notifications group="update_profile" />
                        </div>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card mt-5">
                        <div class="card-header">
                            <h2>Your videos</h2>
                        </div>
                        <div class="card-body">
                            <div v-if="this.videos.length == 0">
                                <div class="alert alert-warning">
                                    <p>You have not uploaded any video yet. Start now !</p>
                                </div>
                            </div>

                            <div v-if="this.videos.length" class="row pb-4">
                                <div v-for="video in this.videos" v-bind:key="video.id" class="col-lg-12">
                                    <nuxt-link :to="'/video?id=' + video.id">
                                        <div class="card">
                                            <div class="card-body row">
                                                <div class="col-lg-3">
                                                    <img src="~/assets/multimedia.png" width="100%"/>
                                                </div>
                                                <div class="col-lg-9">
                                                    <h4><div v-html="video.name"></div></h4>
                                                    <p>{{ video.duration }} seconds</p>
                                                    <p>{{ video.created_at.substring(0, video.created_at.length-10).replace("T", " ") }}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </nuxt-link>
                                </div>
                            </div>
                            
                            <div v-if="this.videos.length" class="row mx-auto">
                                <nav aria-label="...">
                                    <ul class="pagination">
                                        <li v-if="this.pager.current == 1" class="page-item disabled">
                                            <button class="page-link" href="#">Previous</button>
                                        </li>
                                        <li v-if="this.pager.current > 1" class="page-item">
                                            <button class="page-link" href="#" @click="loadPreviousVideoPage()">Previous</button>
                                        </li>
                                        <li class="page-item active">
                                            <div class="page-link" href="#">{{this.pager.current}} <span class="sr-only">(current)</span></div>
                                        </li>
                                        <li v-if="this.pager.current == this.pager.total" class="page-item disabled">
                                            <button class="page-link" href="#">Next</button>
                                        </li>
                                        <li v-if="this.pager.current < this.pager.total" class="page-item">
                                            <button class="page-link" href="#" @click="loadNextVideoPage()">Next</button>
                                        </li>
                                    </ul>
                                </nav>
                            </div>
                        </div>
                        <notifications group="load_videos" />
                    </div>
                </div>
            </div>
        </div>
        <notifications group="auth" />
    </div>
</template>

<script>
import NavBar from '~/components/NavBar.vue'
import Session from '~/middleware/authentication.js'
import User from '~/middleware/user.js'
import Video from '~/middleware/video.js'

export default {
    components: {
        NavBar
    },
    data () {
        return {
            user_details: false,
            session: false,
            authenticated: false,
            user_update: {
                username: "",
                pseudo: "",
                email: "",
                password: ""
            },
            videos: [],
            pager: {}
        }
    },
    mounted() {
        this.session = Session.getSession()
        Session.checkAuthentication().then(isAuthenticated => {
            this.authenticated = isAuthenticated
            if (isAuthenticated == false) {
                this.authenticated = false
                this.$router.replace({ path: "/auth/login" })
                this.$notify({
                    type: 'error',
                    group: 'auth',
                    title: 'Authentication',
                    text: "Please login to access this page"
                })
            }
        })
        this.updateUserDetails()
    },
    methods: {
        updateProfile() {
            var to_update = {}
            for (const [key, value] of Object.entries(this.user_update))
                if (value.length)
                    to_update[key] = value
            if (Object.keys(to_update).length == 4) {
                User.updateUserDetails(
                    this.session.id,
                    this.session.token,
                    to_update
                ).then(response => {
                    this.$notify({
                        type: ("error" in response && response.error == false) ? "success" : "error",
                        group: 'update_profile',
                        title: 'Profile update',
                        text: response.message
                    })
                    Session.checkAuthentication()
                    this.updateUserDetails()
                })
            } else {
                this.$notify({
                    type: 'warn',
                    group: 'update_profile',
                    title: 'Profile update',
                    text: "Please fill all the fields"
                })
            }
        },
        updateUserDetails() {
            User.getUserDetails(this.session.id, this.session.token).then(user_details => {
                if (user_details != false) {
                    this.user_details = user_details
                    this.user_update =  {
                        username: ("username" in this.user_details) ? this.user_details.username : "",
                        pseudo: ("pseudo" in this.user_details) ? this.user_details.pseudo : "",
                        email: ("email" in this.user_details) ? this.user_details.email : ""
                    }
                    this.loadVideos()
                }
            })
        },
        loadVideos() {
            Video.getUserVideos(this.user_details.pseudo, 1, 3).then(response => {
                if ("error" in response && response.error == false) {
                    this.videos = response.data.data
                    this.pager = response.data.pager
                }
            })
        },
        loadNextVideoPage() {
            Video.getUserVideos(this.user_details.pseudo, this.pager.current + 1, 3).then(response => {
                if ("error" in response && response.error == false) {
                    this.videos = response.data.data
                    this.pager = response.data.pager
                }
            })
        },
        loadPreviousVideoPage() {
            Video.getUserVideos(this.user_details.pseudo, this.pager.current - 1, 3).then(response => {
                if ("error" in response && response.error == false) {
                    this.videos = response.data.data
                    this.pager = response.data.pager
                }
            })
        }
    }
}
</script>