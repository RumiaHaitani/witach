const id = localStorage.getItem('id')

if (!id) {
    window.location.href = `${HOME_URL}/pages/login.html`
}

const profile = document.querySelector(".profile")

fetch(`${API_URL}/profile/${id}`, {
    method:"GET"
})
.then(data => data.json())
.then(data => {
    console.log(data)
    profile.innerHTML += `
        <h2>ФИО: ${data.student.full_name}</h2>
        <h2>Группа: ${data.student.group.name}</h2>
        <h2>Телефон: ${data.student.phone}</h2>
    `
})
.catch(errors => console.error(errors))


