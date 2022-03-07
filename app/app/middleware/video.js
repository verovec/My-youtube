import axios from 'axios'

class Video {

    static getUserVideos(pseudo, page, per_page) {
        return axios
            .get('http://localhost:9980/videos', {
                params: {
                    pseudo: pseudo,
                    page: page,
                    per_page: per_page
                }
            }).then(response => response.data)
            .catch(error => {
                console.log(error)
                return {
                    error: true,
                    message: "An error occured"
                }
            })
    }

    static getVideosByName(name, page, per_page) {
        return axios
            .get('http://localhost:9980/videos/' + encodeURI(name), {
                params: {
                    page: page,
                    per_page: per_page
                }
            }).then(response => response.data)
            .catch(error => {
                console.log(error)
                return {
                    error: true,
                    message: "An error occured"
                }
            })
    }

    static getVideos(page, per_page) {
        return axios
            .get('http://localhost:9980/videos', {
                params: {
                    page: page,
                    per_page: per_page
                }
            }).then(response => response.data)
            .catch(error => {
                console.log(error)
                return {
                    error: true,
                    message: "An error occured"
                }
            })
    }

    static getVideoById(video_id) {
        return axios
            .get('http://localhost:9980/video/' + video_id)
            .then(response => response.data)
            .catch(error => {
                console.log(error)
                return {
                    error: true,
                    message: "An error occured"
                }
            })
    }

    static uploadVideo(name, description, file, token) {
        let formData = new FormData()
        formData.append('file', file)
        formData.append('name', name)
        formData.append('description', description)
        return axios
            .post('http://localhost:9980/videos',
                formData,
                {
                    params: {
                        name: name,
                        description: description
                    },
                    headers: {
                        "X-Api-Auth-Token": token,
                        'Content-Type': 'multipart/form-data'
                    }
                }
            ).then(response => response.data)
            .catch(error => {
                console.log(error)
                return {
                    error: true,
                    message: "An error occured"
                }
            })
    }

    static getVideoComments(video_id, page, per_page) {
        return axios
            .get('http://localhost:9980/videos/' + video_id + "/comment", {
                params: {
                    page: page,
                    per_page: per_page
                }
            })
            .then(response => response.data)
            .catch(error => {
                console.log(error)
                return {
                    error: true,
                    message: "An error occured"
                }
            })
    }

    static postVideoComment(video_id, comment, token) {
        return axios
            .post('http://localhost:9980/videos/' + video_id + "/comment", {}, {
                params: {
                    content: comment
                },
                headers: {
                    "X-Api-Auth-Token": token
                }
            })
            .then(response => response.data)
            .catch(error => {
                console.log(error)
                return {
                    error: true,
                    message: "An error occured"
                }
            })
    }

}

export default Video