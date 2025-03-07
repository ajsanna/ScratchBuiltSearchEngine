'''
Search Engine Program Frontend Terminal Application
By: Alexander Sanna
Created on: May 9th, 2024
'''

'''
Description: 
    This is the front end app used to query the database and return results to the user based on user's input. 
    This works by first using SK-Learn's vectorizer with our own built tokenizer/stemmer utilizing NLTK library.
    This step will create the TF-IDF matrix to rank with when the program collects the query. 
    We then run the query through the same stem/stopword vectorization and flatten. 
    Then, using cosine similarity via SK-Learn we can compute similarity scores utilizing our matrix tfidf scores.
    The list is sorted by descending order for the most accurate results first, and returned to main. 
    Return Data is organized and printed to the screen. Built in loop to support multiple queries/session. 
    
    --- For backend related code including web scraping and data collection -> Reference Parser_1.py
    With any questions please email ajsanna@yahoo.com
'''

# imports: Lines 23-29
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import ssl
from pymongo import MongoClient

# Create SSL context for NLTK downloads
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Objects for lemmatizing later on
stemmer = PorterStemmer()
custom_stopwords = stopwords.words('english')

'''
    This is our custom tokenizer using NLTK library. 
    This works by taking in raw text in String format, tokenizing, removing stopwords and stemming.
    Returns processed input in the form of a String array. 
'''
def tokenize_and_stem(text):
    # Simple word splitting and stemming
    words = text.lower().split()
    stemmed_tokens = [stemmer.stem(word) for word in words if word not in custom_stopwords]
    return stemmed_tokens

'''
    Connect to the database to access data stored. 
'''
def connectionDataBase():
    client = MongoClient("mongodb://localhost:27017")
    db = client["Final_Project"]
    return db

'''
    Main search engine method designed to rank documents based on query and tfidf matrix.
    Takes query and uses cosine similarity to compare the query input to the matrix of stored values. 
    Orders a list of relevant documents and returns. 
'''
def search_engine(query, tfidf_matrix, documents, vectorizer):
    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    sorted_results = similarities.argsort()[::-1]
    sorted_documents = [documents[i] for i in sorted_results]
    return sorted_documents

'''
    This is the main method that creates our tfidf matrix for future query comparisons. 
    This works by sending the documents to be processed by our SK-Learn vectorizer, using 
    our prebuilt tokenizer that also utilizes NLTK Library functions. 
    This also prints some helpful design aspects for user view. 
    Returns TFIDF matrix and the vectorizer object. 
'''
def preprocess_text_data(texts):
    vectorizer = TfidfVectorizer(tokenizer = tokenize_and_stem)
    tfidf_matrix = vectorizer.fit_transform(texts)
    print("\n\n\n\n\n")
    print("-" * 100)
    return tfidf_matrix, vectorizer

'''
    This is an organization method that groups 5 pages together to print later on. 
'''
def page_results(results, page_number, items_per_page=5):
    start_index = (page_number - 1) * items_per_page
    end_index = start_index + items_per_page
    #print(results[start_index:end_index])
    return results[start_index:end_index]

'''
    Main method used to drive the search engine and interact with client. 
'''
def main():
    db = connectionDataBase()
    #grab data from the database:
    data = db['CollegeOfEngineering']
    documents = list(data.find())
    texts = [doc['tokens'] for doc in documents]
    tfidf_matrix, vectorizer = preprocess_text_data(texts)

    quitwords = ["quit", 'Quit', "q"]
    run = 1
    while run == 1:
        print("Enter 'quit' to exit")
        query = input("Enter your query: ")
        if query not in quitwords:
            results = search_engine(query, tfidf_matrix, documents, vectorizer)
            paged_results = page_results(results, 1)
            count = 1
            for res in paged_results:
                print(str(count) + " " + str(res['name']))
                words = res['tokens'].split()[:50]  # Take first 50 words
                output = "   " + " ".join(words) + "..."
                print(output)
                print()
                count += 1
            print("-"* 100)
        else:
            run = 0
            print()
            print("Exit Requested. Have a nice day.")
            print("-" * 10)

main()


