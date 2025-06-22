from flask import Flask, request, jsonify
from models.user import User
from models.meal import Meal
from database import db
from flask_login import LoginManager,login_user, current_user, logout_user, login_required
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3307/daily-diet'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@app.route('/user', methods=['POST'])
def create_user():
  data = request.json
  username = data.get('username')
  password = data.get('password')

  if username and password:
    hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
    user = User(username=username, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message':'Usuário criado com sucesso.', 'user_id': user.id})

  return jsonify({'message': 'Dados inválidos.'}), 400  

@app.route('/login', methods=['POST'])
def login():
  data = request.json
  username = data.get('username')
  password = data.get('password')

  if username and password:
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
      login_user(user)
      return jsonify({'message': f'Autenticação realizada com sucesso. Usuário {user.username} logado.'})

  return jsonify({'message': 'Credenciais inválidas'}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
  logout_user()
  return jsonify({'message': 'Logout realizado com sucesso.'})

@app.route('/new_meal', methods=['POST'])
@login_required
def new_meal():
  data = request.json
  meal_name = data.get('meal_name')
  meal_description = data.get('meal_description')
  date_time = data.get('date_time')
  diet_meal = data.get('diet_meal')
  user_id = current_user.id

  if meal_name and diet_meal is not None:
    meal = Meal(meal_name=meal_name, meal_description=meal_description, date_time=date_time, diet_meal=diet_meal, user_id=user_id)
    db.session.add(meal)
    db.session.commit()
    return jsonify({'message': 'Refeição criada com sucesso.', 'meal_id': meal.id})
  
  return jsonify({'message': 'Dados insuficientes para criar refeição. Favor fornecer nome da refeição e se faz parte da dieta.'}), 400

@app.route('/edit_meal/<int:meal_id>', methods=['POST'])
@login_required
def edit_meal(meal_id):
  data = request.json
  meal_name = data.get('meal_name')
  meal_description = data.get('meal_description')
  date_time = data.get('date_time')
  diet_meal = data.get('diet_meal')

  meal = Meal.query.filter_by(id=meal_id).first()
  if meal:
    if current_user.id == meal.user_id:
      meal.meal_name = meal_name if meal_name else meal.meal_name
      meal.meal_description = meal_description if meal_description else meal.meal_description
      meal.date_time = date_time if date_time else meal.date_time
      meal.diet_meal = diet_meal if diet_meal is not None else meal.diet_meal
      db.session.commit()
      return jsonify({'message': f'Refeição {meal.id} editada com sucesso.'})
    return jsonify({'message': 'Não é possível editar refeições de outro usuário.'}), 400
  return jsonify({'message': 'Refeição não encontrada.'}), 400



if __name__ == '__main__':
  app.run(debug=True)