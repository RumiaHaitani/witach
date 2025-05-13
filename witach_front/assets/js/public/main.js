const API_URL = "http://127.0.0.1:5000"
const HOME_URL = "http://127.0.0.1:5500"

AOS.init();

const logout_button = document.getElementById("logout_button")

if (logout_button) {
    logout_button.onclick = function () {
        localStorage.clear()
        window.location.href = `${HOME_URL}/pages/login.html`
    }
}

function show_modal(id_modal) {
    const modal = document.getElementById(id_modal);
    if (modal) {
        modal.classList.toggle("active")
    }
}



