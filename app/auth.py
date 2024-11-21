import os
from flask import Blueprint, request, session, redirect, url_for, render_template
import requests
import jwt
from app.models import Media

auth_blueprint = Blueprint('auth', __name__)
main_blueprint = Blueprint('main', __name__)

CognitoClientID = os.getenv("COGNITO_CLIENT_ID", "32hl71n1am3l8evck3k5oeka8g")
CognitoDomain = os.getenv("COGNITO_DOMAIN", "kibe.auth.us-east-2.amazoncognito.com")
RedirectURI = os.getenv("REDIRECT_URI", "http://localhost:5000/callback")
print(CognitoClientID, CognitoDomain, RedirectURI)


@main_blueprint.route('/')
def home():
    return render_template('index.html')

@auth_blueprint.route('/login')
def login():
    cognito_login_url = f"https://{CognitoDomain}/login?client_id={CognitoClientID}&response_type=code&scope=openid+email&redirect_uri={RedirectURI}"
    return redirect(cognito_login_url)

@auth_blueprint.route('/signup')
def signup():
    cognito_signup_url = f"https://{CognitoDomain}/signup?client_id={CognitoClientID}&response_type=code&scope=openid+email&redirect_uri={RedirectURI}"
    return redirect(cognito_signup_url)

@main_blueprint.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
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
        return redirect(url_for('auth.dashboard'))
    else:
        return f"Error exchanging code for tokens: {response.text}", 400

@auth_blueprint.route('/dashboard')
def dashboard():
    if 'id_token' not in session:
        return redirect(url_for('auth.login'))

    try:
        decoded_token = jwt.decode(session['id_token'], options={"verify_signature": False})
        email = decoded_token.get('email', 'Email not available')
    except jwt.DecodeError:
        email = 'Invalid token'

    # Fetch media for the logged-in user
    media = Media.query.order_by(Media.created_at.desc()).all()



    return render_template('dashboard.html', email=email, media=media)

@auth_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
