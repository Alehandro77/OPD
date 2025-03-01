
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import datetime  # Импортируем модуль datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'важный_секретный_ключ'  # Замените на что-то случайное!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Используем SQLite
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Инициализация Flask-Migrate

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Указываем имя функции для входа!


# Модель User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    profile = db.relationship('UserProfile', backref='user', uselist=False)  # Связь с UserProfile (один к одному)

    def __repr__(self):
        return f'<User {self.username}>'


# Модель UserProfile
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)  # Вес может быть дробным числом
    wake_up_time_monday_hours = db.Column(db.Integer)  # Время пробуждения в понедельник
    wake_up_time_monday_minutes = db.Column(db.Integer)
    wake_up_time_tuesday_hours = db.Column(db.Integer)
    wake_up_time_tuesday_minutes = db.Column(db.Integer)
    wake_up_time_wednesday_hours = db.Column(db.Integer)
    wake_up_time_wednesday_minutes = db.Column(db.Integer)
    wake_up_time_thursday_hours = db.Column(db.Integer)
    wake_up_time_thursday_minutes = db.Column(db.Integer)
    wake_up_time_friday_hours = db.Column(db.Integer)
    wake_up_time_friday_minutes = db.Column(db.Integer)
    wake_up_time_saturday_hours = db.Column(db.Integer)
    wake_up_time_saturday_minutes = db.Column(db.Integer)
    wake_up_time_sunday_hours = db.Column(db.Integer)
    wake_up_time_sunday_minutes = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)  # Foreign Key
    recommendations = db.relationship('Recommendations', backref='user_profile',
                                       uselist=False)  # Связь с Recommendations (один к одному)


# Модель Recommendations
class Recommendations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bedtime = db.Column(db.Integer)  # Время отхода ко сну
    # TODO: Добавить другие рекомендации (время разминки, приема пищи и т.д.)
    user_profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), unique=True,
                                 nullable=False)  # Foreign Key


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def calculate_recommendations(age, weight, wake_up_time_hours, wake_up_time_minutes):
    """
    Функция для расчета рекомендаций на основе данных пользователя.
    TODO: Реализовать более сложную логику.
    """
    # Простая логика: рекомендуем ложиться спать за 8 часов до времени пробуждения
    bedtime_hours = (wake_up_time_hours - 8) % 24
    # TODO: учесть минуты при расчете времени отхода ко сну
    return {"bedtime": bedtime_hours}


def get_wake_up_time_for_today(profile):
    """
    Определяет завтрашний день недели и возвращает время пробуждения для этого дня.
    """
    if not profile:
        return 0, 0  # Возвращаем значения по умолчанию, если профиль не существует

    today = datetime.datetime.now().weekday()  # 0 - понедельник, 6 - воскресенье
    tomorrow = (today + 1) % 7  # Получаем день недели, следующий за текущим

    if tomorrow == 0:
        return profile.wake_up_time_monday_hours, profile.wake_up_time_monday_minutes
    elif tomorrow == 1:
        return profile.wake_up_time_tuesday_hours, profile.wake_up_time_tuesday_minutes
    elif tomorrow == 2:
        return profile.wake_up_time_wednesday_hours, profile.wake_up_time_wednesday_minutes
    elif tomorrow == 3:
        return profile.wake_up_time_thursday_hours, profile.wake_up_time_thursday_minutes
    elif tomorrow == 4:
        return profile.wake_up_time_friday_hours, profile.wake_up_time_friday_minutes
    elif tomorrow == 5:
        return profile.wake_up_time_saturday_hours, profile.wake_up_time_saturday_minutes
    else:
        return profile.wake_up_time_sunday_hours, profile.wake_up_time_sunday_minutes


