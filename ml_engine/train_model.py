"""
Train hate speech / cyberbullying classifier.

ALOGITHM IMPLEMENTED:
- Tokenization (NLTK)
- Stop-word removal (NLTK)
- Stemming / Lemmatization (NLTK WordNetLemmatizer)
- TF-IDF feature extraction
- Bag of Words (BoW) feature extraction
- Logistic Regression classifier
- SVM (LinearSVC) classifier
- Evaluation: Accuracy, Precision, Recall, F1-Score
"""

import os
import sys
import re
import string
import joblib
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, precision_score,
                              recall_score, f1_score, classification_report,
                              confusion_matrix)
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV


# ==================== SAMPLE TRAINING DATA ====================
# Expand this with real dataset for better accuracy

SAMPLE_DATA = [
    # --- HATE SPEECH ---
    ("I hate all people of that race they should be eliminated", "hate_speech"),
    ("Those filthy immigrants need to go back where they came from", "hate_speech"),
    ("Kill all the infidels they are subhuman vermin", "hate_speech"),
    ("We should exterminate those disgusting people from our country", "hate_speech"),
    ("Women are inferior and worthless pieces of garbage", "hate_speech"),
    ("Those terrorists deserve to die horrible deaths", "hate_speech"),
    ("That group of people are subhuman scum who ruin everything", "hate_speech"),
    ("Go back to your country you filthy animal", "hate_speech"),
    ("We need to wipe out all these vermin from our society", "hate_speech"),
    ("Those people are inferior trash that should be removed", "hate_speech"),
    ("Die you disgusting racist bigot terrorist", "hate_speech"),
    ("They are not human they are animals and should be treated as such", "hate_speech"),
    ("All those people are criminals and deserve to be locked up forever", "hate_speech"),
    ("These immigrants are destroying our country they must leave", "hate_speech"),
    ("I want to kill all members of that religion", "hate_speech"),
    ("That race is genetically inferior and causes all problems", "hate_speech"),
    ("Those people spread disease and filth wherever they go", "hate_speech"),
    ("We should ban all people of that religion from our country", "hate_speech"),

    # --- CYBERBULLYING ---
    ("Nobody likes you you should just kill yourself", "cyberbullying"),
    ("You are so ugly and fat everyone hates you loser", "cyberbullying"),
    ("Go die you pathetic piece of garbage no one wants you here", "cyberbullying"),
    ("You are a complete failure and worthless nobody cares about you", "cyberbullying"),
    ("You should be ashamed of yourself you disgusting freak", "cyberbullying"),
    ("No one wants you here leave forever and never come back", "cyberbullying"),
    ("You are so stupid and worthless your parents hate you", "cyberbullying"),
    ("I will make everyone hate you and destroy your life", "cyberbullying"),
    ("You are pathetic and nobody will ever love you", "cyberbullying"),
    ("Just end yourself already nobody would miss you", "cyberbullying"),
    ("You are a burden to everyone around you go away", "cyberbullying"),
    ("Everyone laughs at you behind your back you embarrassment", "cyberbullying"),
    ("You are the ugliest most disgusting person I have ever seen", "cyberbullying"),
    ("Your life is worthless and you should disappear forever", "cyberbullying"),
    ("Nobody wants to be your friend because you are so annoying", "cyberbullying"),
    ("You are such a loser even your family is embarrassed by you", "cyberbullying"),
    ("I hope you suffer every day for the rest of your miserable life", "cyberbullying"),
    ("You deserve to be alone because you are so ugly inside and out", "cyberbullying"),

    # --- NORMAL ---
    ("I had a great day today at the park with friends", "normal"),
    ("Just watched an amazing movie highly recommend it", "normal"),
    ("The weather is really nice this weekend perfect for outdoor activities", "normal"),
    ("Excited to start my new job next week looking forward to it", "normal"),
    ("Happy birthday to my best friend love you so much", "normal"),
    ("Just finished reading a great book the story was wonderful", "normal"),
    ("Cooking dinner for the family tonight trying a new recipe", "normal"),
    ("Looking forward to the weekend going hiking with my friends", "normal"),
    ("Great news everyone we won the game today what a match", "normal"),
    ("Thank you all for the kind words and support means a lot", "normal"),
    ("This new restaurant is absolutely delicious best food in town", "normal"),
    ("So grateful for all the support from my amazing friends", "normal"),
    ("Beautiful sunrise this morning took some amazing photos", "normal"),
    ("Finally finished my project after weeks of hard work so happy", "normal"),
    ("Going to the gym today trying to stay healthy and fit", "normal"),
    ("Just adopted a puppy she is so cute and playful", "normal"),
    ("Watching the football game tonight should be exciting", "normal"),
    ("Learning to play guitar it is challenging but so fun", "normal"),
    ("Had coffee with an old friend today caught up on everything", "normal"),
    ("The concert last night was absolutely incredible loved every moment", "normal"),
    ("Starting a new fitness routine feeling motivated and positive", "normal"),
    ("My garden is blooming so beautifully this season love it", "normal"),
]


