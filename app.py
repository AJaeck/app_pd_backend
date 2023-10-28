from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    dob = db.Column(db.Date, nullable=False)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.json
    dob_date = datetime.strptime(data['dob'], '%Y-%m-%d').date()  # Convert string to date object

    # Check if the user with the given details already exists
    existing_user = User.query.filter_by(first_name=data['first_name'], last_name=data['last_name'],
                                         dob=dob_date).first()
    if existing_user:
        return jsonify({"message": "User with the same details already exists!"}), 409

    new_user = User(first_name=data['first_name'], last_name=data['last_name'], dob=dob_date)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully!", "user_id": new_user.id}), 201

@app.route('/get-users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "dob": user.dob.strftime('%d.%m.%Y')} for user in users]), 200

@app.route('/get-user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "dob": user.dob.strftime('%d.%m.%Y')})
    else:
        return jsonify({"message": "User not found"}), 404

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db()  # Uncomment this if you want to initialize the db every time you run the app
    app.run(debug=True)
