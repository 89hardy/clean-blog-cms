import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required
import frontmatter
from config.config import Config

posts = Blueprint('posts', __name__)

def get_post_path(filename):
    """Get the full path for a post file."""
    return os.path.join(Config.POSTS_PATH, filename)

def get_all_posts():
    """Get all posts with their metadata."""
    posts_list = []
    if os.path.exists(Config.POSTS_PATH):
        for filename in os.listdir(Config.POSTS_PATH):
            if filename.endswith('.md'):
                post_path = get_post_path(filename)
                with open(post_path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                    posts_list.append({
                        'filename': filename,
                        'title': post.metadata.get('title', ''),
                        'date': post.metadata.get('date', ''),
                        'categories': post.metadata.get('categories', []),
                        'tags': post.metadata.get('tags', [])
                    })
    return sorted(posts_list, key=lambda x: x['date'] or '', reverse=True)

@posts.route('/posts')
@login_required
def list_posts():
    """List all posts."""
    posts_list = get_all_posts()
    return render_template('posts/list.html', posts=posts_list)

@posts.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """Create a new post."""
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        categories = request.form.get('categories', '').split(',')
        tags = request.form.get('tags', '').split(',')
        
        # Create filename from title
        date = datetime.now().strftime('%Y-%m-%d')
        filename = f"{date}-{title.lower().replace(' ', '-')}.md"
        
        # Create post with frontmatter
        post = frontmatter.Post(
            content,
            title=title,
            date=datetime.now(),
            categories=[cat.strip() for cat in categories if cat.strip()],
            tags=[tag.strip() for tag in tags if tag.strip()]
        )
        
        # Ensure the posts directory exists
        os.makedirs(Config.POSTS_PATH, exist_ok=True)
        
        # Save the post
        post_path = get_post_path(filename)
        with open(post_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        flash('Post created successfully')
        return redirect(url_for('posts.list_posts'))
    
    return render_template('posts/edit.html')

@posts.route('/posts/<filename>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(filename):
    """Edit an existing post."""
    post_path = get_post_path(filename)
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        categories = request.form.get('categories', '').split(',')
        tags = request.form.get('tags', '').split(',')
        
        # Load existing post to preserve date
        with open(post_path, 'r', encoding='utf-8') as f:
            existing_post = frontmatter.load(f)
        
        # Update post with new content and metadata
        post = frontmatter.Post(
            content,
            title=title,
            date=existing_post.metadata.get('date', datetime.now()),
            categories=[cat.strip() for cat in categories if cat.strip()],
            tags=[tag.strip() for tag in tags if tag.strip()]
        )
        
        # Save the updated post
        with open(post_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        flash('Post updated successfully')
        return redirect(url_for('posts.list_posts'))
    
    # Load existing post for editing
    with open(post_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
        return render_template('posts/edit.html', 
                            post=post.content,
                            title=post.metadata.get('title', ''),
                            categories=','.join(post.metadata.get('categories', [])),
                            tags=','.join(post.metadata.get('tags', [])))

@posts.route('/posts/<filename>/delete', methods=['POST'])
@login_required
def delete_post(filename):
    """Delete a post."""
    post_path = get_post_path(filename)
    try:
        os.remove(post_path)
        flash('Post deleted successfully')
    except OSError:
        flash('Error deleting post')
    return redirect(url_for('posts.list_posts')) 