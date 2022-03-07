<style scoped>
    .icon {
        width: 32px;
    }
</style>

<template>
    <nav class="navbar navbar-dark bg-dark justify-content-between">
        <nuxt-link to="/">
            <a class="navbar-brand">My YouTube</a>
        </nuxt-link>
        <div class="form-inline">
            <input class="form-control mr-sm-2" type="search" v-model="search" placeholder="Search video" aria-label="Search" @keyup.enter="redirectSearch()">
            <button class="btn btn-success my-2 my-sm-0" type="submit" @click="redirectSearch()">Search</button>
            <div v-if="authenticated === true">
                <nuxt-link to="/dashboard">
                    <button class="btn btn-info ml-2">My account</button>
                </nuxt-link>
                <nuxt-link to="/dashboard/upload" title="Upload a video">
                    <v-icon name="upload"></v-icon>
                </nuxt-link>
                <button class="btn btn-warning btn-sm ml-2" v-on:click="logout()">Logout</button>
            </div>
            <div v-else>
                <nuxt-link to="/auth/login">
                    <button class="btn btn-primary ml-2">Sign in</button>
                </nuxt-link>
                <nuxt-link to="/auth/register">
                    <button class="btn btn-info ml-2">Register</button>
                </nuxt-link>
            </div>
        </div>
        <notifications group="nav_auth" />
    </nav>
</template>

<script>
import Session from '~/middleware/authentication.js'

export default {
    props: ["authenticated", "user"],
    data() {
        return {
            search: ""
        }
    },
    mounted() {
        const query = this.$route.query.query
        if (query && query.length)
            this.search = query
    },
    methods: {
        redirectSearch() {
            this.$emit('onVideoQueryChanged', this.search, true)
            if (this.search.length)
                this.$router.replace({ path: "/", query: { query: this.search } })
            else
                if ("query" in this.$route.query)
                    this.$router.replace({ path: "/" })
        },
        logout() {
            if (Session.performLogout()) {
                this.$notify({
                    type: 'success',
                    group: 'nav_auth',
                    title: 'Logout',
                    text: "You've been successfuly logged out"
                })
            } else {
                this.$notify({
                    type: 'error',
                    group: 'nav_auth',
                    title: 'Logout',
                    text: "An error occured logging you out"
                })
            }
            this.$router.replace({ path: "/" })
        }
    }
}
</script>