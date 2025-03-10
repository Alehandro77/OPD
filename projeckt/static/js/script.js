document.addEventListener('DOMContentLoaded', function() {
    function saveProfile() {
        const form = document.getElementById('profileForm');
        const formData = new FormData(form);
    
        const gender = document.getElementById('gender').value;
        formData.append('gender', gender);
    
        fetch('/save_profile', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const errorMessagesElement = document.getElementById('error-messages'); // Получаем элемент для ошибок
    
            if (data.success) {
                // Очищаем ошибки, если сохранение успешно
                errorMessagesElement.innerHTML = '';
                alert('Профиль успешно сохранен!');
                window.location.reload();
            } else {
                // Обработка ошибок
                console.error('Ошибка сохранения профиля:', data);
                errorMessagesElement.innerHTML = ''; // Очищаем предыдущие ошибки
    
                if (data.errors) {
                    // Предполагаем, что data.errors - это объект, где ключи - имена полей, а значения - массивы ошибок
                    for (const field in data.errors) {
                        if (data.errors.hasOwnProperty(field)) {
                            const errors = data.errors[field];
                            errors.forEach(error => {
                                const errorElement = document.createElement('p');
                                errorElement.textContent = `${field}: ${error}`; // Добавляем имя поля к сообщению
                                errorMessagesElement.appendChild(errorElement);
                            });
                        }
                    }
                } else {
                    // Если нет информации об ошибках, выводим общее сообщение
                    errorMessagesElement.textContent = 'Произошла ошибка. Пожалуйста, попробуйте еще раз.';
                }
            }
        })
        .catch(error => {
            console.error('Ошибка при отправке запроса:', error);
            alert('Произошла ошибка при отправке запроса. Пожалуйста, попробуйте еще раз.');
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
