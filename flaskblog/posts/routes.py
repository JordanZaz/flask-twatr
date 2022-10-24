from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint, jsonify)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post, Comment, User, Like
from flaskblog.posts.forms import PostForm


posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    Comment.query.filter_by(post_id=post.id).delete()
    Like.query.filter_by(post_id=post.id).delete()
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))


@posts.route("/comment/<int:post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')
    post = Post.query.get_or_404(post_id)
    if not text:
        flash('Comment cannot be empty!', 'danger')
    else:
        post = Post.query.get_or_404(post_id)
        if post:
            comment = Comment(
                content=text, user_id=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', 'error')
    return redirect(url_for('posts.post', post_id=post.id))


@posts.route("/delete-comment/<int:id>", methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    post = Comment.query.filter_by(id=id).first()

    if not post:
        flash('Comment does not exist', 'danger')

    elif current_user != post.author and current_user != post.post.author:
        flash('You do not have permission to delete this comment', 'danger')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Comment deleted!', 'success')
    return redirect(url_for('posts.post', post_id=post.post_id))


@posts.route("/like-post/<int:post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        user_id=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.user_id, post.likes)})


@posts.route("/like-posts/<int:post_id>", methods=['GET'])
@login_required
def likes(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        user_id=current_user.id, post_id=post_id).first()

    if not post:
        flash('Post does not exist.', 'error')
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return redirect(url_for('posts.post', post_id=post.id))


@posts.route("/like-postss/<int:post_id>", methods=['GET'])
@login_required
def likess(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        user_id=current_user.id, post_id=post_id).first()

    if not post:
        flash('Post does not exist.', 'error')
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return redirect(url_for('users.user_posts', username=post.author.username))
