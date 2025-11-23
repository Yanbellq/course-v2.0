const username = document.getElementById('username')
const email = document.getElementById('email')

const data_session = JSON.parse(sessionStorage.getItem('user'))
const data_local = JSON.parse(localStorage.getItem('user'))
if (data_session) {
    username.value = data_session.user.username
    email.value = data_session.user.email
} else if (data_local) {
    username.value = data_local.user.username
    email.value = data_local.user.email
}//# sourceMappingURL=profile.js.map
