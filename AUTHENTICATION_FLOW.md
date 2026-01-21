# PlantCare AI - Authentication Flow Documentation

## Issues Found & Fixed

### 1. **Empty Authentication Routes**
**Problem:** signup() and signin() functions were empty (just `pass` statement)
**Impact:** Users could not create accounts or log in; authentication was completely broken

**Solution:** Implemented proper authentication logic:
```python
# SIGNUP: Creates new user account with password hashing
- Validates form inputs
- Checks if email already exists
- Hashes password using bcrypt
- Stores user in MySQL database

# SIGNIN: Authenticates user and creates session
- Validates email and password
- Uses bcrypt to verify password
- Creates session with user_id, username, and name
- Redirects to home on success
```

---

### 2. **No Login Protection on Routes**
**Problem:** 
- Home page (/) was directly accessible without login
- Users could skip authentication

**Solution:** Added login_required decorator:
```python
@app.route('/')
def home():
    if 'logged_in' not in session:
        return redirect(url_for('signin'))
    return render_template('index.html')

@app.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    # Protected route
```

---

### 3. **Wrong Weather API Key Variable**
**Problem:** app.py was looking for `OPENWEATHER_API_KEY` but .env has `OPENWEATHERMAP_API_KEY`
**Solution:** Fixed to use correct environment variable:
```python
weather_tool = WeatherForecastTool(api_key=os.getenv("OPENWEATHERMAP_API_KEY"))
```

---

### 4. **Missing Navbar with User Info**
**Problem:** index.html and analyze.html didn't show logged-in user or logout button
**Solution:** Updated navbar in both templates:
```html
<nav class="navbar mb-4">
    <div class="container-fluid d-flex justify-content-between align-items-center">
        <span class="navbar-brand mb-0 h1">🌿 PlantCare AI Consultant</span>
        <div>
            <span class="me-3">Welcome, <strong>{{ session.name }}</strong></span>
            <a href="{{ url_for('logout') }}" class="btn btn-sm btn-outline-light">Logout</a>
        </div>
    </div>
</nav>
```

---

### 5. **Form Submission Issue**
**Problem:** index.html form was submitting to itself instead of /analyze route
**Solution:** Added action attribute to form:
```html
<form method="POST" enctype="multipart/form-data" action="{{ url_for('analyze') }}">
```

---

## Authentication Flow (Fixed)

### Step 1: User Visits App
```
http://localhost:5000/
    ↓
Session check: 'logged_in' not in session?
    ↓ YES
Redirect to signin page
    ↓ NO
Show home page (index.html)
```

### Step 2: First Time Users - Signup
```
/signup (GET)
    ↓
Show signup form
    ↓
User fills: username, email, password
    ↓
Submit (POST)
    ↓
Check if email exists → If yes, show error
    ↓
Hash password with bcrypt
    ↓
Store in MySQL database
    ↓
Redirect to signin with success message
```

### Step 3: Login - Signin
```
/signin (GET)
    ↓
Show signin form
    ↓
User enters: email, password
    ↓
Submit (POST)
    ↓
Find user by email in database
    ↓
Verify password using bcrypt
    ↓
If match:
    - Set session['logged_in'] = True
    - Set session['user_id'], session['name']
    - Redirect to home (index.html)
    ↓
If no match:
    - Show "Invalid email or password" error
    - Redirect to signin
```

### Step 4: Analyze Plant
```
User on index.html
    ↓
Upload image + Enter city
    ↓
Form POSTs to /analyze
    ↓
@login_required checks session
    ↓ NOT LOGGED IN
Redirect to signin
    ↓ LOGGED IN
Predict disease
    ↓
Fetch weather data
    ↓
Generate AI advice using LLM
    ↓
Return analyze.html with results
```

### Step 5: Logout
```
Click "Logout" button
    ↓
/logout route
    ↓
session.clear()
    ↓
Redirect to signin
```

---

## Files Modified

1. **app.py**
   - ✅ Implemented signup() function with user registration
   - ✅ Implemented signin() function with authentication
   - ✅ Updated home() with login check
   - ✅ Fixed weather API key variable name
   - ✅ @login_required decorator on /analyze route

2. **templates/index.html**
   - ✅ Updated navbar to show logged-in user
   - ✅ Added logout button
   - ✅ Fixed form action to POST to /analyze

3. **templates/analyze.html**
   - ✅ Updated navbar to show logged-in user
   - ✅ Added logout button

---

## Database Requirements

Your MySQL database needs a `users` table:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Environment Variables (.env)

Required:
```
GROQ_API_KEY=your_groq_api_key
OPENWEATHERMAP_API_KEY=your_weather_api_key
MYSQL_HOST=localhost
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DB=plantcare_ai
SECRET_KEY=your_secret_key
```

---

## Testing the Flow

1. **Start app:**
   ```bash
   python app.py
   ```

2. **Visit:** http://localhost:5000/
   - Should redirect to signin

3. **Sign up:**
   - Click "Sign Up"
   - Create account with email/password
   - Should redirect to signin with success message

4. **Sign in:**
   - Enter email and password
   - Should redirect to home and show "Welcome, [username]"

5. **Analyze:**
   - Upload plant image
   - Enter city name
   - Click Analyze
   - Should show results with weather and AI advice

6. **Logout:**
   - Click "Logout" button
   - Should redirect to signin

---

## Summary

✅ Complete authentication flow implemented
✅ Login protection on protected routes
✅ User registration with password hashing
✅ Session management
✅ Proper navbar with user info
✅ Weather API integration fixed
✅ Form submission routing fixed
