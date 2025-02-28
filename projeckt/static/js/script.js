
document.addEventListener('DOMContentLoaded', function() { // Ensure DOM is fully loaded

    function updateRecommendations(bedtime) {
        const bedtimeElement = document.getElementById("bedtime");
        if (bedtimeElement) {
            bedtimeElement.textContent = bedtime + ":00"; // Добавляем ":00" для отображения времени
        } else {
            console.warn("Элемент с id 'bedtime' не найден на странице.");
        }
    }

    // Добавляем обработчик события submit для формы профиля
    const profileForm = document.querySelector('form[data-profile-url]');
    if (profileForm) {
        const profileUrl = profileForm.dataset.profileUrl; // Получаем URL из атрибута data-*

        // Функция для валидации одного поля
        function validateField(field, errorElementId, errorMessage) {
            const value = field.value;
            const isNumber = !isNaN(value);
            let isValid = true;

            if (field.id === "age" || field.id === "weight") {
                isValid = isNumber && parseFloat(value) > 0;
            } else if (field.id.startsWith("wake_up_time_")) {
                isValid = isNumber && parseInt(value) >= 0 && parseInt(value) <= 23;
            }

            document.getElementById(errorElementId).textContent = isValid ? "" : errorMessage;
            return isValid;
        }

        // Attach real-time validation to each field
        const fields = profileForm.querySelectorAll('input[type="number"]');
        fields.forEach(field => {
            field.addEventListener('input', function() {
                const fieldId = field.id;
                let errorElementId = fieldId + '-error';
                let errorMessage = '';

                if (fieldId === "age") {
                    errorMessage = "Возраст должен быть положительным числом.";
                } else if (fieldId === "weight") {
                    errorMessage = "Вес должен быть положительным числом.";
                } else if (fieldId.startsWith("wake_up_time_")) {
                    errorMessage = "Время подъема должно быть числом от 0 до 23.";
                }

                validateField(field, errorElementId, errorMessage);
            });
        });

        profileForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Предотвращаем отправку формы по умолчанию

            // Сбрасываем все сообщения об ошибках
            document.getElementById('form-errors').textContent = '';
            document.getElementById('age-error').textContent = '';
            document.getElementById('weight-error').textContent = '';
            document.getElementById('wake_up_time_monday-error').textContent = '';
            document.getElementById('wake_up_time_tuesday-error').textContent = '';
            document.getElementById('wake_up_time_wednesday-error').textContent = '';
            document.getElementById('wake_up_time_thursday-error').textContent = '';
            document.getElementById('wake_up_time_friday-error').textContent = '';
            document.getElementById('wake_up_time_saturday-error').textContent = '';
            document.getElementById('wake_up_time_sunday-error').textContent = '';

            let hasErrors = false;
            let errors = {};
            // Get values from form and validate here
            const ageField = document.getElementById("age");
            const weightField = document.getElementById("weight");
            const wakeUpTimeMondayField = document.getElementById("wake_up_time_monday");
            const wakeUpTimeTuesdayField = document.getElementById("wake_up_time_tuesday");
            const wakeUpTimeWednesdayField = document.getElementById("wake_up_time_wednesday");
            const wakeUpTimeThursdayField = document.getElementById("wake_up_time_thursday");
            const wakeUpTimeFridayField = document.getElementById("wake_up_time_friday");
            const wakeUpTimeSaturdayField = document.getElementById("wake_up_time_saturday");
            const wakeUpTimeSundayField = document.getElementById("wake_up_time_sunday");


            if (!validateField(ageField, 'age-error', "Возраст должен быть положительным числом.")) {
                hasErrors = true;
                errors.age = "Возраст должен быть положительным числом.";
            }
            if (!validateField(weightField, 'weight-error', "Вес должен быть положительным числом.")) {
                hasErrors = true;
                errors.weight = "Вес должен быть положительным числом.";
            }
            if (!validateField(wakeUpTimeMondayField, 'wake_up_time_monday-error', "Время подъема должно быть числом от 0 до 23.")) {
                hasErrors = true;
                errors.wake_up_time_monday = "Время подъема должно быть числом от 0 до 23.";
            }
                        if (!validateField(wakeUpTimeTuesdayField, 'wake_up_time_tuesday-error', "Время подъема должно быть числом от 0 до 23.")) {
                hasErrors = true;
                errors.wake_up_time_tuesday = "Время подъема должно быть числом от 0 до 23.";
            }
                        if (!validateField(wakeUpTimeWednesdayField, 'wake_up_time_wednesday-error', "Время подъема должно быть числом от 0 до 23.")) {
                hasErrors = true;
                errors.wake_up_time_wednesday = "Время подъема должно быть числом от 0 до 23.";
            }
                        if (!validateField(wakeUpTimeThursdayField, 'wake_up_time_thursday-error', "Время подъема должно быть числом от 0 до 23.")) {
                hasErrors = true;
                errors.wake_up_time_thursday = "Время подъема должно быть числом от 0 до 23.";
            }
                        if (!validateField(wakeUpTimeFridayField, 'wake_up_time_friday-error', "Время подъема должно быть числом от 0 до 23.")) {
                hasErrors = true;
                errors.wake_up_time_friday = "Время подъема должно быть числом от 0 до 23.";
            }
                        if (!validateField(wakeUpTimeSaturdayField, 'wake_up_time_saturday-error', "Время подъема должно быть числом от 0 до 23.")) {
                hasErrors = true;
                errors.wake_up_time_saturday = "Время подъема должно быть числом от 0 до 23.";
            }
             if (!validateField(wakeUpTimeSundayField, 'wake_up_time_sunday-error', "Время подъема должно быть числом от 0 до 23.")) {
                hasErrors = true;
                errors.wake_up_time_sunday = "Время подъема должно быть числом от 0 до 23.";
            }


            if (hasErrors) {
                let errorString = "Пожалуйста, исправьте следующие ошибки:\n";

                let ageAndWeightErrors = [];
                if (errors.age) ageAndWeightErrors.push(errors.age);
                if (errors.weight) ageAndWeightErrors.push(errors.weight);

                if (ageAndWeightErrors.length > 0) {
                    errorString += "Возраст и вес должны быть положительными числами.\n";
                }
                if (errors.wake_up_time_monday || errors.wake_up_time_tuesday || errors.wake_up_time_wednesday || errors.wake_up_time_thursday || errors.wake_up_time_friday || errors.wake_up_time_saturday || errors.wake_up_time_sunday)
                    errorString += "Время подъема должно быть числом от 0 до 23.\n";
                 document.getElementById('form-errors').textContent = errorString;
                return; // Stop form submission
            }


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
                const indexPage = document.getElementById("recommendations");
                if (indexPage) {
                    updateRecommendations(data.bedtime);
                }
                // Перенаправляем пользователя обратно на страницу профиля
                window.location.href = profileUrl;

            })
            .catch(error => {
                console.error('Ошибка:', error);
                document.getElementById('form-errors').textContent = 'Произошла ошибка при отправке запроса.';
            });
        });
    } else {
        console.warn("Форма профиля не найдена на странице.");
    }
});
