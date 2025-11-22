from flask import Flask
from database import db, init_db
import models  # This imports all models

app = Flask(__name__)

# Have to replace this with our own info
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/fitness_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize database
init_db(app)

@app.route('/')
def index():
    return "Fitness Management System - ORM Version"

if __name__ == '__main__':
    app.run(debug=True)