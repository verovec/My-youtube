import axios from 'axios'

class User {

    static getUserDetails(ids, token) {
        return axios
            .get('http://localhost:9980/user/' + ids, {
                headers: {
                    "X-Api-Auth-Token": token
                }
            })
            .then(response => {
                response = response.data
                return ("error" in response && response.error == false) ? response.data : false
            })
            .catch(error => {
                console.log(error)
                return false
            })
    }

    static updateUserDetails(ids, token, details) {
        return axios
            .put('http://localhost:9980/user/' + ids, details, {
                headers: {
                    "X-Api-Auth-Token": token
                }
            })
            .then(response => {
                return response.data
            })
            .catch(error => {
                console.log(error)
                return {
                    error: true,
                    message: "An error occured"
                }
            })
    }

    static registerUser(details) {
        return axios
            .post('http://localhost:9980/user', details)
            .then(response => {
                return response.data
            })
            .catch(error => {
                console.log(error)
                return {
                    error: true,
                    message: "An error occured"
                }
            })
    }

}

export default User