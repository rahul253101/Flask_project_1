from flask_sqlalchemy.session import Session

from project import db, app
from project import User, Post

app.app_context().push()
db.create_all()
# user3 = User(username='Sam', email='Sam@gmail.com', password='password')
# db.session.add(user3)
#
# user4 = User(username ='Tim', email='Tim@gmail.com', password='password')
#
# db.session.add(user4)
#
# db.session.commit()

# x = User.query.filter_by(username='Sam')
x = User.query.all()
# x = User.query.first()

for i in x:
    print(i.username)

i=0
for i in x:
    print(i.id)

post1 = Post(title='Fist post', content='Hey Minaa', user_id=i.id)
db.session.add(post1)
db.session.commit()
y = Post.query.first()
print(y)
