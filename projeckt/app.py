from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
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
login_manager.login_message = None  # Отключаем сообщение по умолчанию


# Модель User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    color = db.Column(db.String(20), nullable=False, default='green')
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
    bedtime_hours = db.Column(db.Integer)  # Время отхода ко сну часы
    bedtime_minytes = db.Column(db.Integer)  # Время отхода ко сну минуты
    not_hours = db.Column(db.Integer)  # Время без нагрузок в часах
    not_minytes = db.Column(db.Integer)  # Время без нагрузок в минутах
    breakfast_hours = db.Column(db.Integer)  # Начала завтрака в часах
    breakfast_minutes = db.Column(db.Integer)  # Начала завтрака в минутах
    breakfast_hours_up = db.Column(db.Integer)  # Конец завтрака в часах
    breakfast_minutes_up = db.Column(db.Integer)  # Конец завтрака в минутах
    lanch_hours = db.Column(db.Integer)  # Время начала обеда в часах 
    lanch_minutes = db.Column(db.Integer)  # Время обеда в минутах
    lanch_hours_up = db.Column(db.Integer)  # Время конца обеда в часах 
    diner = db.Column(db.Integer)  # Начало ужана
    diner_up = db.Column(db.Integer)  # Конец ужина
    user_profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), unique=True,
                                 nullable=False)  # Foreign Key


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def calculate_recommendations(age, weight, wake_up_time_hours, wake_up_time_minutes, wake_up_time_hours_2, wake_up_time_minutes_2):
    """
    Функция для расчета рекомендаций на основе данных пользователя.
    """
    # Лечь спать за 8 часолв до пробуждения
    bedtime_hours = (wake_up_time_hours - 8) % 24
    bedtime_minytes = wake_up_time_minutes // 10 * 10

    # Убрать телефон и убрать стресс
    not_hours = (bedtime_hours - 1) % 24
    not_minytes = bedtime_minytes // 10 * 10

    # Ужин
    diner = (bedtime_hours - 3) % 24
    diner_up = (bedtime_hours - 2) % 24

    #Завтрак
    breakfast_minutes = (wake_up_time_minutes_2 + 30) % 60 // 10 * 10
    breakfast_minutes_dop = (wake_up_time_minutes_2 + 30) // 60
    breakfast_hours = wake_up_time_hours_2 + breakfast_minutes_dop
    breakfast_minutes_up = (breakfast_minutes + 20) % 60
    breakfast_minutes_dop_up = (breakfast_minutes + 20) // 60
    breakfast_hours_up = breakfast_hours + breakfast_minutes_dop_up

    # Обед
    lanch_time_d = (diner - 6) % 24
    lanch_time_b = (breakfast_hours_up + 6) % 24
    lanch_sr = (lanch_time_d + lanch_time_b) // 2
    lanch_hours = lanch_sr
    lanch_minutes = 0
    lanch_hours_up = lanch_sr + 1

    return {"bedtime_hours": bedtime_hours, "bedtime_minytes": bedtime_minytes, 
            "not_hours": not_hours, "not_minytes": not_minytes,
            "diner": diner, "diner_up": diner_up,
            "breakfast_minutes": breakfast_minutes, "breakfast_hours": breakfast_hours, 
            "breakfast_minutes_up": breakfast_minutes_up, "breakfast_hours_up": breakfast_hours_up,
            "lanch_hours": lanch_hours, "lanch_hours_up": lanch_hours_up, "lanch_minutes": lanch_minutes}

def get_wake_up_time_for_tomorrow(profile):
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


def get_wake_up_time_for_today(profile):
    """
    Определяет сегодняшний день недели и возвращает время пробуждения для этого дня.
    """
    if not profile:
        return 0, 0  # Возвращаем значения по умолчанию, если профиль не существует

    today = datetime.datetime.now().weekday()  # 0 - понедельник, 6 - воскресенье

    if today == 0:
        return profile.wake_up_time_monday_hours, profile.wake_up_time_monday_minutes
    elif today == 1:
        return profile.wake_up_time_tuesday_hours, profile.wake_up_time_tuesday_minutes
    elif today == 2:
        return profile.wake_up_time_wednesday_hours, profile.wake_up_time_wednesday_minutes
    elif today == 3:
        return profile.wake_up_time_thursday_hours, profile.wake_up_time_thursday_minutes
    elif today == 4:
        return profile.wake_up_time_friday_hours, profile.wake_up_time_friday_minutes
    elif today == 5:
        return profile.wake_up_time_saturday_hours, profile.wake_up_time_saturday_minutes
    else:
        return profile.wake_up_time_sunday_hours, profile.wake_up_time_sunday_minutes

