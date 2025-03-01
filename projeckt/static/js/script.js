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
                    // Очищаем предыдущие ошибки
                    formErrors.innerHTML = '';

                    // Выводим новые ошибки
                    for (const key in data.errors) {
                        const error = document.createElement('p');
                        error.textContent = data.errors[key];
                        formErrors.appendChild(error);
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
            if (target.classList.contains('time-value')) {
                const action = target.dataset.action;
                const targetInput = target.dataset.target;
                const inputElement = document.getElementById(targetInput);
                const displayElement = document.getElementById(targetInput + '_display');

                if (inputElement && displayElement) {
                    let currentValue = parseInt(inputElement.value);
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
});
