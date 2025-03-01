document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const formErrors = document.getElementById('form-errors');

    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Предотвращаем стандартную отправку формы

            const formData = new FormData(form);
            const profileUrl = form.dataset.profileUrl;

            fetch(profileUrl, {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.errors) {
                    // Очищаем предыдущие ошибки под полями
                    const errorSpans = document.querySelectorAll('.error');
                    errorSpans.forEach(span => {
                        span.textContent = '';
                    });

                    // Выводим ошибки под соответствующими полями
                    for (const key in data.errors) {
                        const errorSpan = document.getElementById(key + '-error');
                        if (errorSpan) {
                            errorSpan.textContent = data.errors[key];
                        } else {
                            // Если нет соответствующего элемента, выводим в общую ошибку
                            const error = document.createElement('p');
                            error.textContent = data.errors[key];
                            formErrors.appendChild(error);
                        }
                    }
                } else {
                    // Если ошибок нет, можно обновить страницу или показать сообщение об успехе
                    formErrors.innerHTML = '<p>Данные успешно сохранены!</p>';
                }
            })
            .catch(error => {
                console.error('Ошибка при отправке запроса:', error);
                formErrors.innerHTML = '<p>Произошла ошибка при сохранении данных.</p>';
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
