<style scoped>
    .simulate-video {
        height: 512px;
        width: 100%;
        background-color: gray;
    }
</style>

<template>
    <div>
        <NavBar :authenticated="this.authenticated"/>
        <div class="container">
                <div v-if="Object.keys(this.video).length == 0">
                    <div class="col-lg-12 mt-4">
                        <center>
                            <p>Looking for you video...</p>
                        </center>
                    </div>
                </div>

                <div v-if="Object.keys(this.video).length" class="row pb-4">
                    <div class="col-lg-8 mt-4">
                        <div v-if="this.video_url.length === 0" class="card simulate-video">
                        </div>
                        <video width="100%" v-if="this.video_url.length" controls autoplay>
                            <source :src="this.video_url" >
                            Your browser does not support the video tag.
                        </video>
                        <br/>
                        <div class="row">
                            <div class="col-lg-9 mt-4">
                                <h4><div v-html="this.video.name"></div></h4>
                                <p>Added the {{ this.video.created_at.substring(0, this.video.created_at.length-10) }}</p>
                                <p v-if="this.video.description.length">{{this.video.description}}</p>
                                <p v-if="this.video.description.length == 0"><i>No description</i></p>
                            </div>
                            <div class="col-lg-3 mt-4">
                                <div class="row">
                                    <div class="col-lg-12">
                                        <p>By <b>{{ this.video.user_pseudo }}</b></p>
                                        <p>{{ this.video.duration }} seconds</p>
                                    </div>
                                    <div class="col-lg-12" v-if="this.video.format">
                                        <hr/>
                                        <p>Available in</p>
                                        <ul>
                                            <li v-for="(_path, _format) in this.video.format" v-bind:key="_format">
                                                <span v-if="_format == video_format" class="badge badge-info">{{ _format }}p (current)</span>
                                                <a v-if="_format != video_format" :href="'/video?id=' + video_id + '&format=' + _format">{{ _format }}p</a>
                                            </li>
                                        </ul>
                                    </div>
                                    <div class="col-lg-12" v-if="!this.video.format">
                                        <div class="alert alert-warning">
                                            <p>Video is processing...</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div v-if="this.authenticated" class="col-lg-12 p-2">
                                <div class="form-group">
                                    <b-form-textarea
                                        id="textarea"
                                        v-model="comment"
                                        placeholder="Share your thoughts..."
                                        rows="3"
                                        max-rows="6"
                                        :disabled="this.comment_form_loading"
                                    ></b-form-textarea>
                                </div>
                                <div class="form-group">
                                    <button class="btn btn-primary" v-if="this.comment_form_loading == false" v-on:click="onComment()">Comment</button>
                                    <button class="btn btn-primary" v-if="this.comment_form_loading" disabled>Sending...</button>
                                </div>
                            </div>
                            <div v-if="this.authenticated === false" class="col-lg-12">
                                <a href="/auth/login">Log in to comment</a>
                            </div>
                            <div class="col-lg-12">
                                <hr/>
                                <h4>Comments</h4>
                                <div class="card card-body m-2" v-for="(comment, index) in this.comments" v-bind:key="index">
                                    <p><b>{{comment.user_pseudo}}</b> the <b>{{comment.created_at.substring(0, comment.created_at.length-10)}}</b></p>
                                    <p>{{comment.content}}</p>
                                </div>
                                <div v-if="this.comments.length" class="row mx-auto">
                                    <nav aria-label="...">
                                        <ul class="pagination">
                                            <li v-if="this.comments_pager.current == 1" class="page-item disabled">
                                                <button class="page-link" href="#">Previous</button>
                                            </li>
                                            <li v-if="this.comments_pager.current > 1" class="page-item">
                                                <button class="page-link" href="#" @click="loadPreviousCommentPage()">Previous</button>
                                            </li>
                                            <li class="page-item active">
                                                <div class="page-link" href="#">{{this.comments_pager.current}} <span class="sr-only">(current)</span></div>
                                            </li>
                                            <li v-if="this.comments_pager.current == this.comments_pager.total" class="page-item disabled">
                                                <button class="page-link" href="#">Next</button>
                                            </li>
                                            <li v-if="this.comments_pager.current < this.comments_pager.total" class="page-item">
                                                <button class="page-link" href="#" @click="loadNextCommentPage()">Next</button>
                                            </li>
                                        </ul>
                                    </nav>
                                </div>
                                <div v-if="this.comments.length == 0" class="alert alert-warning">
                                    <p>No comment yet !</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-4 mt-4">
                        <h5>More videos</h5>
                        <div v-for="video_s in this.videos_s" v-bind:key="video_s.id" class="col-lg-12 p-1">
                            <a :href="'video?id=' + video_s.id">
                                <div class="card" >
                                    <div class="card-body row">
                                        <div class="col-lg-3">
                                            <img src="~/assets/multimedia.png" width="100%"/>
                                        </div>
                                        <div class="col-lg-9">
                                            <h4><div v-html="video_s.name"></div></h4>
                                            <p>{{ video_s.duration }} seconds</p>
                                            <p>{{ video_s.created_at.substring(0, video.created_at.length-10).replace("T", " ") }}</p>
                                        </div>
                                    </div>
                                </div>
                            </a>
                        </div>
                    </div>
                </div>
                <notifications group="video" />
                <notifications group="comment" />
            </div>
        </div>
    </div>
