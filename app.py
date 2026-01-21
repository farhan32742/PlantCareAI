import os
import json
import markdown
import numpy as np
from functools import wraps
import cv2
import sys
from pathlib import Path

# Flask and extensions
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

# AI and ML libraries
import tensorflow as tf 
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# --- ADD PATH FOR CUSTOM MODULES ---
ai_app_src = Path(__file__).parent / "apps" / "AI_app" / "src"
sys.path.insert(0, str(ai_app_src))

# --- IMPORT YOUR CUSTOM MODULES ---
from PlantCare_AI.utils.model_loader import ModelLoader
from PlantCare_AI.utils.weather_info import WeatherForecastTool
from PlantCare_AI.prompt_library.prompts import PLANT_CARE_PROMPT

load_dotenv()

app = Flask(__name__)

# --- CONFIGURATIONS ---
# --- CONFIGURATIONS ---
app.config['SECRET_KEY'] = '1234488%^$hra'
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DATABASE')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- INITIALIZE EXTENSIONS ---
mysql = MySQL(app)
bcrypt = Bcrypt(app)

# --- INITIALIZE AI & WEATHER TOOLS ---

# 1. Load LLM using your ModelLoader
try:
    llm_loader = ModelLoader(model_provider="groq")
    llm = llm_loader.load_llm()
except Exception as e:
    print(f"Error loading LLM: {e}")
    llm = None

# 2. Load Weather Tool
weather_tool = WeatherForecastTool(api_key=os.getenv("OPENWEATHERMAP_API_KEY"))

# 3. Load Disease Model
try:
    model = tf.keras.models.load_model('final-plant-disease-detection-model.keras')
    with open('class_names.json', 'r') as f:
        class_names = json.load(f)
    if isinstance(class_names, dict):
        class_names = [class_names[str(i)] for i in range(len(class_names))]
except Exception as e:
    print(f"Error loading AI model: {e}")
    model = None

# --- HELPER FUNCTIONS ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None: return None
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (224, 224))
    return np.expand_dims(img_resized, axis=0)

def predict_disease(img_path):
    if model is None: return "Model not loaded", 0.0
    processed_img = preprocess_image(img_path)
    if processed_img is None: return "Processing failed", 0.0
    predictions = model.predict(processed_img)
    idx = np.argmax(predictions[0])
    return class_names[idx], np.max(predictions[0])

def get_combined_advice(disease_name, city):
    if not llm: return "AI advice unavailable."
    
    # Fetch Weather
    weather_data = weather_tool.get_current_weather(city)
    forecast_data = weather_tool.get_forecast_weather(city)
    
    weather_summary = f"Weather in {city}: {weather_data.get('weather', [{}])[0].get('description', 'N/A')}, " \
                      f"Temp: {weather_data.get('main', {}).get('temp')}°C. "
    
    # Combine everything using your prompt
    clean_name = disease_name.replace('___', ' ').replace('_', ' ')
    chain = PLANT_CARE_PROMPT | llm | StrOutputParser()
    
    return chain.invoke({
        "disease": clean_name,
        "weather_data": weather_summary
    })

# --- ROUTES ---

@app.route('/')
def home():
    # If user is not logged in, redirect to signin
    if 'logged_in' not in session:
        return redirect(url_for('signin'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullName = request.form.get('fullName')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        
        # Validation
        if not fullName or not email or not password or not confirm_password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))
        
        try:
            # Check if user exists
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
            
            if user:
                flash('Email already registered!', 'danger')
                return redirect(url_for('signup'))
            
            # Hash password
            hashed_password = bcrypt.generate_password_hash(password)
            
            # Insert new user
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                         (fullName, email, hashed_password))
            mysql.connection.commit()
            cursor.close()
            
            flash('Account created successfully! Please sign in.', 'success')
            return redirect(url_for('signin'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('signup'))
    
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password required!', 'danger')
            return redirect(url_for('signin'))
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
            cursor.close()
            
            if user and bcrypt.check_password_hash(user['password'], password):  # Use DictCursor
                session['logged_in'] = True
                session['user_id'] = user['id']
                session['username'] = user['name']
                session['name'] = user['name']
                flash(f'Welcome {user["name"]}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password!', 'danger')
                return redirect(url_for('signin'))
        except Exception as e:
            flash(f'Error 3: {str(e)}', 'danger')
            return redirect(url_for('signin'))
    
    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))

@app.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    if request.method == 'POST':
        city = request.form.get('city')  # NEW: Get city from form
        file = request.files.get('file')

        if file and allowed_file(file.filename) and city:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 1. Prediction
            disease, confidence = predict_disease(filepath)
            
            # 2. Weather & AI Advice (Using your new modules)
            # Fetch current weather
            weather_data = weather_tool.get_current_weather(city)
            weather_summary = f"{weather_data['weather'][0]['description'].capitalize()}, {weather_data['main']['temp']}°C" if 'main' in weather_data else "Weather data unavailable"

            # 3. Generate combined advice using prompt
            chain = PLANT_CARE_PROMPT | llm | StrOutputParser()
            advice_md = chain.invoke({
                "disease": disease.replace('___', ' ').replace('_', ' '),
                "weather_data": weather_summary
            })

            return render_template('analyze.html',
                                   filename=filename,
                                   disease=disease.replace('___', ' - ').replace('_', ' '),
                                   confidence=f"{round(confidence * 100, 2)}%",
                                   weather=weather_summary,
                                   city=city,
                                   remedy=markdown.markdown(advice_md))
    
    return render_template('analyze.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)