# Маршрут для профиля пользователя
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = current_user.profile  # Получаем профиль пользователя
    errors = {}  # Создаем словарь для хранения ошибок

    if request.method == 'POST':
        age = request.form['age']
        weight = request.form['weight']
        wake_up_time_monday_hours = request.form['wake_up_time_monday_hours']
        wake_up_time_monday_minutes = request.form['wake_up_time_monday_minutes']
        wake_up_time_tuesday_hours = request.form['wake_up_time_tuesday_hours']
        wake_up_time_tuesday_minutes = request.form['wake_up_time_tuesday_minutes']
        wake_up_time_wednesday_hours = request.form['wake_up_time_wednesday_hours']
        wake_up_time_wednesday_minutes = request.form['wake_up_time_wednesday_minutes']
        wake_up_time_thursday_hours = request.form['wake_up_time_thursday_hours']
        wake_up_time_thursday_minutes = request.form['wake_up_time_thursday_minutes']
        wake_up_time_friday_hours = request.form['wake_up_time_friday_hours']
        wake_up_time_friday_minutes = request.form['wake_up_time_friday_minutes']
        wake_up_time_saturday_hours = request.form['wake_up_time_saturday_hours']
        wake_up_time_saturday_minutes = request.form['wake_up_time_saturday_minutes']
        wake_up_time_sunday_hours = request.form['wake_up_time_sunday_hours']
        wake_up_time_sunday_minutes = request.form['wake_up_time_sunday_minutes']

        # Валидация данных на стороне сервера
        try:
            age = int(age)
            if age <= 0:
                errors['age'] = "Возраст должен быть положительным числом."
        except ValueError:
            errors['age'] = "Возраст должен быть числом."

        try:
            weight = float(weight)
            if weight <= 0:
                errors['weight'] = "Вес должен быть положительным числом."
        except ValueError:
            errors['weight'] = "Вес должен быть числом."

        def validate_wake_up_time(hours, minutes):
            try:
                hours = int(hours)
                minutes = int(minutes)
                if hours < 0 or hours > 23:
                    return "Время подъема (часы) должно быть числом от 0 до 23."
                if minutes < 0 or minutes > 59:
                    return "Время подъема (минуты) должно быть числом от 0 до 59."
                return None
            except ValueError:
                return "Время подъема должно быть числом."

        error_monday = validate_wake_up_time(wake_up_time_monday_hours, wake_up_time_monday_minutes)
        if error_monday:
            errors['wake_up_time_monday'] = error_monday
        error_tuesday = validate_wake_up_time(wake_up_time_tuesday_hours, wake_up_time_tuesday_minutes)
        if error_tuesday:
            errors['wake_up_time_tuesday'] = error_tuesday
        error_wednesday = validate_wake_up_time(wake_up_time_wednesday_hours, wake_up_time_wednesday_minutes)
        if error_wednesday:
            errors['wake_up_time_wednesday'] = error_wednesday
        error_thursday = validate_wake_up_time(wake_up_time_thursday_hours, wake_up_time_thursday_minutes)
        if error_thursday:
            errors['wake_up_time_thursday'] = error_thursday
        error_friday = validate_wake_up_time(wake_up_time_friday_hours, wake_up_time_friday_minutes)
        if error_friday:
            errors['wake_up_time_friday'] = error_friday
        error_saturday = validate_wake_up_time(wake_up_time_saturday_hours, wake_up_time_saturday_minutes)
        if error_saturday:
            errors['wake_up_time_saturday'] = error_saturday
        error_sunday = validate_wake_up_time(wake_up_time_sunday_hours, wake_up_time_sunday_minutes)
        if error_sunday:
            errors['wake_up_time_sunday'] = error_sunday

        # Если есть ошибки, возвращаем их в виде JSON
        if errors:
            return jsonify({'errors': errors})

        # Если ошибок нет, сохраняем данные в базу данных
        try:
            age = int(age)
            weight = float(weight)
            wake_up_time_monday_hours = int(wake_up_time_monday_hours)
            wake_up_time_monday_minutes = int(wake_up_time_monday_minutes)
            wake_up_time_tuesday_hours = int(wake_up_time_tuesday_hours)
            wake_up_time_tuesday_minutes = int(wake_up_time_tuesday_minutes)
            wake_up_time_wednesday_hours = int(wake_up_time_wednesday_hours)
            wake_up_time_wednesday_minutes = int(wake_up_time_wednesday_minutes)
            wake_up_time_thursday_hours = int(wake_up_time_thursday_hours)
            wake_up_time_thursday_minutes = int(wake_up_time_thursday_minutes)
            wake_up_time_friday_hours = int(wake_up_time_friday_hours)
            wake_up_time_friday_minutes = int(wake_up_time_friday_minutes)
            wake_up_time_saturday_hours = int(wake_up_time_saturday_hours)
            wake_up_time_saturday_minutes = int(wake_up_time_saturday_minutes)
            wake_up_time_sunday_hours = int(wake_up_time_sunday_hours)
            wake_up_time_sunday_minutes = int(wake_up_time_sunday_minutes)
        except ValueError as e:
            print(f"Ошибка преобразования типов: {e}")
            errors['conversion'] = "Ошибка преобразования типов данных."
            return jsonify({'errors': errors})

        if profile:
            profile.age = age
            profile.weight = weight
            profile.wake_up_time_monday_hours = wake_up_time_monday_hours
            profile.wake_up_time_monday_minutes = wake_up_time_monday_minutes
            profile.wake_up_time_tuesday_hours = wake_up_time_tuesday_hours
            profile.wake_up_time_tuesday_minutes = wake_up_time_tuesday_minutes
            profile.wake_up_time_wednesday_hours = wake_up_time_wednesday_hours
            profile.wake_up_time_wednesday_minutes = wake_up_time_wednesday_minutes
            profile.wake_up_time_thursday_hours = wake_up_time_thursday_hours
            profile.wake_up_time_thursday_minutes = wake_up_time_thursday_minutes
            profile.wake_up_time_friday_hours = wake_up_time_friday_hours
            profile.wake_up_time_friday_minutes = wake_up_time_friday_minutes
            profile.wake_up_time_saturday_hours = wake_up_time_saturday_hours
            profile.wake_up_time_saturday_minutes = wake_up_time_saturday_minutes
            profile.wake_up_time_sunday_hours = wake_up_time_sunday_hours
            profile.wake_up_time_sunday_minutes = wake_up_time_sunday_minutes
        else:  # Создаем новый профиль
            profile = UserProfile(
                age=age,
                weight=weight,
                wake_up_time_monday_hours=wake_up_time_monday_hours,
                wake_up_time_monday_minutes=wake_up_time_monday_minutes,
                wake_up_time_tuesday_hours=wake_up_time_tuesday_hours,
                wake_up_time_tuesday_minutes=wake_up_time_tuesday_minutes,
                wake_up_time_wednesday_hours=wake_up_time_wednesday_hours,
                wake_up_time_wednesday_minutes=wake_up_time_wednesday_minutes,
                wake_up_time_thursday_hours=wake_up_time_thursday_hours,
                wake_up_time_thursday_minutes=wake_up_time_thursday_minutes,
                wake_up_time_friday_hours=wake_up_time_friday_hours,
                wake_up_time_friday_minutes=wake_up_time_friday_minutes,
                wake_up_time_saturday_hours=wake_up_time_saturday_hours,
                wake_up_time_saturday_minutes=wake_up_time_saturday_minutes,
                wake_up_time_sunday_hours=wake_up_time_sunday_hours,
                wake_up_time_sunday_minutes=wake_up_time_sunday_minutes,
                user_id=current_user.id
            )  # Связываем с пользователем
            db.session.add(profile)

        db.session.commit()

        # Рассчитываем рекомендации
        wake_up_time_hours, wake_up_time_minutes = get_wake_up_time_for_today(
            profile)  # Получаем время пробуждения для текущего дня
        recommendations_data = calculate_recommendations(age, weight, wake_up_time_hours, wake_up_time_minutes)

        # Сохраняем рекомендации в базе данных
        if profile.recommendations:
            recommendations = profile.recommendations
            recommendations.bedtime = recommendations_data['bedtime']
        else:
            recommendations = Recommendations(bedtime=recommendations_data['bedtime'], user_profile_id=profile.id)
            db.session.add(recommendations)

        db.session.commit()

        # Возвращаем JSON с рекомендациями
        return jsonify(recommendations_data)

    else:  # Если это GET запрос, отображаем форму с данными профиля
        if profile:
            return render_template('profile.html', profile=profile)
        else:
            return render_template('profile.html')