</template>

<script>
import NavBar from '~/components/NavBar.vue'
import Session from '~/middleware/authentication.js'
import Video from '~/middleware/video.js'

export default {
    components: {
        NavBar
    },
    data () {
        return {
            authenticated: false,
            session: false,
            video_id: this.$route.query.id,
            video_format: this.$route.query.format,
            video_url: "",
            video: {},
            videos_s: [],
            comment: "", // User comment to write
            comment_form_loading: false,
            comments_pager: {},
            comments: []
        }
    },
    mounted() {
        this.session = Session.getSession()
        this.getVideoDetails()
        this.loadVideos()
        this.loadInitialComments()
        Session.checkAuthentication().then(isAuthenticated => {
            this.authenticated = isAuthenticated
        })
    },
    methods: {
        getVideoFormat(formats) {
            if (this.video_format) {
                if (formats.indexOf(this.video_format) >= 0) {
                    return this.video_format
                } else {
                    this.$notify({
                        type: 'error',
                        group: 'video',
                        title: 'Video format',
                        text: "Invalid video format"
                    })
                    this.$router.replace({ path: "/video?id=" + this.video_id + "&format=" + formats[0]})
                }
            }
            return formats[0]
        },
        onComment() {
            if (this.comment) {
                this.comment_form_loading = true
                Video.postVideoComment(
                    this.video_id,
                    this.comment,
                    this.session.token
                ).then((response) => {
                    if("error" in response && response.error == false) {
                        this.$notify({
                            type: 'success',
                            group: 'comment',
                            title: 'Video comment',
                            text: response.message
                        })
                        this.comment = ""
                    } else {
                        this.$notify({
                            type: 'error',
                            group: 'comment',
                            title: 'Video comment',
                            text: response.message
                        })
                    }
                }).then(() => {
                    this.loadInitialComments()
                    this.comment_form_loading = false
                })
            }
        },
        getVideoDetails() {
            if (this.video_id) {
                Video.getVideoById(this.video_id).then((response) => {
                    if("error" in response && response.error == false) {
                        this.video = response.data
                        this.video_format = this.getVideoFormat(Object.keys(this.video.format))
                        this.video_url = "http://localhost:9980/video/file/" + this.video_id + "?format=" + this.video_format
                        console.log(this.video_url)
                    } else {
                        this.$notify({
                            type: 'error',
                            group: 'video',
                            title: 'Video',
                            text: response.message
                        })
                    }
                })
            } else {
                this.$router.replace({ path: "/" })
            }
        },
        loadVideos() {
            Video.getVideos(1, 3).then(response => {
                if ("error" in response && response.error == false) {
                    this.videos_s = response.data.data
                }
            })
        },
        loadInitialComments() {
            Video.getVideoComments(this.video_id, 1, 5).then(response => {
                if ("error" in response && response.error == false) {
                    this.comments_pager = response.data.pager
                    this.comments = response.data.data
                }
            })
        },
        loadNextCommentPage() {
            Video.getVideoComments(this.video_id, this.comments_pager.current + 1, 5).then(response => {
                if ("error" in response && response.error == false) {
                    this.comments_pager = response.data.pager
                    this.comments = response.data.data
                }
            })
        },
        loadPreviousCommentPage() {
            Video.getVideoComments(this.video_id, this.comments_pager.current - 1, 5).then(response => {
                if ("error" in response && response.error == false) {
                    this.comments_pager = response.data.pager
                    this.comments = response.data.data
                }
            })
        }
    }
}
</script>

<style>
</style>