# Маршрут для профиля пользователя
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(current_user.id)
    color = user.color
    profile = current_user.profile  # Получаем профиль пользователя
    errors = {}  # Создаем словарь для хранения ошибок

    if request.method == 'POST':
        try:
            age = int(request.form['age'])
            weight = float(request.form['weight'])

            wake_up_time_monday_hours = int(request.form['wake_up_time_monday_hours'])
            wake_up_time_monday_minutes = int(request.form['wake_up_time_monday_minutes'])
            wake_up_time_tuesday_hours = int(request.form['wake_up_time_tuesday_hours'])
            wake_up_time_tuesday_minutes = int(request.form['wake_up_time_tuesday_minutes'])
            wake_up_time_wednesday_hours = int(request.form['wake_up_time_wednesday_hours'])
            wake_up_time_wednesday_minutes = int(request.form['wake_up_time_wednesday_minutes'])
            wake_up_time_thursday_hours = int(request.form['wake_up_time_thursday_hours'])
            wake_up_time_thursday_minutes = int(request.form['wake_up_time_thursday_minutes'])
            wake_up_time_friday_hours = int(request.form['wake_up_time_friday_hours'])
            wake_up_time_friday_minutes = int(request.form['wake_up_time_friday_minutes'])
            wake_up_time_saturday_hours = int(request.form['wake_up_time_saturday_hours'])
            wake_up_time_saturday_minutes = int(request.form['wake_up_time_saturday_minutes'])
            wake_up_time_sunday_hours = int(request.form['wake_up_time_sunday_hours'])
            wake_up_time_sunday_minutes = int(request.form['wake_up_time_sunday_minutes'])

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
                    wake_up_time_monday_hours=int(wake_up_time_monday_hours),  # Преобразуем в int
                    wake_up_time_monday_minutes=int(wake_up_time_monday_minutes),  # Преобразуем в int
                    wake_up_time_tuesday_hours=int(wake_up_time_tuesday_hours),  # Преобразуем в int
                    wake_up_time_tuesday_minutes=int(wake_up_time_tuesday_minutes),  # Преобразуем в int
                    wake_up_time_wednesday_hours=int(wake_up_time_wednesday_hours),  # Преобразуем в int
                    wake_up_time_wednesday_minutes=int(wake_up_time_wednesday_minutes),  # Преобразуем в int
                    wake_up_time_thursday_hours=int(wake_up_time_thursday_hours),  # Преобразуем в int
                    wake_up_time_thursday_minutes=int(wake_up_time_thursday_minutes),  # Преобразуем в int
                    wake_up_time_friday_hours=int(wake_up_time_friday_hours),  # Преобразуем в int
                    wake_up_time_friday_minutes=int(wake_up_time_friday_minutes),  # Преобразуем в int
                    wake_up_time_saturday_hours=int(wake_up_time_saturday_hours),  # Преобразуем в int
                    wake_up_time_saturday_minutes=int(wake_up_time_saturday_minutes),  # Преобразуем в int
                    wake_up_time_sunday_hours=int(wake_up_time_sunday_hours),  # Преобразуем в int
                    wake_up_time_sunday_minutes=int(wake_up_time_sunday_minutes),  # Преобразуем в int
                    user_id=current_user.id
                )  # Связываем с пользователем
                db.session.add(profile)


            db.session.commit()

            # Рассчитываем рекомендации
            wake_up_time_hours, wake_up_time_minutes = get_wake_up_time_for_tomorrow(
                profile)  # Получаем время пробуждения для текущего дня
            wake_up_time_hours_2, wake_up_time_minutes_2 = get_wake_up_time_for_today(
                profile)  # Получаем время пробуждения для текущего дня
            recommendations_data = calculate_recommendations(age, weight, wake_up_time_hours, wake_up_time_minutes, wake_up_time_hours_2, wake_up_time_minutes_2)

            # Сохраняем рекомендации в базе данных
            if profile.recommendations:
                recommendations = profile.recommendations
                recommendations.bedtime_hours = recommendations_data['bedtime_hours']
                recommendations.bedtime_minytes = recommendations_data['bedtime_minytes']
                recommendations.not_hours = recommendations_data['not_hours']
                recommendations.not_minytes = recommendations_data['not_minytes']
                recommendations.breakfast_hours = recommendations_data['breakfast_hours']
                recommendations.breakfast_minutes = recommendations_data['breakfast_minutes']
                recommendations.breakfast_hours_up = recommendations_data['breakfast_hours_up']
                recommendations.breakfast_minutes_up = recommendations_data['breakfast_minutes_up']
                recommendations.lanch_hours = recommendations_data['lanch_hours']
                recommendations.lanch_minutes = recommendations_data['lanch_minutes']
                recommendations.lanch_hours_up = recommendations_data['lanch_hours_up']
                recommendations.diner = recommendations_data['diner']
                recommendations.diner_up = recommendations_data['diner_up']
            else:
                recommendation_bedtime_hours = Recommendations(bedtime_hours=recommendations_data['bedtime_hours'], user_profile_id=profile.id)
                recommendation_bedtime_minytes = Recommendations(bedtime_minytes=recommendations_data['bedtime_minytes'], user_profile_id=profile.id)
                recommendation_not_hours = Recommendations(not_hours=recommendations_data['not_hours'], user_profile_id=profile.id)
                recommendation_not_minytes = Recommendations(not_minytes=recommendations_data['not_minytes'], user_profile_id=profile.id)
                recommendation_breakfast_hours = Recommendations(breakfast_hours=recommendations_data['breakfast_hours'], user_profile_id=profile.id)
                recommendation_breakfast_minutes = Recommendations(breakfast_minutes=recommendations_data['breakfast_minutes'], user_profile_id=profile.id)
                recommendation_breakfast_hours_up = Recommendations(breakfast_hours_up=recommendations_data['breakfast_hours_up'], user_profile_id=profile.id)
                recommendation_breakfast_minutes_up = Recommendations(breakfast_minutes_up=recommendations_data['breakfast_minutes_up'], user_profile_id=profile.id)
                recommendation_lanch_hours = Recommendations(lanch_hours=recommendations_data['lanch_hours'], user_profile_id=profile.id)
                recommendation_lanch_minutes = Recommendations(lanch_minutes=recommendations_data['lanch_minutes'], user_profile_id=profile.id)
                recommendation_lanch_hours_up = Recommendations(lanch_hours_up=recommendations_data['lanch_hours_up'], user_profile_id=profile.id)
                recommendation_diner = Recommendations(diner=recommendations_data['diner'], user_profile_id=profile.id)
                recommendation_diner_up = Recommendations(diner_up=recommendations_data['diner_up'], user_profile_id=profile.id)
                db.session.add(recommendation_bedtime_hours, recommendation_bedtime_minytes, recommendation_not_hours, 
                               recommendation_not_minytes, recommendation_diner,recommendation_diner_up, recommendation_breakfast_hours, recommendation_breakfast_minutes,
                               recommendation_breakfast_hours_up, recommendation_breakfast_minutes_up, recommendation_lanch_hours, 
                               recommendation_lanch_minutes, recommendation_lanch_hours_up)

            db.session.commit()

            # Возвращаем JSON с рекомендациями
            return jsonify(recommendations_data)
        
        except ValueError as e:
            db.session.rollback()
            return jsonify({'errors': {'weight': 'Некорректный формат числа'}})
        
    else:  # Если это GET запрос, отображаем форму с данными профиля
        if profile:
            return render_template('profile.html', profile=profile, color=color)
        else:
            return render_template('profile.html', color=color)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user = User.query.get(current_user.id)
    color = user.color
    if request.method == 'POST':
        color = request.form.get('color')
        user.color = color
        db.session.commit()
        return render_template("settings.html", color=color)
    else:
        return render_template("settings.html", color=color)



