# 🚀 Twitterly — Intelligent Twitter Clone with Hate Speech Detection

A full-stack social media platform inspired by Twitter, enhanced with **real-time NLP-powered moderation** to detect hate speech and cyberbullying. Built for scalability, extensibility, and responsible digital interaction.

---

## 🌟 Overview

**Twitterly** combines a familiar microblogging experience with an integrated **machine learning moderation engine**, enabling safer online communities through automated content analysis and admin-driven governance.

---

## ✨ Core Capabilities

### 👤 User Experience

* Authentication (Register / Login / Logout)
* Profile customization (bio, avatar, cover, location, website)
* Tweet system (text + image, 280 characters)
* Like, Retweet, Quote Tweet
* Threaded replies (conversation chains)
* Bookmarking system
* Follow / Unfollow users
* Personalized home feed
* Explore page (hashtags + search)
* Real-time notifications (likes, replies, follows, warnings)
* Hashtag auto-detection and indexing

---

### 🧠 AI Moderation Engine

* Real-time **hate speech detection** on tweets
* **Cyberbullying detection** in replies/comments
* Confidence scoring for predictions
* Keyword-based fallback (when model unavailable)
* Custom dataset training support (CSV input)

---

### 🛡️ Admin Control System

* Analytics dashboard (activity + moderation stats)
* Flagged content queue (real-time tracking)
* Moderation actions:

  * Dismiss (false positive)
  * Warn user (notification + strike count)
  * Delete content
  * Block / Unblock users
* Advanced user management (search + filtering)

---

## 🧱 Architecture

```
User Action → Django Backend → ML Engine → Classification
        ↓                         ↓
     Database ← Moderation Logic ← Flag System
        ↓
   Admin Dashboard / Notifications
```

---

## 🛠️ Tech Stack

| Layer    | Technology                                      |
| -------- | ----------------------------------------------- |
| Backend  | Django 4.2 (Python 3.11)                        |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript            |
| Database | SQLite (Dev) / MySQL (Production)               |
| ML/NLP   | Scikit-learn, NLTK, TF-IDF, Logistic Regression |
| Auth     | Django Custom User Model                        |

---

## ⚙️ Installation & Setup

### 🔹 Option 1: Automated (Linux / Mac)

```bash
cd twitter_clone
chmod +x setup_and_run.sh
./setup_and_run.sh
```

---

### 🔹 Option 2: Manual Setup

#### 1. Install Dependencies

```bash
pip install Django scikit-learn nltk pandas numpy Pillow django-crispy-forms crispy-bootstrap5 joblib
```

#### 2. Download NLP Resources

```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
```

#### 3. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 4. Create Admin User

```bash
python manage.py createsuperuser
```

#### 5. Train ML Model (Optional but Recommended)

```bash
python ml_engine/train_model.py
```

Or with dataset:

```bash
python ml_engine/train_model.py path/to/dataset.csv
```

#### 6. Run Server

```bash
python manage.py runserver
```

---

## 🌐 Application Routes

| URL                     | Description       |
| ----------------------- | ----------------- |
| `/`                     | Home Feed         |
| `/accounts/register/`   | User Registration |
| `/accounts/login/`      | Login             |
| `/explore/`             | Explore & Search  |
| `/notifications/`       | Notifications     |
| `/bookmarks/`           | Saved Tweets      |
| `/accounts/<username>/` | User Profile      |
| `/admin-portal/`        | Admin Dashboard   |

---

## 📂 Project Structure

```
twitter_clone/
├── accounts/          # Authentication, profiles, follow system
├── tweets/            # Core tweet logic
├── notifications/     # Notification engine
├── admin_portal/      # Moderation dashboard
├── ml_engine/         # NLP + ML pipeline
│   ├── predictor.py
│   ├── train_model.py
│   └── model/
├── templates/         # UI templates
├── static/            # CSS, JS, assets
├── media/             # Uploaded content
└── twitter_clone/     # Core settings
```

---

## 🤖 Machine Learning Pipeline

### Workflow

1. User submits content
2. `analyze_text()` processes input
3. Preprocessing:

   * Lowercasing
   * URL removal
   * Stopword filtering
   * Lemmatization
4. TF-IDF vectorization
5. Logistic Regression classification:

   * `normal`
   * `hate_speech`
   * `cyberbullying`
6. If harmful:

   * Flag created
   * Admin notified

---

## 📊 Model Improvement

Train with real datasets for higher accuracy:

* Kaggle Hate Speech Dataset
* HatEval Dataset

Expected format:

```
text,label
"This is abusive",hate_speech
```

---

## 🔐 Admin Privileges Setup

```bash
python manage.py shell
```

```python
from accounts.models import User
u = User.objects.get(username='yourusername')
u.is_staff = True
u.save()
```

---

## 🚀 Production Deployment

Recommended stack:

* Gunicorn (WSGI server)
* Nginx (reverse proxy)
* MySQL / PostgreSQL
* WhiteNoise (static file serving)

⚠️ Important:

* Set `DEBUG = False`
* Configure `ALLOWED_HOSTS`
* Secure `SECRET_KEY`
* Use environment variables

---

## 🧭 Design Philosophy

This project is not just a clone—it's a **reimagined social platform**:

* Content ≠ just publishing → it's **risk-evaluated communication**
* Moderation ≠ reactive → it's **predictive and proactive**
* Admin ≠ passive → it's **decision intelligence**

---

## 📌 Future Enhancements

* Real-time WebSocket feeds
* Transformer-based NLP models (BERT)
* Shadow banning & trust scores
* AI-assisted moderation suggestions
* Distributed microservices architecture

---

## 🤝 Contributing

Pull requests are welcome. For major changes:

* Open an issue first
* Propose architectural improvements
* Align with project direction

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 💡 Final Thought

Twitterly isn’t just a clone.
It’s a **prototype for responsible social networks**—where AI doesn’t replace humans, but amplifies better decisions.


