# Test Login Credentials

## 🚀 Development Testing Accounts

The following test accounts are automatically created in the database for development and testing purposes:

### 📧 Test User 1
- **Email:** `test@example.com`
- **Password:** `test123`
- **Name:** Test User

### 📧 Test User 2
- **Email:** `demo@example.com`
- **Password:** `demo123`
- **Name:** Demo User

### 📧 Admin User
- **Email:** `admin@example.com`
- **Password:** `admin123`
- **Name:** Admin User

## 🔐 How to Use

1. **Start the backend server:**
   ```bash
   cd /home/tarun/MarketSentimentAnalysis
   python backend_api.py
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm start
   ```

3. **Navigate to the login page:**
   - Go to `http://localhost:3000/signin`
   - Or click "Sign In" from the home page

4. **Use any of the test credentials above**

## 🛡️ Security Note

⚠️ **Important:** These are test credentials only and should NOT be used in production. The passwords are stored as hashed values in the database for security.

## 🔄 Database Reset

If you need to reset the test users, simply delete the auth database file:
```bash
rm /home/tarun/MarketSentimentAnalysis/db/auth.db
```

The test users will be automatically recreated when you restart the backend server.

## 🎯 Features Available After Login

Once logged in, you'll have access to:
- ✅ Dashboard with personalized data
- ✅ Fundamental Analysis
- ✅ Stock Search and Analysis
- ✅ Portfolio Management (if implemented)
- ✅ User Settings and Preferences

## 🚫 Public Access

The following pages remain publicly accessible without login:
- ✅ Home page (`/`)
- ✅ Sectoral Analysis (`/sectoral-analysis`)
- ✅ Sign In page (`/signin`)
- ✅ Sign Up page (`/signup`) 