import os
from flask import Blueprint, request, session, redirect, url_for, render_template
import requests
import jwt
from app.models import Media
from app.utills.logger import setup_logger  

logger = setup_logger(__name__)

auth_blueprint = Blueprint('auth', __name__)
main_blueprint = Blueprint('main', __name__)

CognitoClientID = os.getenv("COGNITO_CLIENT_ID", "32hl71n1am3l8evck3k5oeka8g")
CognitoDomain = os.getenv("COGNITO_DOMAIN", "kibe.auth.us-east-2.amazoncognito.com")
RedirectURI = os.getenv("REDIRECT_URI", "http://localhost:5000/callback")

logger.info(f"Cognito Client ID: {CognitoClientID}, Cognito Domain: {CognitoDomain}, Redirect URI: {RedirectURI}")

@main_blueprint.route('/')
def home():
    logger.info("Home page accessed")
    return render_template('index.html')

@auth_blueprint.route('/login')
def login():
    logger.info("Login page accessed")
    cognito_login_url = f"https://{CognitoDomain}/login?client_id={CognitoClientID}&response_type=code&scope=openid+email&redirect_uri={RedirectURI}"
    return redirect(cognito_login_url)

@auth_blueprint.route('/signup')
def signup():
    logger.info("Signup page accessed")
    cognito_signup_url = f"https://{CognitoDomain}/signup?client_id={CognitoClientID}&response_type=code&scope=openid+email&redirect_uri={RedirectURI}"
    return redirect(cognito_signup_url)

@main_blueprint.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        logger.error("Error: Missing code parameter")
        return "Error: Missing code parameter", 400

    token_url = f"https://{CognitoDomain}/oauth2/token"
    payload = {
        'grant_type': 'authorization_code',
        'client_id': CognitoClientID,
        'code': code,
        'redirect_uri': RedirectURI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(token_url, data=payload, headers=headers)

    if response.status_code == 200:
        tokens = response.json()
        session['id_token'] = tokens.get('id_token')
        session['access_token'] = tokens.get('access_token')
        session['refresh_token'] = tokens.get('refresh_token')
        logger.info("Successfully exchanged code for tokens")
        return redirect(url_for('auth.dashboard'))
    else:
        logger.error(f"Error exchanging code for tokens: {response.text}")
        return f"Error exchanging code for tokens: {response.text}", 400

@auth_blueprint.route('/dashboard')
def dashboard():
    if 'id_token' not in session:
        logger.warning("User tried to access dashboard without being authenticated.")
        return redirect(url_for('auth.login'))

    try:
        decoded_token = jwt.decode(session['id_token'], options={"verify_signature": False})
        email = decoded_token.get('email', 'Email not available')
        logger.info(f"User {email} accessed the dashboard")
    except jwt.DecodeError:
        email = 'Invalid token'
        logger.error("Invalid token in session")
    
    media = Media.query.order_by(Media.created_at.desc()).all()

    return render_template('dashboard.html', email=email, media=media)

@auth_blueprint.route('/logout')
def logout():
    session.clear()
    logger.info("User logged out")
    return redirect(url_for('auth.login'))
