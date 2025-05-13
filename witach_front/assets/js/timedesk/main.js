
// получаем группы с сервера
const select_id_group = document.getElementById('id_group')

fetch(`${API_URL}/groups`, {
    'method': "GET"
})
    .then(data => data.json())
    .then(data => {
        console.log(data)
        data.groups.forEach(group => {
            select_id_group.innerHTML += `
            <option value="${group.id}">${group.name}</option>
            `
        });
    })
    .catch(err => console.error(err))

// получаем занятия с сервера
const select_id_lesson = document.getElementById('id_lesson')

fetch(`${API_URL}/lessons`, {
    'method': "GET"
})
    .then(data => data.json())
    .then(data => {
        console.log(data)
        data.lessons.forEach(lesson => {
            select_id_lesson.innerHTML += `
            <option value="${lesson.id}">${lesson.name}</option>
            `
        });
    })
    .catch(err => console.error(err))

// получаем аудитории с сервера
const select_id_auditorium = document.getElementById('id_auditorium')

fetch(`${API_URL}/auditoriums`, {
    'method': "GET"
})
    .then(data => data.json())
    .then(data => {
        console.log(data)
        data.auditoriums.forEach(auditorium => {
            select_id_auditorium.innerHTML += `
            <option value="${auditorium.id}">${auditorium.number} Аудитория</option>
            `
        });
    })
    .catch(err => console.error(err))

// получаем учителей с сервера
const select_id_teacher = document.getElementById('id_teacher')

fetch(`${API_URL}/teachers`, {
    'method': "GET"
})
    .then(data => data.json())
    .then(data => {
        console.log(data)
        data.teachers.forEach(teacher => {
            select_id_teacher.innerHTML += `
            <option value="${teacher.id}">${teacher.full_name}</option>
            `
        });
    })
    .catch(err => console.error(err))


function add_timedesk() {
    const data = {
        "id_group": select_id_group.value,
        "id_lesson": select_id_lesson.value,
        "id_auditorium": select_id_auditorium.value,
        "id_teacher": select_id_teacher.value,
        "start_time": document.getElementById('start_time').value,
        "finish_time": document.getElementById('finish_time').value,
        "date_lesson": document.getElementById('date_lesson').value,
    }
    fetch(`${API_URL}/timedesk`, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json"
        }
    })
        .then(data => data.json())
        .then(data => {
            console.log(data)
            document.querySelector(".timedesk_create").reset()
            alert("Расписание изменено")
        })
        .catch(err => {
            console.error(err)
            alert("Не удалось изменить расписание")
        })
}
document.querySelector(".timedesk_create").onsubmit = function (event) {
    event.preventDefault() // отмена перезагрузки страницы
    add_timedesk()
}