# ==================== PREPROCESSING ====================

def download_nltk_data():
    """Download required NLTK datasets."""
    import nltk
    datasets = ['punkt', 'stopwords', 'wordnet', 'omw-1.4', 'punkt_tab']
    for d in datasets:
        try:
            nltk.download(d, quiet=True)
        except Exception:
            pass


def preprocess_text(text):
    """Full NLP preprocessing pipeline."""
    if not text:
        return ""

    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#(\w+)', r'\1', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenization
    try:
        import nltk
        tokens = nltk.word_tokenize(text)
    except Exception:
        tokens = text.split()

    # Stop-word removal (keep negations)
    try:
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words('english'))
        keep = {'no', 'not', 'nor', 'never', 'none', 'nobody',
                'nothing', 'nowhere', 'neither', 'against'}
        stop_words = stop_words - keep
        tokens = [t for t in tokens if t not in stop_words]
    except Exception:
        pass

    # Lemmatization
    try:
        from nltk.stem import WordNetLemmatizer
        lem = WordNetLemmatizer()
        tokens = [lem.lemmatize(t) for t in tokens]
    except Exception:
        pass

    return ' '.join(tokens)


# ==================== TRAINING ====================

def train_model(csv_path=None):
    print("=" * 60)
    print("TWITTERLY — HATE SPEECH DETECTION MODEL TRAINER")
    print("=" * 60)

    # Download NLTK data
    print("\n📚 Downloading NLTK data...")
    try:
        download_nltk_data()
        print("   ✅ NLTK data ready")
    except Exception as e:
        print(f"   ⚠️  NLTK download warning: {e}")

    # Load dataset
    print("\n📂 Loading dataset...")
    if csv_path and os.path.exists(csv_path):
        df = pd.read_csv(csv_path)

        # Support Kaggle format: tweet, class (0=hate, 1=offensive, 2=neither)
        if 'tweet' in df.columns and 'class' in df.columns:
            label_map = {0: 'hate_speech', 1: 'cyberbullying', 2: 'normal'}
            df['label'] = df['class'].map(label_map)
            df['text'] = df['tweet']

        # Support HatEval format
        elif 'text' in df.columns and 'HS' in df.columns:
            df['label'] = df['HS'].map({1: 'hate_speech', 0: 'normal'})

        elif 'text' not in df.columns or 'label' not in df.columns:
            print("   ❌ CSV must have 'text'+'label' OR 'tweet'+'class' columns")
            print("   Using sample data instead...")
            df = pd.DataFrame(SAMPLE_DATA, columns=['text', 'label'])
        
        print(f"   ✅ Loaded {len(df)} samples from {csv_path}")
    else:
        print("   ℹ️  No dataset provided — using built-in sample data")
        print("   💡 For better accuracy, download:")
        print("      https://www.kaggle.com/datasets/mrmorj/hate-speech-and-offensive-language-dataset")
        df = pd.DataFrame(SAMPLE_DATA, columns=['text', 'label'])

    # Preprocess
    print("\n🔧 Preprocessing text (tokenize → stopwords → lemmatize)...")
    df = df.dropna(subset=['text', 'label'])
    df['text_clean'] = df['text'].apply(preprocess_text)
    df = df[df['text_clean'].str.len() > 2]

    print(f"   ✅ {len(df)} samples after cleaning")
    print(f"   Label distribution:")
    for label, count in df['label'].value_counts().items():
        print(f"      {label}: {count}")

    X = df['text_clean'].values
    y = df['label'].values

    # Train/test split
    test_size = 0.2 if len(df) > 20 else 0.1
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
    except Exception:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

    print(f"\n   Train: {len(X_train)} | Test: {len(X_test)}")

    # ==================== FEATURE EXTRACTION ====================
    print("\n📊 Feature Extraction...")

    # TF-IDF Vectorizer (primary — as per abstract)
    print("   Building TF-IDF features...")
    tfidf_vec = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=15000,
        min_df=1,
        sublinear_tf=True,
        strip_accents='unicode',
    )
    X_train_tfidf = tfidf_vec.fit_transform(X_train)
    X_test_tfidf = tfidf_vec.transform(X_test)
    print(f"   ✅ TF-IDF features: {X_train_tfidf.shape[1]}")

    # Bag of Words Vectorizer (secondary — as per abstract)
    print("   Building Bag-of-Words features...")
    bow_vec = CountVectorizer(
        ngram_range=(1, 2),
        max_features=15000,
        min_df=1,
    )
    X_train_bow = bow_vec.fit_transform(X_train)
    X_test_bow = bow_vec.transform(X_test)
    print(f"   ✅ BoW features: {X_train_bow.shape[1]}")

    # ==================== MODEL TRAINING ====================
    print("\n🤖 Training Classifiers...")

    results = {}

    # 1. Logistic Regression with TF-IDF
    print("\n   [1/4] Logistic Regression + TF-IDF...")
    lr_model = LogisticRegression(
        max_iter=1000, C=1.0,
        class_weight='balanced', random_state=42,
        multi_class='multinomial', solver='lbfgs'
    )
    lr_model.fit(X_train_tfidf, y_train)
    lr_pred = lr_model.predict(X_test_tfidf)
    lr_acc = accuracy_score(y_test, lr_pred)
    lr_f1 = f1_score(y_test, lr_pred, average='weighted', zero_division=0)
    results['LR_TFIDF'] = {
        'model': lr_model, 'vectorizer': tfidf_vec,
        'accuracy': lr_acc, 'f1': lr_f1,
        'predictions': lr_pred, 'name': 'Logistic Regression + TF-IDF'
    }
    print(f"      Accuracy: {lr_acc:.4f} | F1: {lr_f1:.4f}")

    # 2. Logistic Regression with BoW
    print("   [2/4] Logistic Regression + Bag of Words...")
    lr_bow = LogisticRegression(
        max_iter=1000, C=1.0,
        class_weight='balanced', random_state=42,
        multi_class='multinomial', solver='lbfgs'
    )
    lr_bow.fit(X_train_bow, y_train)
    lr_bow_pred = lr_bow.predict(X_test_bow)
    lr_bow_acc = accuracy_score(y_test, lr_bow_pred)
    lr_bow_f1 = f1_score(y_test, lr_bow_pred, average='weighted', zero_division=0)
    results['LR_BOW'] = {
        'model': lr_bow, 'vectorizer': bow_vec,
        'accuracy': lr_bow_acc, 'f1': lr_bow_f1,
        'predictions': lr_bow_pred, 'name': 'Logistic Regression + BoW'
    }
    print(f"      Accuracy: {lr_bow_acc:.4f} | F1: {lr_bow_f1:.4f}")

    # 3. SVM (LinearSVC) with TF-IDF
    print("   [3/4] SVM (LinearSVC) + TF-IDF...")
    svm_base = LinearSVC(
        C=1.0, class_weight='balanced',
        random_state=42, max_iter=2000
    )
    # Wrap with CalibratedClassifierCV for predict_proba support
    svm_model = CalibratedClassifierCV(svm_base, cv=min(3, len(set(y_train))))
    svm_model.fit(X_train_tfidf, y_train)
    svm_pred = svm_model.predict(X_test_tfidf)
    svm_acc = accuracy_score(y_test, svm_pred)
    svm_f1 = f1_score(y_test, svm_pred, average='weighted', zero_division=0)
    results['SVM_TFIDF'] = {
        'model': svm_model, 'vectorizer': tfidf_vec,
        'accuracy': svm_acc, 'f1': svm_f1,
        'predictions': svm_pred, 'name': 'SVM (LinearSVC) + TF-IDF'
    }
    print(f"      Accuracy: {svm_acc:.4f} | F1: {svm_f1:.4f}")

    # 4. SVM with BoW
    print("   [4/4] SVM (LinearSVC) + Bag of Words...")
    svm_bow_base = LinearSVC(
        C=1.0, class_weight='balanced',
        random_state=42, max_iter=2000
    )
    svm_bow_model = CalibratedClassifierCV(svm_bow_base, cv=min(3, len(set(y_train))))
    svm_bow_model.fit(X_train_bow, y_train)
    svm_bow_pred = svm_bow_model.predict(X_test_bow)
    svm_bow_acc = accuracy_score(y_test, svm_bow_pred)
    svm_bow_f1 = f1_score(y_test, svm_bow_pred, average='weighted', zero_division=0)
    results['SVM_BOW'] = {
        'model': svm_bow_model, 'vectorizer': bow_vec,
        'accuracy': svm_bow_acc, 'f1': svm_bow_f1,
        'predictions': svm_bow_pred, 'name': 'SVM + BoW'
    }
    print(f"      Accuracy: {svm_bow_acc:.4f} | F1: {svm_bow_f1:.4f}")

    # ==================== SELECT BEST MODEL ====================
    print("\n🏆 Model Comparison:")
    print("-" * 50)
    best_key = max(results, key=lambda k: results[k]['f1'])

    for key, res in results.items():
        marker = " ← BEST" if key == best_key else ""
        print(f"   {res['name']:<35} Acc: {res['accuracy']:.4f}  F1: {res['f1']:.4f}{marker}")

    best = results[best_key]
    print(f"\n✅ Best Model: {best['name']}")

    # ==================== EVALUATION METRICS ====================
    print("\n📈 Detailed Evaluation (Best Model):")
    print("-" * 50)

    labels = sorted(list(set(y)))
    acc = accuracy_score(y_test, best['predictions'])
    prec = precision_score(y_test, best['predictions'], average='weighted', zero_division=0)
    rec = recall_score(y_test, best['predictions'], average='weighted', zero_division=0)
    f1 = f1_score(y_test, best['predictions'], average='weighted', zero_division=0)

    print(f"   Accuracy  : {acc:.4f} ({acc*100:.1f}%)")
    print(f"   Precision : {prec:.4f}")
    print(f"   Recall    : {rec:.4f}")
    print(f"   F1-Score  : {f1:.4f}")

    print("\n   Per-class Report:")
    print(classification_report(y_test, best['predictions'],
                                 labels=labels, zero_division=0))

    # ==================== SAVE MODEL ====================
    model_dir = os.path.join(os.path.dirname(__file__), 'model')
    os.makedirs(model_dir, exist_ok=True)

    joblib.dump(best['model'], os.path.join(model_dir, 'classifier.pkl'))
    joblib.dump(best['vectorizer'], os.path.join(model_dir, 'vectorizer.pkl'))

    # Save metrics for admin dashboard display
    metrics = {
        'best_model_name': best['name'],
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'all_models': {k: {'name': v['name'], 'accuracy': round(v['accuracy'], 4),
                           'f1': round(v['f1'], 4)} for k, v in results.items()},
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'labels': labels,
    }
    joblib.dump(metrics, os.path.join(model_dir, 'metrics.pkl'))

    print(f"\n💾 Model saved to: {model_dir}/")
    print(f"   Files: classifier.pkl, vectorizer.pkl, metrics.pkl")
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)

    return metrics


if __name__ == '__main__':
    csv_path = sys.argv[1] if len(sys.argv) > 1 else None
    train_model(csv_path)
