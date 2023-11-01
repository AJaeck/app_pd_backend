from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    # No need to manually define the 'results' relationship here.


class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    taps = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('results', lazy=True))

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

@app.route('/get-user-data/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    print(user)
    if user:
        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "dob": user.dob.strftime('%d.%m.%Y'),
            "results": [{"date": result.date.strftime('%Y-%m-%d'), "taps": result.taps} for result in user.results]
        }
        return jsonify(user_data), 200
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/delete-user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Delete associated results
    Results.query.filter_by(user_id=user_id).delete()

    # Delete the user
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User and associated data deleted successfully!"}), 200


@app.route('/save-tapping-result/<user_id>', methods=['POST'])
def save_tapping_result(user_id):
    data = request.json

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    tapping_result = Results(user_id=user_id, date=datetime.now(), taps=data['taps'])
    db.session.add(tapping_result)
    db.session.commit()
    return jsonify({"message": "Tapping result saved successfully!"}), 201

@app.route('/get-tapping-results/<user_id>', methods=['GET'])
def get_tapping_results(user_id):
    results = Results.query.filter_by(user_id=user_id).all()
    return jsonify([{"date": result.date.strftime('%Y-%m-%d'), "taps": result.taps} for result in results]), 200

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db()  # Uncomment this if you want to initialize the db every time you run the app
    app.run(debug=True)
