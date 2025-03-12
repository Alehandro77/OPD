from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import datetime  # Импортируем модуль datetime
import random

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
    gender = db.Column(db.String(6))
    height = db.Column(db.Integer)
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

def calculate_recommendations(age, weight, gender, height, wake_up_time_hours, wake_up_time_minutes, wake_up_time_hours_2, wake_up_time_minutes_2):
    """
    Функция для расчета рекомендаций на основе данных пользователя.
    """
    base_time_m = 0
    
    if age >= 0 and age <= 1:
        base_time_h = 13
    elif age >= 2 and age <= 5:
        base_time_h = 12
    elif age >= 6 and age <= 13:
        base_time_h = 10
    elif age >= 14 and age <= 17:
        base_time_h = 9
    elif age >= 18 and age <= 64:
        base_time_h = 8
    elif age > 64:
        base_time_h = 7
        base_time_m = 30

    imt = weight/((height/100)*(height/100))

    if imt < 18.5:
        imt_kor_m = -15
    elif imt >= 25 and age <= 30:
        imt_kor_m = 15
    elif imt > 30:
        imt_kor_m = 30
    else:
        imt_kor_m = 0
    if gender == "men":
        k_gender_m = 0
    elif gender == "women":
        k_gender_m = 15

    bedtime_minytes = (wake_up_time_minutes - (base_time_m + imt_kor_m + k_gender_m)) % 60 // 15 * 15
    k_bedtime_minytes = (wake_up_time_minutes - (base_time_m + imt_kor_m + k_gender_m)) // 60
    bedtime_hours = (wake_up_time_hours - base_time_h + k_bedtime_minytes)  % 24

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
            height = int(request.form['height'])
            gender = request.form['gender']
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

            try:
                height = int(height)
                if height <= 0:
                    errors['height'] = "Рост должен быть положительным числом."
            except ValueError:
                errors['height'] = "Рост должен быть числом."

            # Если есть ошибки, возвращаем их в виде JSON
            if errors:
                return jsonify({'errors': errors})

            # Если ошибок нет, сохраняем данные в базу данных
            try:
                age = int(age)
                weight = float(weight)
                height = int(height)
                gender = gender
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
                profile.aheightge = height
                profile.gender = gender
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
                    age=int(age),
                    weight=int(weight),
                    height=int(height),
                    gender=gender,
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
            recommendations_data = calculate_recommendations(age, weight, gender, height, wake_up_time_hours, wake_up_time_minutes, wake_up_time_hours_2, wake_up_time_minutes_2)
            
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
    breakfast_fact_1 = "Завтрак – топливо для вашего дня. Он должен составлять около 25-30% от вашей суточной нормы калорий. Пропуск завтрака замедляет метаболизм, лишает вас энергии и может привести к перееданию в течение дня. Отдайте предпочтение сложным углеводам и белкам для устойчивого заряда бодрости."
    breakfast_fact_2 = "Завтрак – ключ к концентрации. Он помогает стабилизировать уровень сахара в крови, что крайне важно для работы мозга. Без него сложно сосредоточиться и продуктивно работать. Включите в завтрак продукты, богатые клетчаткой и витаминами группы B."
    breakfast_fact_3 = "Завтрак для поддержания формы. Исследования показывают, что люди, которые регулярно завтракают, реже страдают от лишнего веса. Завтрак активирует метаболические процессы и помогает контролировать аппетит в течение дня. Сделайте выбор в пользу белка и полезных жиров."
    breakfast_fact_4 = "Начните день правильно. Завтрак – это возможность задать тон всему дню. Правильно подобранный завтрак обеспечивает организм необходимыми питательными веществами и создает хорошее настроение. Не пропускайте эту важную трапезу, даже если очень спешите."
    breakfast_fact_5 = "Утренний ритуал здоровья. Завтрак – это не просто еда, это инвестиция в ваше здоровье и благополучие. Он укрепляет иммунитет, улучшает пищеварение и помогает бороться со стрессом. Сделайте завтрак вкусным и полезным ритуалом."
    breakfast_fact_6 = "Завтрак как источник энергии. После ночного голодания организм нуждается в восполнении запасов энергии. Завтрак запускает процесс расщепления жиров и углеводов, обеспечивая вас топливом на несколько часов. Выбирайте продукты с высоким содержанием клетчатки."
    breakfast_fact_7 = " Завтрак для улучшения настроения. Некоторые продукты, такие как яйца и овсянка, содержат вещества, которые способствуют выработке серотонина, гормона счастья. Начните день с полезного и вкусного завтрака, чтобы поднять себе настроение."
    breakfast_fact_8 = " Завтрак – важный элемент здорового питания. Он обеспечивает организм витаминами, минералами и антиоксидантами, которые необходимы для нормального функционирования всех систем. Не забывайте включать в завтрак фрукты и овощи."
    breakfast_fact_9 = "Утренний прием пищи и метаболизм. Завтрак способствует поддержанию здорового метаболизма, что особенно важно для людей, следящих за своим весом. Он помогает сжигать калории в течение дня и предотвращает замедление метаболизма."
    breakfast_fact_10 = "Завтрак как профилактика заболеваний. Регулярный завтрак снижает риск развития сердечно-сосудистых заболеваний, диабета 2 типа и других хронических заболеваний. Правильный выбор продуктов для завтрака – залог здоровья на долгие годы."
    breakfast_fact_11 = "Завтрак: Время для полезных жиров. Не бойтесь включать в завтрак полезные жиры, такие как авокадо, орехи или семена. Они помогают усваивать жирорастворимые витамины и поддерживают здоровье сердца. Они также способствуют чувству сытости."
    breakfast_fact_12 = "Завтрак: Протеиновый заряд. Белок на завтрак способствует более длительному ощущению сытости и помогает контролировать аппетит до обеда. Яйца, йогурт, творог или протеиновый коктейль – отличные варианты."
    breakfast_fact_13 = "Завтрак: Фокус на сложные углеводы. Избегайте простых углеводов, таких как сладости и выпечка, которые вызывают резкий скачок сахара в крови. Вместо этого выбирайте сложные углеводы, такие как овсянка, цельнозерновой хлеб или фрукты."
    breakfast_fact_14 = "Завтрак: Источник клетчатки. Клетчатка помогает нормализовать пищеварение, снижает уровень холестерина и улучшает общее состояние здоровья. Овсянка, фрукты, овощи и цельнозерновые продукты богаты клетчаткой."
    breakfast_fact_15 = "Завтрак: Время для творчества. Не бойтесь экспериментировать с разными рецептами и ингредиентами. Завтрак может быть не только полезным, но и вкусным и разнообразным."
    breakfast_fact_16 = "Завтрак вне дома. Даже если вы не успеваете приготовить завтрак дома, всегда можно найти полезные варианты в кафе или магазине. Выбирайте йогурт, фрукты, смузи или цельнозерновые батончики."
    breakfast_fact_17 = " Завтрак для спортсменов. Спортсменам особенно важно завтракать, чтобы обеспечить организм энергией для тренировок и восстановления после них. Завтрак должен быть богат углеводами и белками."
    breakfast_fact_18 = "Завтрак для детей. Завтрак для детей должен быть особенно питательным и разнообразным, чтобы обеспечить их растущий организм всеми необходимыми веществами. Включите в завтрак фрукты, овощи, цельнозерновые продукты и белок."
    breakfast_fact_19 = "Завтрак: Индивидуальный подход. Не существует универсального завтрака, подходящего всем. Выбирайте продукты, которые вам нравятся и хорошо усваиваются вашим организмом. Прислушивайтесь к своим ощущениям."
    breakfast_fact_20 = "Завтрак и водный баланс. Не забывайте выпивать стакан воды перед завтраком, чтобы запустить пищеварительную систему и восполнить водный баланс после ночного сна. Это также помогает улучшить усвоение питательных веществ."

    lanch_fact_1 = "Обед – залог продуктивности во второй половине дня. Он должен составлять около 30-35% от суточной нормы калорий. Пропуск обеда приводит к снижению энергии и концентрации, а также к перееданию вечером. Включите белок, сложные углеводы и полезные жиры."
    lanch_fact_2 = "Обед – способ поддержать стабильный уровень сахара в крови. Это помогает избежать резких перепадов настроения и поддерживает когнитивные функции. Выбирайте продукты с низким гликемическим индексом и высоким содержанием клетчатки."
    lanch_fact_3 = "Обед для поддержания здорового веса. Сбалансированный обед помогает контролировать аппетит и предотвращает переедание вечером. Сосредоточьтесь на нежирном белке, овощах и цельных злаках."
    lanch_fact_4 = "Перезагрузка в середине дня. Обед – это возможность сделать перерыв в работе и зарядиться энергией. Правильно подобранный обед помогает снять стресс и улучшить общее самочувствие. Выделите время, чтобы насладиться обедом."
    lanch_fact_5 = "Питательный обед для здоровья и энергии. Обед должен быть сбалансированным и содержать все необходимые питательные вещества. Это помогает поддерживать здоровье, укрепляет иммунитет и повышает уровень энергии."
    lanch_fact_6 = "Обед как топливо для мышц. Если вы занимаетесь спортом или ведете активный образ жизни, обед должен быть богат белком и углеводами. Это поможет восстановить мышцы и восполнить запасы гликогена."
    lanch_fact_7 = "Обед для улучшения пищеварения. Включите в обед продукты, богатые клетчаткой, чтобы улучшить пищеварение и предотвратить запоры. Овощи, фрукты и цельнозерновые продукты – отличный выбор."
    lanch_fact_8 = "Обед – возможность получить необходимые витамины и минералы. Обед должен включать в себя разнообразные продукты, чтобы обеспечить организм всеми необходимыми питательными веществами."
    lanch_fact_9 = "Сбалансированный обед для поддержания метаболизма. Обед способствует поддержанию здорового метаболизма, что важно для поддержания здорового веса и общего самочувствия."
    lanch_fact_10 = "Обед как профилактика заболеваний. Правильный выбор продуктов для обеда помогает снизить риск развития сердечно-сосудистых заболеваний, диабета 2 типа и других хронических заболеваний."
    lanch_fact_11 = "Обед: Время для овощей и зелени. Овощи и зелень должны быть неотъемлемой частью обеда. Они богаты витаминами, минералами, антиоксидантами и клетчаткой, которые необходимы для здоровья."
    lanch_fact_12 = "Обед: Контролируйте размер порций. Не переедайте во время обеда. Старайтесь съедать порцию, которая соответствует вашим потребностям в калориях и питательных веществах."
    lanch_fact_13 = "Обед: Не забывайте о полезных жирах. Полезные жиры, такие как авокадо, орехи, семена или оливковое масло, помогают усваивать жирорастворимые витамины и поддерживают здоровье сердца."
    lanch_fact_14 = "Обед: Выбирайте свежие и цельные продукты. Избегайте обработанных продуктов, фаст-фуда и полуфабрикатов. Отдавайте предпочтение свежим и цельным продуктам, которые богаты питательными веществами."
    lanch_fact_15 = "Обед: Планируйте заранее. Планирование обеда поможет вам сделать более здоровый выбор и избежать соблазна перекусить чем-то вредным."
    lanch_fact_16 = "Обед вне дома: Сделайте правильный выбор. Если вы обедаете вне дома, старайтесь выбирать более здоровые варианты. Заказывайте салаты, супы, блюда из нежирного мяса или рыбы с овощами."
    lanch_fact_17 = "Обед для умственной активности. Определенные продукты, такие как рыба, орехи и авокадо, полезны для работы мозга. Включите их в свой обед, чтобы повысить концентрацию и улучшить память."
    lanch_fact_18 = "Обед для тех, кто следит за фигурой. Если вы следите за своей фигурой, отдавайте предпочтение низкокалорийным блюдам, богатым белком и клетчаткой. Салаты, супы и овощные рагу – отличный выбор."
    lanch_fact_19 = "Обед: Правильный баланс. Стремитесь к тому, чтобы ваш обед содержал все необходимые питательные вещества в правильном соотношении: белки, углеводы, жиры, витамины и минералы."
    lanch_fact_20 = "Обед: Наслаждайтесь едой. Не торопитесь во время обеда. Уделите время, чтобы насладиться вкусом еды и получить удовольствие от процесса. Это поможет вам лучше усваиватьпищу и чувствовать себя более удовлетворенным"

    diner_fact_1 = "Ужин – завершение дня и подготовка к ночному отдыху. Он должен составлять около 20-25% суточной нормы калорий. Важно, чтобы ужин не был слишком тяжелым и не перегружал пищеварительную систему перед сном. Выбирайте легкоусвояемые продукты."
    diner_fact_2 = "Ужин для поддержания уровня сахара в крови ночью. Это особенно важно для людей с диабетом или склонностью к гипогликемии. Избегайте простых углеводов и отдавайте предпочтение белку и сложным углеводам."
    diner_fact_3 = "Ужин для поддержания здорового веса и крепкого сна. Легкий и сбалансированный ужин помогает контролировать вес и улучшает качество сна. Тяжелая пища перед сном может вызывать дискомфорт и мешать засыпанию."
    diner_fact_4 = "Расслабление и восстановление вечером. Ужин – это время для расслабления и восстановления после напряженного дня. Насладитесь едой в спокойной обстановке и избегайте просмотра телевизора или использования гаджетов во время еды."
    diner_fact_5 = "Ужин как источник питательных веществ для ночного восстановления. Во время сна организм продолжает работать и восстанавливаться. Ужин обеспечивает организм необходимыми питательными веществами для этого процесса."
    diner_fact_6 = "Ужин для поддержания мышечной массы. Если вы занимаетесь спортом, ужин должен содержать достаточно белка для восстановления и роста мышц во время сна. Нежирное мясо, рыба, яйца или творог – отличные варианты."
    diner_fact_7 = "Ужин для улучшения пищеварения и сна. Включите в ужин продукты, способствующие расслаблению и улучшению пищеварения, такие как ромашковый чай, йогурт или авокадо."
    diner_fact_8 = "Ужин – возможность получить последние необходимые витамины и минералы. Убедитесь, что ваш ужин содержит разнообразные продукты, чтобы обеспечить организм всеми необходимыми питательными веществами до утра."
    diner_fact_9 = "Сбалансированный ужин для гормонального баланса. Правильный ужин может влиять на выработку гормонов во время сна, что важно для общего здоровья и самочувствия."
    diner_fact_10 = "Ужин как профилактика проблем со сном. Избегайте кофеина, алкоголя и тяжелой пищи перед сном, чтобы не нарушать сон."
    diner_fact_11 = "Ужин: Фокус на легкоусвояемый белок. Легкоусвояемый белок, такой как рыба, птица или тофу, является отличным выбором для ужина. Он не перегружает пищеварительную систему и способствует восстановлению мышц."
    diner_fact_12 = "Ужин: Овощи – обязательный компонент. Овощи должны быть неотъемлемой частью ужина. Они богаты витаминами, минералами и клетчаткой, которые необходимы для здоровья и хорошего сна."
    diner_fact_13 = "Ужин: Минимизируйте простые углеводы. Избегайте сладких напитков, десертов и других простых углеводов на ужин. Они могут вызвать резкий скачок сахара в крови и нарушить сон."
    diner_fact_14 = "Ужин: Не переедайте. Переедание на ужин может привести к дискомфорту, изжоге и бессоннице. Старайтесь съедать умеренную порцию, которая соответствует вашим потребностям."
    diner_fact_15 = "Ужин: Соблюдайте интервал. Старайтесь ужинать не позднее, чем за 2-3 часа до сна, чтобы дать организму достаточно времени для переваривания пищи."
    diner_fact_16 = "Ужин вне дома: Сделайте осознанный выбор. Если вы ужинаете вне дома, выбирайте легкие и здоровые блюда. Заказывайте салаты, супы, блюда из рыбы или птицы с овощами."
    diner_fact_17 = "Ужин для хорошего настроения. Некоторые продукты, такие как рыба и авокадо, содержат вещества, которые способствуют выработке серотонина, гормона счастья. Включите их в свой ужин, чтобы улучшить настроение перед сном."
    diner_fact_18 = "Ужин для тех, кто хочет похудеть. Если вы хотите похудеть, выбирайте низкокалорийные блюда, богатые белком и клетчаткой. Салаты, овощные рагу и нежирная рыба – отличный выбор."
    diner_fact_19 = "Ужин: Прислушивайтесь к своему телу. Выбирайте продукты, которые вам нравятся и хорошо усваиваются вашим организмом. Не ешьте то, что вызывает дискомфорт или аллергические реакции."
    diner_fact_20 = "Ужин: Создайте приятную атмосферу. Приглушите свет, зажгите свечи, включите спокойную музыку и насладитесь ужином в приятной обстановке. Это поможет вам расслабиться и подготовиться ко сну."

    relaxr_fact_1 = "За час до сна – время для спокойствия. Отложите гаджеты, приглушите свет и создайте атмосферу умиротворения. Подготовьтесь к ночному отдыху, чтобы сон был глубоким и восстанавливающим. Попробуйте расслабляющую ванну или чтение книги."
    relaxr_fact_2 = "Избавьтесь от экранов за час до сна. Синий свет от экранов гаджетов подавляет выработку мелатонина, гормона сна. Выключите телевизор, компьютер и телефон, чтобы облегчить засыпание и улучшить качество сна."
    relaxr_fact_3 = "Успокойте ум перед сном. Избегайте обсуждения сложных вопросов и просмотра новостей за час до сна. Сосредоточьтесь на позитивных мыслях и расслабляющих занятиях, чтобы успокоить ум и подготовиться к отдыху."
    relaxr_fact_4 = "Ритуал подготовки ко сну – ваш путь к здоровому сну. Разработайте свой собственный ритуал, который поможет вам расслабиться и настроиться на сон. Это может быть теплая ванна, медитация, чтение книги или легкая растяжка."
    relaxr_fact_5 = "Подготовьте спальню ко сну. Убедитесь, что в вашей спальне темно, тихо и прохладно. Оптимальная температура для сна – около 18-20 градусов. Используйте плотные шторы и беруши, если необходимо."
    relaxr_fact_6 = "За час до сна – время для релаксации. Попробуйте расслабляющие техники, такие как глубокое дыхание, медитация или йога. Они помогут снять напряжение и подготовиться к сну."
    relaxr_fact_7 = "Забудьте о рабочих делах за час до сна. Не проверяйте электронную почту и не думайте о рабочих проблемах перед сном. Оставьте все дела на завтра и позвольте себе расслабиться."
    relaxr_fact_8 = "Выпейте травяной чай перед сном. Травяные чаи, такие как ромашковый, лавандовый или валериановый, обладают успокаивающими свойствами и помогают заснуть."
    relaxr_fact_9 = "За час до сна – время для благодарности. Подумайте о том, за что вы благодарны в своей жизни. Это поможет вам сосредоточиться на позитивных мыслях и заснуть с хорошим настроением."
    relaxr_fact_10 = "Подготовьте все необходимое для утра. Соберите вещи на работу, приготовьте завтрак и запланируйте свой день. Это поможет вам избежать утреннего стресса и начать день спокойно."
    relaxr_fact_11 = "За час до сна: Послушайте расслабляющую музыку. Спокойная музыка без слов может помочь вам расслабиться и успокоить ум перед сном."
    relaxr_fact_12 = "За час до сна: Почитайте книгу (бумажную!). Чтение бумажной книги – отличный способ отвлечься от проблем и подготовиться ко сну. Избегайте электронных книг на планшетах или телефонах."
    relaxr_fact_13 = "За час до сна: Напишите в дневник. Запишите свои мысли и чувства в дневник. Это поможет вам освободиться от негативных эмоций и заснуть с чистой головой."
    relaxr_fact_14 = "За час до сна: Поговорите с близким человеком. Поделитесь своими переживаниями с близким человеком. Это поможет вам почувствовать поддержку и расслабиться."
    relaxr_fact_15 = "За час до сна: Сделайте легкую растяжку. Легкая растяжка поможет расслабить мышцы и снять напряжение."
    relaxr_fact_16 = "За час до сна: Уделите время уходу за собой. Сделайте маску для лица, нанесите увлажняющий крем или примите теплую ванну. Это поможет вам расслабиться и почувствовать себя лучше."
    relaxr_fact_17 = "За час до сна: Приготовьтесь к завтрашнему дню. Соберите одежду, подготовьте документы и сделайте все необходимое, чтобы утро прошло гладко."
    relaxr_fact_18 = "За час до сна: Подумайте о своих целях. Визуализируйте свои цели и представьте, как вы их достигаете. Это поможет вам почувствовать себя увереннее и мотивированнее."
    relaxr_fact_19 = "За час до сна: Создайте уютную атмосферу. Зажгите аромалампу с эфирными маслами, которые способствуют расслаблению, такими как лаванда или ромашка."
    relaxr_fact_20 = "За час до сна: Сделайте паузу для себя. Отвлекитесь от всего и посвятите время только себе. Сделайте то, что вам нравится и что помогает вам расслабиться и почувствовать себя счастливым. Это ваша личная подготовка к здоровому и крепкому сну."

    facts_list = [breakfast_fact_1, breakfast_fact_2, breakfast_fact_3, breakfast_fact_4,
                            breakfast_fact_5, breakfast_fact_6, breakfast_fact_7, breakfast_fact_8,
                            breakfast_fact_9, breakfast_fact_10, breakfast_fact_11, breakfast_fact_12,
                            breakfast_fact_13, breakfast_fact_14, breakfast_fact_15, breakfast_fact_16,
                            breakfast_fact_17, breakfast_fact_18, breakfast_fact_19, breakfast_fact_20,
                            lanch_fact_1, lanch_fact_2, lanch_fact_3, lanch_fact_4,
                            lanch_fact_5, lanch_fact_6, lanch_fact_7, lanch_fact_8,
                            lanch_fact_9, lanch_fact_10, lanch_fact_11, lanch_fact_12,
                            lanch_fact_13, lanch_fact_14, lanch_fact_15, lanch_fact_16,
                            lanch_fact_17, lanch_fact_18, lanch_fact_19, lanch_fact_20,
                            diner_fact_1, diner_fact_2, diner_fact_3, diner_fact_4,
                            diner_fact_5, diner_fact_6, diner_fact_7, diner_fact_8,
                            diner_fact_9, diner_fact_10, diner_fact_11, diner_fact_12,
                            diner_fact_13, diner_fact_14, diner_fact_15, diner_fact_16,
                            diner_fact_17, diner_fact_18, diner_fact_19, diner_fact_20,
                            relaxr_fact_1, relaxr_fact_2, relaxr_fact_3, relaxr_fact_4,
                            relaxr_fact_5, relaxr_fact_6, relaxr_fact_7, relaxr_fact_8,
                            relaxr_fact_9, relaxr_fact_10, relaxr_fact_11, relaxr_fact_12,
                            relaxr_fact_13, relaxr_fact_14, relaxr_fact_15, relaxr_fact_16,
                            relaxr_fact_17, relaxr_fact_18, relaxr_fact_19, relaxr_fact_20]


    sovet = random.choice(facts_list)
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
            recommendations_data = calculate_recommendations(profile.age, profile.weight, profile.gender, profile.height, wake_up_time_hours, wake_up_time_minutes, wake_up_time_hours_2, wake_up_time_minutes_2)

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
                           lanch_hours=lanch_hours, lanch_minutes=lanch_minutes, lanch_hours_up=lanch_hours_up, diner=diner, diner_up=diner_up, color=color,
                           sovet=sovet)


if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Создаем таблицы (если их еще нет)
    app.run(debug=True)
