import os
from datetime import datetime
from github import Github
from config.config import Config

def commit_and_push_changes():
    """Commit and push changes to the blog repository."""
    try:
        # Initialize GitHub client
        g = Github(Config.GITHUB_TOKEN)
        repo = g.get_repo(f"{Config.GITHUB_USERNAME}/89hardy.github.io")
        
        # Get the current branch (usually 'main' or 'master')
        branch = repo.default_branch
        
        # Get the latest commit
        ref = repo.get_git_ref(f"heads/{branch}")
        latest_commit = repo.get_commit(ref.object.sha)
        
        # Create a tree with the new/modified files
        base_tree = latest_commit.commit.tree
        element_list = []
        
        # Walk through the _posts directory
        for root, dirs, files in os.walk(Config.POSTS_PATH):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create blob
                    blob = repo.create_git_blob(content, "utf-8")
                    
                    # Create tree element
                    relative_path = os.path.relpath(file_path, Config.BLOG_PATH)
                    element = {
                        "path": relative_path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob.sha
                    }
                    element_list.append(element)
        
        if element_list:
            # Create tree
            new_tree = repo.create_git_tree(element_list, base_tree)
            
            # Create commit
            commit_message = f"Update blog posts - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            new_commit = repo.create_git_commit(
                commit_message,
                new_tree,
                [latest_commit.commit]
            )
            
            # Update reference
            ref.edit(new_commit.sha)
            
            return True, "Changes pushed successfully"
    except Exception as e:
        return False, f"Error pushing changes: {str(e)}"

def sync_images():
    """Sync images from the local assets directory to GitHub."""
    try:
        # Initialize GitHub client
        g = Github(Config.GITHUB_TOKEN)
        repo = g.get_repo(f"{Config.GITHUB_USERNAME}/89hardy.github.io")
        
        # Get the current branch
        branch = repo.default_branch
        ref = repo.get_git_ref(f"heads/{branch}")
        latest_commit = repo.get_commit(ref.object.sha)
        
        # Create a tree with the images
        base_tree = latest_commit.commit.tree
        element_list = []
        
        # Walk through the images directory
        for root, dirs, files in os.walk(Config.IMAGES_PATH):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    # Create blob
                    blob = repo.create_git_blob(content.hex(), "base64")
                    
                    # Create tree element
                    relative_path = os.path.relpath(file_path, Config.BLOG_PATH)
                    element = {
                        "path": relative_path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob.sha
                    }
                    element_list.append(element)
        
        if element_list:
            # Create tree
            new_tree = repo.create_git_tree(element_list, base_tree)
            
            # Create commit
            commit_message = f"Update blog images - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            new_commit = repo.create_git_commit(
                commit_message,
                new_tree,
                [latest_commit.commit]
            )
            
            # Update reference
            ref.edit(new_commit.sha)
            
            return True, "Images synced successfully"
    except Exception as e:
        return False, f"Error syncing images: {str(e)}" 