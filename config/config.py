import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')
    BLOG_PATH = os.path.abspath(os.getenv('BLOG_PATH', '../blog'))
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
    
    # Derived paths
    POSTS_PATH = os.path.join(BLOG_PATH, '_posts')
    DRAFTS_PATH = os.path.join(BLOG_PATH, '_drafts')
    IMAGES_PATH = os.path.join(BLOG_PATH, 'assets/images')
    
    # Ensure directories exist
    @classmethod
    def init_app(cls):
        os.makedirs(cls.POSTS_PATH, exist_ok=True)
        os.makedirs(cls.DRAFTS_PATH, exist_ok=True)
        os.makedirs(cls.IMAGES_PATH, exist_ok=True) 