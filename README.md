# 🐦 Twitterly — Twitter Clone with Hate Speech Detection

A full-featured Twitter-like social media application built with Django, featuring real-time hate speech and cyberbullying detection using NLP/ML.

---

## ✨ Features

### User Features
- ✅ Register / Login / Logout
- ✅ Edit profile (bio, avatar, cover photo, location, website)
- ✅ Post tweets (text + image, 280 chars)
- ✅ Like / Unlike tweets
- ✅ Retweet / Quote tweet
- ✅ Reply to tweets (threaded comments)
- ✅ Bookmark tweets
- ✅ Follow / Unfollow users
- ✅ Home feed (followed users' tweets)
- ✅ Explore page (trending hashtags + search)
- ✅ Notifications (likes, follows, replies, warnings)
- ✅ Hashtag support (#tag auto-detection)

### ML/NLP Features
- ✅ Automatic hate speech detection on every tweet
- ✅ Cyberbullying detection on comments too
- ✅ Confidence score for each detection
- ✅ Keyword-based fallback when model not trained
- ✅ Train with your own dataset (CSV)

### Admin Portal
- ✅ Dashboard with stats and charts
- ✅ Pending flag queue with real-time count
- ✅ Review flagged content
- ✅ **Dismiss** (false positive)
- ✅ **Warn user** (sends notification + increments warning count)
- ✅ **Delete content** (removes post + notifies user)
- ✅ **Block user** (suspends account)
- ✅ Unblock users
- ✅ User management with search + filter

---

## 🚀 Quick Start

### Option 1: Auto Setup (Linux/Mac)
```bash
cd twitter_clone
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### Option 2: Manual Setup (Windows or any OS)

**Step 1: Install Python packages**
```bash
pip install Django scikit-learn nltk pandas numpy Pillow django-crispy-forms crispy-bootstrap5 joblib
```

**Step 2: Download NLTK data**
```python
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
```

**Step 3: Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Step 4: Create admin superuser**
```bash
python manage.py createsuperuser
```
> Set `is_staff=True` — this gives you access to the Admin Portal at `/admin-portal/`

**Step 5: Train ML model (optional)**
```bash
# With sample data (basic accuracy):
python ml_engine/train_model.py

# With Kaggle dataset (better accuracy):
# Download: https://www.kaggle.com/datasets/mrmorj/hate-speech-and-offensive-language-dataset
python ml_engine/train_model.py path/to/dataset.csv
```

**Step 6: Run server**
```bash
python manage.py runserver
```

---

## 📍 URLs

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Home feed |
| `http://127.0.0.1:8000/accounts/register/` | Register |
| `http://127.0.0.1:8000/accounts/login/` | Login |
| `http://127.0.0.1:8000/explore/` | Explore / Search |
| `http://127.0.0.1:8000/notifications/` | Notifications |
| `http://127.0.0.1:8000/bookmarks/` | Bookmarks |
| `http://127.0.0.1:8000/accounts/<username>/` | User profile |
| `http://127.0.0.1:8000/admin-portal/` | Admin Dashboard |
| `http://127.0.0.1:8000/admin-portal/flagged/` | Flagged content |
| `http://127.0.0.1:8000/admin-portal/users/` | User management |

---

## 📁 Project Structure

```
twitter_clone/
├── accounts/          # User auth, profiles, follow system
├── tweets/            # Tweets, likes, retweets, bookmarks, hashtags
├── notifications/     # Notification system
├── admin_portal/      # Custom admin dashboard
├── ml_engine/         # NLP + ML detection engine
│   ├── predictor.py   # Main detection function
│   ├── train_model.py # Train ML model
│   └── model/         # Saved model files (after training)
├── templates/         # HTML templates
├── static/            # CSS, JS, Images
│   ├── css/style.css
│   └── js/app.js
└── twitter_clone/     # Django project settings
```

---

## 🤖 ML Model

### How it works:
1. User posts a tweet
2. `ml_engine/predictor.py` → `analyze_text()` is called
3. Text is cleaned (lowercase, remove URLs, stopwords, lemmatize)
4. TF-IDF vectorization
5. Classification: `normal` / `hate_speech` / `cyberbullying`
6. If harmful → `FlagReport` created → Admin alerted

### Improving accuracy:
Download a real dataset and retrain:
- **Kaggle Hate Speech Dataset**: https://www.kaggle.com/datasets/mrmorj/hate-speech-and-offensive-language-dataset
- **HatEval**: https://competitions.codalab.org/competitions/19935
- Any CSV with columns: `text`, `label` (normal/hate_speech/cyberbullying)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11 + Django 4.2 |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Database | SQLite (dev) / MySQL (prod) |
| ML/NLP | Scikit-learn, NLTK, TF-IDF, Logistic Regression |
| Auth | Django built-in + custom User model |

---

## 🔐 Make a User Admin

```bash
python manage.py shell
>>> from accounts.models import User
>>> u = User.objects.get(username='yourusername')
>>> u.is_staff = True
>>> u.save()
```

---

## 📝 Notes

- Images are stored in `media/` folder
- Static files served by Django in development
- For production, use Nginx + Gunicorn + WhiteNoise
- Change `SECRET_KEY` in `settings.py` before deployment
