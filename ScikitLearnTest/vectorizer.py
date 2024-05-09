from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
#nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
courpus = [ 'this is document one map this is the second document mapping, and this is the third one maps.,Is this the first document documents and document']
stemmer = PorterStemmer()
custom_stopwords = stopwords.words('english')
def tokenize_and_stem(text):
    tokens = nltk.word_tokenize(text)
    stemmed_tokens = [stemmer.stem(token)for token in tokens if token.lower() not in custom_stopwords]
    return stemmed_tokens

vectorizer = TfidfVectorizer(tokenizer=tokenize_and_stem)
x = vectorizer.fit_transform(courpus)
print(vectorizer.get_stop_words())
print(vectorizer.get_feature_names_out())
print(x.shape)