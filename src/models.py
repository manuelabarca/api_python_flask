from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

    def get_user(email):
        user = User.query.filter_by(email=email).first()
        return user

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.String(255), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "description": self.description
        }
    
    def create_post(user_id, description):
        post = Post(user_id=user_id, description=description)
        db.session.add(post)
        db.session.commit()
    
    def get_all_post():
        posts = Post.query.all()
        posts = list(map(lambda post: post.serialize(), posts))
        return posts

    def get_post(user_id):
        post = Post.query.filter_by(user_id=user_id).first()
        return post

    def delete_post(post_id):
        post = Post.query.get(post_id)
        db.session.delete(post)
        db.session.commit()

class Favorite(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id
        }

    def create_favorite(user_id, post_id):
        favorite = Favorite(user_id=user_id, post_id=post_id)
        db.session.add(favorite)
        db.session.commit()

    def get_all_favorites():
        favorites = Favorite.query.all()
        favorites = list(map(lambda favorite: favorite.serialize(), favorites))
        return favorites