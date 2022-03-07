<template>
    <div>
        <NavBar :authenticated="this.authenticated" @onVideoQueryChanged="this.updateVideoQuery"/>
        <div class="container">
            <div class="row">
                <div class="col-lg-12 mt-4">
                    <div v-if="this.videos.length == 0">
                        <div class="alert alert-warning">
                            <p>We were not able to find any video :(</p>
                        </div>
                    </div>

                    <div v-if="this.videos.length" class="row pb-4">
                        <div v-for="video in this.videos" v-bind:key="video.id" class="col-lg-6 p-2">
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
            videos: [],
            pager: {}
        }
    },
    mounted() {
        this.updateVideoQuery()
        Session.checkAuthentication().then(isAuthenticated => {
            this.authenticated = isAuthenticated
        })
    },
    methods: {
        updateVideoQuery(new_query, force=false) {
            const query = 
                (force == false)
                    ? ("query" in this.$route.query) ? this.$route.query.query : new_query
                    : new_query
            if (query && query.length)
                this.searchVideos(query)
            else
                this.loadVideos()
        },
        searchVideos(query) {
            Video.getVideosByName(query, 1, 6).then(response => {
                if ("error" in response && response.error == false) {
                    this.videos = response.data.data
                    this.pager = response.data.pager
                } else {
                    this.videos = []
                    this.pager = {}
                }
            })
        },
        loadVideos() {
            Video.getVideos(1, 6).then(response => {
                if ("error" in response && response.error == false) {
                    this.videos = response.data.data
                    this.pager = response.data.pager
                }
            })
        },
        loadNextVideoPage() {
            Video.getVideos(this.pager.current + 1, 6).then(response => {
                if ("error" in response && response.error == false) {
                    this.videos = response.data.data
                    this.pager = response.data.pager
                }
            })
        },
        loadPreviousVideoPage() {
            Video.getVideos(this.pager.current - 1, 6).then(response => {
                if ("error" in response && response.error == false) {
                    this.videos = response.data.data
                    this.pager = response.data.pager
                }
            })
        }
    }
}
</script>

<style>
</style>
