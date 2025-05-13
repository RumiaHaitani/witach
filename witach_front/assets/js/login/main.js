const registration_form = document.getElementById("registration_form")
const login_form = document.getElementById("login_form")

registration_form.addEventListener("submit", function (event) {
    event.preventDefault() // отмена перезагрузки страницы
    const full_name = document.getElementById("full_name").value.trim();
    const id_group = document.getElementById("id_group").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const password = document.getElementById("password").value.trim();
    const data = { full_name, id_group, phone, password }
    fetch(`${API_URL}/registration`, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json"
        }
    })
        .then(data => data.json())
        .then(data => {
            console.log(data)
            alert("Вы зарегестрированы")
            registration_form.reset()
        })
        .catch(errors => {
            console.error(errors)
            alert("Не удалось зарегестрироваться")
        })
})

login_form.addEventListener("submit", function (event) {
    event.preventDefault() // не перезагружай страницу
    // получаем данные для входа
    const login = document.getElementById("login_user").value.trim()
    const password = document.getElementById("password_user").value.trim()
    // упаковываем в объект
    const data = { login, password }

    fetch(`${API_URL}/login`, {
        method: "POST",
        body: JSON.stringify(data),
        credentials:"same-origin",
        headers: {
            "Content-Type": "application/json"
        }
    })
        .then(data => {
            if (!data.ok) {
                throw new Error("Не удалось авторизоваться");
            }
            return data.json()
        })
        .then(data => {
            console.log(data)
            alert("Вы авторизованы")
            // редирект на страницу пользователей
            localStorage.setItem("id", data.user.id)
            window.location.href = `${HOME_URL}/pages/user-navigate.html`
        })
        .catch(errors => {
            console.error(errors)
            alert("Не удалось авторизоваться")
        })
})





