import os
import logging
import requests
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
        tree_data = []
        
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
                    
                    # Create blob using GitHub API directly
                    headers = {
                        'Authorization': f'token {Config.GITHUB_TOKEN}',
                        'Accept': 'application/vnd.github.v3+json'
                    }
                    blob_data = {
                        'content': content,
                        'encoding': 'utf-8'
                    }
                    blob_response = requests.post(
                        f'https://api.github.com/repos/{Config.GITHUB_USERNAME}/89hardy.github.io/git/blobs',
                        headers=headers,
                        json=blob_data
                    ).json()
                    logger.debug(f"Created blob with SHA: {blob_response['sha']}")
                    
                    # Create tree element
                    relative_path = os.path.relpath(file_path, Config.BLOG_PATH)
                    logger.debug(f"Relative path: {relative_path}")
                    tree_data.append({
                        "path": relative_path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob_response['sha']
                    })
        
        if tree_data:
            logger.debug(f"Creating tree with {len(tree_data)} elements")
            # Create tree using GitHub API directly
            tree_payload = {
                'base_tree': base_tree.sha,
                'tree': tree_data
            }
            tree_response = requests.post(
                f'https://api.github.com/repos/{Config.GITHUB_USERNAME}/89hardy.github.io/git/trees',
                headers=headers,
                json=tree_payload
            ).json()
            
            # Create commit using GitHub API directly
            commit_message = f"Update blog posts - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            commit_data = {
                'message': commit_message,
                'tree': tree_response['sha'],
                'parents': [latest_commit.sha]
            }
            commit_response = requests.post(
                f'https://api.github.com/repos/{Config.GITHUB_USERNAME}/89hardy.github.io/git/commits',
                headers=headers,
                json=commit_data
            ).json()
            logger.debug(f"Created commit with SHA: {commit_response['sha']}")
            
            # Update reference using GitHub API directly
            ref_data = {
                'sha': commit_response['sha'],
                'force': False
            }
            ref_response = requests.patch(
                f'https://api.github.com/repos/{Config.GITHUB_USERNAME}/89hardy.github.io/git/refs/heads/{branch}',
                headers=headers,
                json=ref_data
            )
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
        tree_data = []
        
        # Set up headers for GitHub API
        headers = {
            'Authorization': f'token {Config.GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
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
                    
                    # Create blob using GitHub API directly
                    blob_data = {
                        'content': content.hex(),
                        'encoding': 'base64'
                    }
                    blob_response = requests.post(
                        f'https://api.github.com/repos/{Config.GITHUB_USERNAME}/89hardy.github.io/git/blobs',
                        headers=headers,
                        json=blob_data
                    ).json()
                    logger.debug(f"Created blob with SHA: {blob_response['sha']}")
                    
                    # Create tree element
                    relative_path = os.path.relpath(file_path, Config.BLOG_PATH)
                    logger.debug(f"Relative path: {relative_path}")
                    tree_data.append({
                        "path": relative_path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob_response['sha']
                    })
        
        if tree_data:
            logger.debug(f"Creating tree with {len(tree_data)} elements")
            # Create tree using GitHub API directly
            tree_payload = {
                'base_tree': base_tree.sha,
                'tree': tree_data
            }
            tree_response = requests.post(
                f'https://api.github.com/repos/{Config.GITHUB_USERNAME}/89hardy.github.io/git/trees',
                headers=headers,
                json=tree_payload
            ).json()
            
            # Create commit using GitHub API directly
            commit_message = f"Update blog images - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            commit_data = {
                'message': commit_message,
                'tree': tree_response['sha'],
                'parents': [latest_commit.sha]
            }
            commit_response = requests.post(
                f'https://api.github.com/repos/{Config.GITHUB_USERNAME}/89hardy.github.io/git/commits',
                headers=headers,
                json=commit_data
            ).json()
            logger.debug(f"Created commit with SHA: {commit_response['sha']}")
            
            # Update reference using GitHub API directly
            ref_data = {
                'sha': commit_response['sha'],
                'force': False
            }
            ref_response = requests.patch(
                f'https://api.github.com/repos/{Config.GITHUB_USERNAME}/89hardy.github.io/git/refs/heads/{branch}',
                headers=headers,
                json=ref_data
            )
            logger.debug("Updated reference successfully")
            
            return True, "Images synced successfully"
        else:
            logger.warning("No images to sync")
            return False, "No images to sync"
    except Exception as e:
        logger.error(f"Error in sync_images: {str(e)}", exc_info=True)
        return False, f"Error syncing images: {str(e)}"

def delete_from_github(file_path):
    """Delete a file from GitHub repository."""
    try:
        logger.debug(f"Starting delete_from_github for {file_path}")
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
        
        # Set up headers for GitHub API
        headers = {
            'Authorization': f'token {Config.GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get the current tree
        base_tree = latest_commit.commit.tree
        
        # Create a new tree without the deleted file
        tree_data = []
        for item in base_tree.tree:
            if item.path != file_path:
                tree_data.append({
                    "path": item.path,
                    "mode": item.mode,
                    "type": item.type,
                    "sha": item.sha
                })
        
        # Create new tree using GitHub API
        tree_payload = {
            'base_tree': None,  # Create a new root tree
            'tree': tree_data
        }
        tree_response = requests.post(
            f'https://api.github.com/repos/{Config.GITHUB_USERNAME}/89hardy.github.io/git/trees',
            headers=headers,
            json=tree_payload
        ).json()
        
        # Create commit using GitHub API
        commit_message = f"Delete {file_path} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        commit_data = {
            'message': commit_message,
            'tree': tree_response['sha'],
            'parents': [latest_commit.sha]
        }
        commit_response = requests.post(
            f'https://api.github.com/repos/{Config.GITHUB_USERNAME}/89hardy.github.io/git/commits',
            headers=headers,
            json=commit_data
        ).json()
        logger.debug(f"Created commit with SHA: {commit_response['sha']}")
        
        # Update reference using GitHub API
        ref_data = {
            'sha': commit_response['sha'],
            'force': False
        }
        ref_response = requests.patch(
            f'https://api.github.com/repos/{Config.GITHUB_USERNAME}/89hardy.github.io/git/refs/heads/{branch}',
            headers=headers,
            json=ref_data
        )
        logger.debug("Updated reference successfully")
        
        return True, "File deleted successfully"
    except Exception as e:
        logger.error(f"Error in delete_from_github: {str(e)}", exc_info=True)
        return False, f"Error deleting file: {str(e)}" 