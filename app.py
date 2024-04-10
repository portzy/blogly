"""Blogly application."""

from flask import Flask, render_template, request, redirect, flash, url_for
from models import db, connect_db, User, Post, Tag


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'akina123'  
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

with app.app_context():
    db.create_all()

@app.route('/')
def root():
    """Show recent list of posts, most-recent first."""

    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template("homepage.html", posts=posts)

############USERS################

@app.route('/users')
def users_list():
    users = User.query.all()
    return render_template('users/users.html', users=users)

@app.route('/users/new', methods=["GET"])
def users_new_form():
    """Show a form to create a new user"""

    return render_template('users/user_new.html')

@app.route('/users/new', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        image_url = request.form.get('image_url') or None
        new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)

        db.session.add(new_user)
        db.session.commit()

        return redirect('/users')
    
@app.route('/users/<int:user_id>')
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('users/user_details.html', user=user)

@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('users/user_edit.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['POST'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    user.first_name = request.form.get('first_name')
    user.last_name = request.form.get('last_name')
    user.image_url = request.form.get('image_url', 'default_image.png')
    image_url = request.form.get('image_url')
    if image_url:
        user.image_url = image_url
    
    db.session.commit()
    return redirect(f'/users/{user_id}')

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')


###################POSTS#########################

@app.route('/users/<int:user_id>/posts/new', methods=['GET'])
def posts_new_form(user_id):
    user = User.query.get_or_404(user_id) 
    return render_template('posts/post_new.html', user=user)  

@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def posts_new(user_id):
    """Handle form submission for creating a new post for a specific user"""

    user = User.query.get_or_404(user_id)
    new_post = Post(title=request.form['title'],
                    content=request.form['content'],
                    user=user)

    db.session.add(new_post)
    db.session.commit()
    flash(f"Post '{new_post.title}' added.")

    return redirect(f"/users/{user_id}")


@app.route('/posts/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('posts/post_details.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        db.session.commit()
        return redirect(f'/posts/{post.id}')
    else:
        return render_template('posts/post_edit.html', post=post)

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(f'/users/{post.user_id}') 

############TAGS#############

@app.route('/tags')
def tags_index():
    """show page with all tags"""
    tags = Tag.query.all()
    return render_template('tags/tag_index.html', tags=tags)

@app.route('/tags/new')
def tags_new_form():
    """show form to create a new tag"""
    posts = Post.query.all()
    return render_template('/tags/tag_new.html', posts=posts)

@app.route('/tags/new', methods=['POST'])
def tags_new():
    """handles form submission for creating new tag"""
    tag_name = request.form.get('name')
    post_ids = request.form.getlist('posts')
    new_tag = Tag(name=tag_name)

    for post_id in post_ids:
        post = Post.query.get(post_id)
        new_tag.posts.append(post)

    db.session.add(new_tag)
    db.session.commit()

    flash(f"Tag '{new_tag.name}' added.")
    return redirect('/tags')

@app.route('/tags/<int:tag_id>')
def tags_show(tag_id):
    """show a page with info on a tag"""

    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/tag_show.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit')
def tags_edit_form(tag_id):
    """show a form to edit an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tags/tag_edit.html', tag=tag, posts=posts)

@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tags_edit(tag_id):
    """handle form submission for tag edits."""
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = request.form.getlist('posts')
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' edited.")

    return redirect("/tags")

@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tags_delete(tag_id):
    """handle form submission for deleting a tag."""
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' deleted.")

    return redirect('/tags')


if __name__ == '__main__':
    app.run(debug=True)