# Маршрут регистрации
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)  # Используем bcrypt по умолчанию
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


# Маршрут входа
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        return 'Неверные имя пользователя или пароль'  # TODO: Вывести сообщение об ошибке на страницу
    return render_template('login.html')


# Маршрут выхода
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Главная страница
@app.route('/')
@login_required
def index():
    profile = current_user.profile
    recommendations = None

    if profile and profile.recommendations:
        recommendations = current_user.profile.recommendations
    else:
        if profile: # Проверяем, что profile не None
            wake_up_time_hours, wake_up_time_minutes = get_wake_up_time_for_today(
                profile)  # Получаем время пробуждения для текущего дня
            recommendations_data = calculate_recommendations(profile.age, profile.weight, wake_up_time_hours,
                                                             wake_up_time_minutes)
            if profile:
                recommendations = Recommendations(bedtime=recommendations_data['bedtime'], user_profile_id=profile.id)
                db.session.add(recommendations)
                db.session.commit()
            else:
                recommendations_data = {"bedtime": 0}
            recommendations = profile.recommendations
        else:
            recommendations_data = {"bedtime": 0} # Значения по умолчанию
            recommendations = None

    return render_template('index.html', recommendations=recommendations)

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Создаем таблицы (если их еще нет)
    app.run(debug=True)
