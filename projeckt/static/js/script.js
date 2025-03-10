document.addEventListener('DOMContentLoaded', function() { // Ensure DOM is fully loaded  
    // Добавляем обработчик события submit для формы профиля
    const profileForm = document.querySelector('form[data-profile-url]');
    if (profileForm) {
        const profileUrl = profileForm.dataset.profileUrl; // Получаем URL из атрибута data-*
        profileForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Предотвращаем отправку формы по умолчанию

            // Собираем данные из формы
            const formData = new FormData(this);

            // Отправляем данные на сервер с помощью Fetch API
            fetch(profileUrl, { // Используем полученный URL
                method: 'POST',
                body: formData
            })
            .then(response => response.json()) // Преобразуем ответ в JSON
            .then(data => {
                // Обновляем рекомендации на странице (если находимся на главной странице)
                if (document.getElementById("recommendations")) {
                    updateRecommendations(data.bedtime);
                }
                // Перенаправляем пользователя обратно на страницу профиля
                window.location.href = profileUrl;

            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при обновлении рекомендаций.');
            });
        });
    } else {
        console.warn("Форма профиля не найдена на странице.");
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
    const heightInput = document.getElementById('height');

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

    if (heightInput) {
        heightInput.addEventListener('input', function() {
            validateNumber(this, 'height-error', 'Рост должен быть числом.');
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
