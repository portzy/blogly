"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, default='static/images/default_profile.png')
    posts = db.relationship("Post", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.id}: {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


    @property
    def friendly_date(self):
        """Return nicely-formatted date."""

        return self.created_at.strftime("%a %b %-d  %Y, %-I:%M %p")
    
class PostTag(db.Model):
    """manages many2many rs between posts and tags."""
    __tablename__ = 'posts_tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, 
                        db.ForeignKey('posts.id'),
                        primary_key=True, )
    tag_id = db.Column(db.Integer, 
                       db.ForeignKey('tags.id'),
                       primary_key=True)

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique= True, nullable=False)

    posts = db.relationship(
        'Post',
        secondary='posts_tags', 
        backref='tags',
    )

def connect_db(app):
    db.app = app
    db.init_app(app)




        