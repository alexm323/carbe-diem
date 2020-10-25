from models import db, User
from app import app

# Create all tables
db.drop_all()
db.create_all()

a = User(username='alexm323', password='123',
         email='alexmartinez323@gmail.com', first_name='Alex', last_name='Martinez')
b = User(username='benm323', password='123',
         email='benmartinez323@gmail.com', first_name='Benjamin', last_name='Martinez')
s = User(username='samm323', password='123',
         email='sammartinez323@gmail.com', first_name='Sam', last_name='Martinez')


db.session.add_all([a, b, s])

db.session.commit()
