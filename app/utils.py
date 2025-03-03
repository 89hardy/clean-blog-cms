import os
import logging
from datetime import datetime
from github import Github
from config.config import Config

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def commit_and_push_changes():
    """Commit and push changes to the blog repository."""
    try:
        # Debug logging
        logger.debug(f"Starting commit_and_push_changes")
        logger.debug(f"BLOG_PATH: {Config.BLOG_PATH}")
        logger.debug(f"POSTS_PATH: {Config.POSTS_PATH}")
        logger.debug(f"GitHub Username: {Config.GITHUB_USERNAME}")
        
        if not Config.GITHUB_TOKEN:
            return False, "GitHub token not configured"
        
        # Initialize GitHub client
        g = Github(Config.GITHUB_TOKEN)
        repo = g.get_repo(f"{Config.GITHUB_USERNAME}/89hardy.github.io")
        logger.debug(f"Connected to repository: {repo.full_name}")
        
        # Get the current branch (usually 'main' or 'master')
        branch = repo.default_branch
        logger.debug(f"Default branch: {branch}")
        
        # Get the latest commit
        ref = repo.get_git_ref(f"heads/{branch}")
        latest_commit = repo.get_commit(ref.object.sha)
        logger.debug(f"Latest commit SHA: {latest_commit.sha}")
        
        # Create a tree with the new/modified files
        base_tree = latest_commit.commit.tree
        element_list = []
        
        # Walk through the _posts directory
        logger.debug(f"Walking through posts directory: {Config.POSTS_PATH}")
        for root, dirs, files in os.walk(Config.POSTS_PATH):
            logger.debug(f"Found files: {files}")
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    logger.debug(f"Processing file: {file_path}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create blob
                    blob = repo.create_git_blob(content, "utf-8")
                    logger.debug(f"Created blob with SHA: {blob.sha}")
                    
                    # Create tree element
                    relative_path = os.path.relpath(file_path, Config.BLOG_PATH)
                    logger.debug(f"Relative path: {relative_path}")
                    element = {
                        "path": relative_path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob.sha
                    }
                    element_list.append(element)
        
        if element_list:
            logger.debug(f"Creating tree with {len(element_list)} elements")
            # Create tree
            new_tree = repo.create_git_tree(element_list, base_tree)
            
            # Create commit
            commit_message = f"Update blog posts - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            new_commit = repo.create_git_commit(
                commit_message,
                new_tree,
                [latest_commit.commit]
            )
            logger.debug(f"Created commit with SHA: {new_commit.sha}")
            
            # Update reference
            ref.edit(new_commit.sha)
            logger.debug("Updated reference successfully")
            
            return True, "Changes pushed successfully"
        else:
            logger.warning("No files to commit")
            return False, "No files to commit"
    except Exception as e:
        logger.error(f"Error in commit_and_push_changes: {str(e)}", exc_info=True)
        return False, f"Error pushing changes: {str(e)}"

def sync_images():
    """Sync images from the local assets directory to GitHub."""
    try:
        logger.debug("Starting sync_images")
        logger.debug(f"IMAGES_PATH: {Config.IMAGES_PATH}")
        
        if not Config.GITHUB_TOKEN:
            return False, "GitHub token not configured"
        
        # Initialize GitHub client
        g = Github(Config.GITHUB_TOKEN)
        repo = g.get_repo(f"{Config.GITHUB_USERNAME}/89hardy.github.io")
        logger.debug(f"Connected to repository: {repo.full_name}")
        
        # Get the current branch
        branch = repo.default_branch
        ref = repo.get_git_ref(f"heads/{branch}")
        latest_commit = repo.get_commit(ref.object.sha)
        logger.debug(f"Latest commit SHA: {latest_commit.sha}")
        
        # Create a tree with the images
        base_tree = latest_commit.commit.tree
        element_list = []
        
        # Walk through the images directory
        logger.debug(f"Walking through images directory: {Config.IMAGES_PATH}")
        for root, dirs, files in os.walk(Config.IMAGES_PATH):
            logger.debug(f"Found files: {files}")
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    file_path = os.path.join(root, file)
                    logger.debug(f"Processing file: {file_path}")
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    # Create blob
                    blob = repo.create_git_blob(content.hex(), "base64")
                    logger.debug(f"Created blob with SHA: {blob.sha}")
                    
                    # Create tree element
                    relative_path = os.path.relpath(file_path, Config.BLOG_PATH)
                    logger.debug(f"Relative path: {relative_path}")
                    element = {
                        "path": relative_path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob.sha
                    }
                    element_list.append(element)
        
        if element_list:
            logger.debug(f"Creating tree with {len(element_list)} elements")
            # Create tree
            new_tree = repo.create_git_tree(element_list, base_tree)
            
            # Create commit
            commit_message = f"Update blog images - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            new_commit = repo.create_git_commit(
                commit_message,
                new_tree,
                [latest_commit.commit]
            )
            logger.debug(f"Created commit with SHA: {new_commit.sha}")
            
            # Update reference
            ref.edit(new_commit.sha)
            logger.debug("Updated reference successfully")
            
            return True, "Images synced successfully"
        else:
            logger.warning("No images to sync")
            return False, "No images to sync"
    except Exception as e:
        logger.error(f"Error in sync_images: {str(e)}", exc_info=True)
        return False, f"Error syncing images: {str(e)}" 