@app.route('/check_username')
def check_username():
    username = request.args.get('username')
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})
      
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Проверяем, существует ли пользователь с таким логином
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь с таким логином уже существует.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
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
        else:
            flash('Неверный логин или пароль', 'error') # Используем flash
            return redirect(url_for('login'))
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
    user = User.query.get(current_user.id)
    color = user.color
    profile = current_user.profile
    recommendations = None
    bedtime_hours = None  # Инициализируем bedtime_hours
    bedtime_minytes = None # Инициализируем bedtime_minytes
    not_hours = None  # Инициализируем not_hours
    not_minytes = None # Инициализируем not_minytes
    breakfast_hours = None
    breakfast_minutes = None  # Инициализируем bedtime_hours
    breakfast_hours_up = None # Инициализируем bedtime_minytes
    breakfast_minutes_up = None  # Инициализируем not_hours
    lanch_hours = None # Инициализируем not_minytes
    lanch_minutes = None
    lanch_hours_up = None  # Инициализируем bedtime_hour
    diner = None # Инициализируем bedtime_minytes
    diner_up = None  # Инициализируем not_hours

    if profile and profile.recommendations:
        recommendations = current_user.profile.recommendations
        bedtime_hours = profile.recommendations.bedtime_hours  # Получаем часы из базы данных
        bedtime_minytes = profile.recommendations.bedtime_minytes  # Получаем минуты из базы данных
        not_hours = profile.recommendations.not_hours  # Получаем часы из базы данных
        not_minytes = profile.recommendations.not_minytes  # Получаем минуты из базы данных
        breakfast_hours = profile.recommendations.breakfast_hours  # Получаем минуты из базы данных
        breakfast_minutes = profile.recommendations.breakfast_minutes  # Получаем минуты из базы данных
        breakfast_hours_up = profile.recommendations.breakfast_hours_up  # Получаем минуты из базы данных
        breakfast_minutes_up = profile.recommendations.breakfast_minutes_up  # Получаем минуты из базы данных
        lanch_hours = profile.recommendations.lanch_hours  # Получаем минуты из базы данных
        lanch_minutes = profile.recommendations.lanch_minutes  # Получаем минуты из базы данных
        lanch_hours_up = profile.recommendations.lanch_hours_up  # Получаем минуты из базы данных
        diner = profile.recommendations.diner  # Получаем минуты из базы данных
        diner_up = profile.recommendations.diner_up  # Получаем минуты из базы данных
    else:
        if profile: # Проверяем, что profile не None
            wake_up_time_hours, wake_up_time_minutes = get_wake_up_time_for_tomorrow(profile) # Получаем время пробуждения для текущего дня
            wake_up_time_hours_2, wake_up_time_minutes_2 = get_wake_up_time_for_today(profile)  # Получаем время пробуждения для текущего дня
            recommendations_data = calculate_recommendations(profile.age, profile.weight, wake_up_time_hours, wake_up_time_minutes, wake_up_time_hours_2, wake_up_time_minutes_2)

            if profile:
                # Получаем часы и минуты из calculate_recommendations
                bedtime_hours = recommendations_data['bedtime_hours']
                bedtime_minytes = recommendations_data['bedtime_minytes']
                not_hours = recommendations_data['not_hours']
                not_minytes = recommendations_data['not_minytes']
                breakfast_hours = recommendations_data['breakfast_hours']
                breakfast_minutes = recommendations_data['breakfast_minutes']
                breakfast_hours_up = recommendations_data['breakfast_hours_up']
                breakfast_minutes_up = recommendations_data['breakfast_minutes_up']
                lanch_hours = recommendations_data['lanch_hours']
                lanch_minutes = recommendations_data['lanch_minutes']
                lanch_hours_up = recommendations_data['lanch_hours_up']
                diner = recommendations_data['diner']
                diner_up = recommendations_data['diner_up']
                
                recommendations = Recommendations(
                    bedtime_hours=bedtime_hours,
                    bedtime_minytes=bedtime_minytes,
                    not_hours=not_hours,
                    not_minytes=not_minytes,
                    breakfast_hours=breakfast_hours,
                    breakfast_minutes=breakfast_minutes,
                    breakfast_hours_up=breakfast_hours_up,
                    breakfast_minutes_up=breakfast_minutes_up,
                    lanch_hours=lanch_hours,
                    lanch_minutes=lanch_minutes,
                    lanch_hours_up=lanch_hours_up,
                    diner=diner,
                    diner_up=diner_up,
                    user_profile_id=profile.id
                )
                db.session.add(recommendations)
                db.session.commit()
        else:
            recommendations_data = {"bedtime_hours": 0, "bedtime_minytes": 0, "not_hours": 0, "not_minytes": 0} # Значения по умолчанию
            recommendations = None

    return render_template('index.html', bedtime_hours=bedtime_hours, bedtime_minytes=bedtime_minytes, not_hours=not_hours, not_minytes=not_minytes,
                           breakfast_hours=breakfast_hours, breakfast_minutes=breakfast_minutes, breakfast_hours_up=breakfast_hours_up, breakfast_minutes_up=breakfast_minutes_up,
                           lanch_hours=lanch_hours, lanch_minutes=lanch_minutes, lanch_hours_up=lanch_hours_up, diner=diner, diner_up=diner_up, color=color)


if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Создаем таблицы (если их еще нет)
    app.run(debug=True)
