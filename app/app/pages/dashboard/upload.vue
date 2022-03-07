<template>
    <div>
        <NavBar :authenticated="this.authenticated"/>
        <div v-if="this.authenticated == true" class="container">
            <div class="row">
                <div class="col-lg-12">
                    <div class="jumbotron">
                        <h1 class="display-4">Start sharing, {{this.user_details.pseudo}} !</h1>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="offset-lg-2 col-lg-8" v-if="upload.success == false">
                    <div class="form-group">
                        <label for="video_name">Video name</label>
                        <input type="text" class="form-control" id="video_name" v-model="video.name" aria-describedby="video_name" placeholder="My great video..." :disabled="form_loading" required>
                    </div>
                    <div class="form-group">
                        <b-form-file
                            v-model="video.file"
                            :state="Boolean(video.file)"
                            placeholder="Choose a video or drop it here..."
                            drop-placeholder="Drop video here..."
                            accept=".mp4,.mov,.avi"
                            size="lg"
                            :disabled="form_loading"
                            required
                        ></b-form-file>
                    </div>
                    <div class="form-group">
                        <b-form-textarea
                            id="textarea"
                            v-model="video.description"
                            placeholder="Write some description..."
                            rows="3"
                            max-rows="6"
                            :disabled="form_loading"
                        ></b-form-textarea>
                    </div>
                    <div class="form-group">
                        <div class="mt-3" v-if="video.file"><b>Video to be uploaded : {{ video.file ? video.file.name : '' }}</b></div>
                        <br/>
                        <button class="btn btn-primary" v-if="form_loading == false" v-on:click="onVideoUpload()">Upload video</button>
                        <button class="btn btn-primary" v-if="form_loading" disabled>Please wait...</button>
                    </div>
                </div>
                <div class="offset-lg-2 col-lg-8" v-if="upload.success">
                    <div class="jumbotron">
                        <center>
                            <v-icon name="check-circle"></v-icon>
                            <br/>
                            <h4 class="display-4">Congrats on uploading<br/><b>"{{video.name}}"</b></h4>
                            <p>You will receive an email when your video is ready.</p>
                            <p v-if="upload.video_id">
                                <a :href="'/video?id=' + this.upload.video_id">It will be available here soon</a>
                            </p>
                            <button class="btn btn-info" v-on:click="redirectToDashboard()">Go back to dashboard</button>
                        </center>
                    </div>
                </div>
            </div>
        </div>
        <notifications group="auth" />
        <notifications group="upload" />
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
            form_loading: false,
            video: {
                name: "",
                description: "",
                file: null
            },
            upload: {
                success: false,
                video_id: null
            }
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
        onVideoUpload() {
            this.form_loading = true
            let do_upload = true
            if (!this.video.file) {
                this.$notify({
                    type: 'error',
                    group: 'upload',
                    title: 'Video upload',
                    text: "Please select a video"
                })
                do_upload = false
            } 
            if (this.video.name.length == 0) {
                this.$notify({
                    type: 'error',
                    group: 'upload',
                    title: 'Video upload',
                    text: "Please fill a video name"
                })
                do_upload = false
            }
            if (do_upload)
                Video.uploadVideo(
                    this.video.name,
                    this.video.description,
                    this.video.file,
                    this.session.token
                ).then((response) => {
                    if("error" in response && response.error == false) {
                        this.$notify({
                            type: 'success',
                            group: 'upload',
                            title: 'Video upload',
                            text: response.message
                        })
                        this.upload.success = true
                        this.upload.video_id = response.data.id
                    } else {
                        this.$notify({
                            type: 'error',
                            group: 'upload',
                            title: 'Video upload',
                            text: response.message
                        })
                    }
                    this.form_loading = false
                })
            this.form_loading = false
        },
        redirectToDashboard() {
            this.$router.replace({ path: "/dashboard" })
        },
        updateUserDetails() {
            User.getUserDetails(this.session.id, this.session.token).then(user_details => {
                if (user_details != false) {
                    this.user_details = user_details
                }
            })
        }
    }
}
</script>