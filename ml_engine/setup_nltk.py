
import nltk

print("Downloading NLTK data...")
packages = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']
for pkg in packages:
    try:
        nltk.download(pkg, quiet=False)
        print(f"  ✅ {pkg}")
    except Exception as e:
        print(f"  ⚠️  {pkg}: {e}")

print("\nDone! NLTK data ready.")
