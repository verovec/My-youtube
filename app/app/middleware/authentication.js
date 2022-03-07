import axios from 'axios'

class Session {

    static checkToken(session) {
        return axios
            .post('http://localhost:9980/auth/check', {}, {
                headers: { "X-Api-Auth-Token": session.token }
            })
            .then(response => {
                response = response.data
                if("error" in response && response.error == false) {
                    session.expires_at = response.data.expires_at
                    localStorage.setItem("session", JSON.stringify(session))
                    return true
                } else {
                    localStorage.removeItem("session")
                    console.log(response)
                    return false
                }
            })
            .catch(error => {
                console.log(error)
                return false
            })
    }

    static checkAuthentication() {
        const session_str = localStorage.getItem('session')
        var session = (session_str && session_str.length) ? JSON.parse(session_str) : false
        if (session && "token" in session) {
            return Session.checkToken(session)
        } else {
            return new Promise((resolve) => {resolve(false)})
        }
    }

    static getSession() {
        const session_str = localStorage.getItem('session')
        var session = (session_str && session_str.length) ? JSON.parse(session_str) : false
        return session
    }

    static performLogout() {
        const session_str = localStorage.getItem('session')
        var session = (session_str && session_str.length) ? JSON.parse(session_str) : false
        if (session && "token" in session) {
            localStorage.removeItem("session")
            return true
        }
        return false
    }

    static performLogin(username, password) {
        return axios
            .post('http://localhost:9980/auth', {
                    username: username,
                    password: password
                }, { headers: { "Content-Type": "application/json" } }
            )
            .then(response => {
                response = response.data
                if("error" in response && response.error == false)
                    localStorage.setItem('session', JSON.stringify({...response.data, ...{username: username}}))
                return response
            })
    }

}

export default Session