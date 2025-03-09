document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const formErrors = document.getElementById('form-errors');
    // Добавляем проверку, существует ли форма на странице
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Предотвратить стандартную отправку формы

            const formData = new FormData(form); // Получить данные с формы как FormData
            //const profileUrl = formData.get('profileUrl'); // Извлечь profileUrl из FormData  УДАЛИТЬ ЭТУ СТРОКУ

            //fetch(profileUrl, { // Отправляем данные на URL profileUrl УДАЛИТЬ ЭТУ СТРОКУ
            fetch('/profile', { // Отправляем данные на URL profile ИЗМЕНИТЬ ЭТУ СТРОКУ
                method: 'POST',
                body: formData
            })
            .then(response => response.json()) // Преобразуем ответ в json
            .then(data => {
                if (data.errors) { // Если есть ошибки
                    // Выводим предыдущие ошибки под полями
                    const errorsDiv = document.querySelector(".error");
                    errorsDiv.textContent = "";

                    for (let key in data.errors) {
                        let errorSpan = document.getElementById(key + "-error");
                        if (errorSpan) {
                            errorSpan.textContent = data.errors[key];
                        } else {
                            // Если нет соответствующего элемента, выводим в общий блок
                            errorsDiv.textContent += data.errors[key] + " ";
                        }
                    }
                } else {
                    // Если ошибок нет, можно обновить страницу или показать сообщение об успехе
                    errorsForm.innerHTML = "<p>Данные успешно сохранены!</p>";
                }
            })
            .catch(error => {
                console.error('Ошибка при отправке запроса:', error);
                errorsForm.innerHTML = "<p>Ошибка при сохранении данных.</p>";
            });
        });
    }

    const timeSelectors = document.querySelectorAll('.time-selector');

    timeSelectors.forEach(selector => {
        selector.addEventListener('click', function(event) {
            const target = event.target;

            // Проверяем, является ли target элементом .time-value
            if (target.classList.contains('time-value')) {
                const action = target.dataset.action;
                const targetInput = target.dataset.target;
                const inputElement = document.getElementById(targetInput);
                const displayElement = document.getElementById(targetInput + '_display');

                if (inputElement && displayElement) {
                    let currentValue = parseInt(inputElement.value);

                    // Проверяем, является ли currentValue NaN
                    if (isNaN(currentValue)) {
                        currentValue = 0; // Устанавливаем значение по умолчанию
                    }

                    let maxValue = targetInput.includes('hours') ? 23 : 59;
                    let minValue = 0;

                    if (action === 'increment') {
                        currentValue = (currentValue + 1) > maxValue ? minValue : (currentValue + 1);
                    } else if (action === 'decrement') {
                        currentValue = (currentValue - 1) < minValue ? maxValue : (currentValue - 1);
                    }

                    inputElement.value = currentValue;
                    displayElement.textContent = String(currentValue).padStart(2, '0');
                }
            }
        });
    });

    // Добавляем обработчики событий для валидации в реальном времени
    const ageInput = document.getElementById('age');
    const weightInput = document.getElementById('weight');

    if (ageInput) {
        ageInput.addEventListener('input', function() {
            validateNumber(this, 'age-error', 'Возраст должен быть числом.');
        });
    }

    if (weightInput) {
        weightInput.addEventListener('input', function() {
            validateNumber(this, 'weight-error', 'Вес должен быть числом.');
        });
    }

    // Функция для валидации числовых полей
    function validateNumber(input, errorId, errorMessage) {
    const value = input.value;
    const errorSpan = document.getElementById(errorId);

    if (isNaN(value)) {
        errorSpan.textContent = errorMessage;
    } else {
        const numberValue = parseFloat(value);
        if (numberValue < 0) {
            errorSpan.textContent = "Значение должно быть положительным.";
        } else {
            errorSpan.textContent = '';
        }
    }
}


});

document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('username');
    const usernameError = document.createElement('span');
    usernameError.classList.add('error');
    usernameInput.parentNode.appendChild(usernameError);

    usernameInput.addEventListener('input', function() {
        const username = this.value;

        // Отправляем AJAX запрос на сервер
        fetch('/check_username?username=' + username)
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    usernameError.textContent = 'Пользователь с таким логином уже существует.';
                } else {
                    usernameError.textContent = '';
                }
            });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');

    loginForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Предотвращаем отправку формы по умолчанию

        const formData = new FormData(loginForm); // Создаем объект FormData

        fetch('/login', { // Отправляем AJAX запрос на сервер
            method: 'POST',
            body: formData
        })
        .then(response => response.json()) // Преобразуем ответ в JSON
        .then(data => {
            if (data.success) { // Если вход успешен
                window.location.href = '/'; // Перенаправляем на главную страницу
            } else { // Если вход не успешен
                loginError.textContent = data.message; // Выводим сообщение об ошибке
            }
        });
    });
});
