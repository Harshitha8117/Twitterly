"""
ML Engine for hate speech and cyberbullying detection.
Uses NLTK preprocessing + TF-IDF + SVM/Logistic Regression.
"""
import re
import os
import string

# ==================== TEXT PREPROCESSING ====================

def preprocess_text(text):

    if not text:
        return ""

    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Remove URLs, mentions, hashtag symbols, punctuation
    text = re.sub(r'http\S+|www\S+', '', text)       # remove URLs
    text = re.sub(r'@\w+', '', text)                   # remove mentions
    text = re.sub(r'#(\w+)', r'\1', text)              # keep hashtag words
    text = re.sub(r'[^\w\s]', ' ', text)               # remove punctuation
    text = re.sub(r'\d+', '', text)                    # remove numbers
    text = re.sub(r'\s+', ' ', text).strip()           # normalize spaces

    # Step 3: Tokenization
    try:
        import nltk
        tokens = nltk.word_tokenize(text)
    except Exception:
        tokens = text.split()

    # Step 4: Stop-word removal
    try:
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words('english'))
        # Keep negations and important words
        keep_words = {'no', 'not', 'nor', 'never', 'none', 'nobody',
                      'nothing', 'nowhere', 'neither', 'against'}
        stop_words = stop_words - keep_words
        tokens = [t for t in tokens if t not in stop_words]
    except Exception:
        pass

    # Step 5: Lemmatization
    try:
        from nltk.stem import WordNetLemmatizer
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(t) for t in tokens]
    except Exception:
        pass

    return ' '.join(tokens)


# ==================== MODEL LOADING ====================

_model_cache = {}

def load_model():
 
    if _model_cache:
        return _model_cache.get('classifier'), _model_cache.get('vectorizer')

    try:
        import joblib
        from django.conf import settings
        model_path = str(settings.ML_MODEL_PATH)

        clf_path = os.path.join(model_path, 'classifier.pkl')
        vec_path = os.path.join(model_path, 'vectorizer.pkl')

        if os.path.exists(clf_path) and os.path.exists(vec_path):
            _model_cache['classifier'] = joblib.load(clf_path)
            _model_cache['vectorizer'] = joblib.load(vec_path)
            return _model_cache['classifier'], _model_cache['vectorizer']
    except Exception as e:
        pass

    return None, None


# ==================== KEYWORD FALLBACK ====================

HATE_KEYWORDS = [
    'hate', 'kill', 'die', 'worthless', 'disgusting', 'trash', 'garbage',
    'racist', 'sexist', 'bigot', 'terrorist', 'inferior', 'subhuman',
    'filth', 'scum', 'vermin', 'exterminate', 'eliminate', 'destroy them',
    'get rid of', 'wipe out', 'they should die', 'go back', 'filthy immigrants'
]

CYBERBULLYING_KEYWORDS = [
    'ugly', 'fat', 'nobody likes you', 'kill yourself', 'kys',
    'no one cares', 'you should die', 'end yourself', 'loser', 'pathetic',
    'freak', 'weirdo', 'nobody wants you', 'go die', 'you are nothing',
    'you suck', 'you are stupid', 'worthless piece', 'embarrassment',
    'failure', 'everyone hates you', 'we hate you', 'you deserve nothing'
]


def keyword_detection(text):
   
    text_lower = text.lower()
    hate_count = sum(1 for kw in HATE_KEYWORDS if kw in text_lower)
    cyber_count = sum(1 for kw in CYBERBULLYING_KEYWORDS if kw in text_lower)

    if hate_count == 0 and cyber_count == 0:
        return 'normal', 0.95

    if hate_count >= cyber_count:
        return 'hate_speech', min(0.60 + hate_count * 0.10, 0.95)
    else:
        return 'cyberbullying', min(0.60 + cyber_count * 0.10, 0.95)


# ==================== MAIN ANALYSIS FUNCTION ====================

def analyze_text(text):

    if not text or len(text.strip()) < 3:
        return {'label': 'normal', 'confidence': 1.0, 'is_harmful': False}

    # Step 1: Preprocess
    cleaned = preprocess_text(text)

    # Step 2: Try ML model
    clf, vec = load_model()
    label, confidence = None, None

    if clf and vec:
        try:
            features = vec.transform([cleaned])
            label = clf.predict(features)[0]
            # Get confidence from predict_proba if available
            if hasattr(clf, 'predict_proba'):
                proba = clf.predict_proba(features)[0]
                confidence = float(max(proba))
            elif hasattr(clf, 'decision_function'):
                # For SVM - convert decision score to confidence
                decision = clf.decision_function(features)[0]
                if hasattr(decision, '__len__'):
                    confidence = float(max(abs(d) for d in decision))
                    confidence = min(confidence / 2.0, 0.99)
                else:
                    confidence = min(abs(float(decision)) / 2.0, 0.99)
                confidence = max(confidence, 0.55)
            else:
                confidence = 0.80
        except Exception:
            label, confidence = None, None

    # Step 3: Fallback to keyword detection
    if label is None:
        label, confidence = keyword_detection(text)

    is_harmful = label in ('hate_speech', 'cyberbullying')

    return {
        'label': label,
        'confidence': round(float(confidence), 4),
        'is_harmful': is_harmful
    }
