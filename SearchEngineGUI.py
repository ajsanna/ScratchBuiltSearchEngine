import tkinter as tk
from tkinter import ttk, scrolledtext
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import ssl
from pymongo import MongoClient
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

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

# Objects for lemmatizing
stemmer = PorterStemmer()
custom_stopwords = stopwords.words('english')

# CPP Colors
CPP_GREEN = "#1B4D3E"  # Dark green
CPP_GOLD = "#FFB81C"   # Gold
CPP_LIGHT_GREEN = "#E8F5E9"  # Light green for background
CPP_DARK_GREEN = "#0A2E1F"   # Darker green for text

def tokenize_and_stem(text):
    words = text.lower().split()
    stemmed_tokens = [stemmer.stem(word) for word in words if word not in custom_stopwords]
    return stemmed_tokens

def connectionDataBase():
    client = MongoClient("mongodb://localhost:27017")
    db = client["Final_Project"]
    return db

def search_engine(query, tfidf_matrix, documents, vectorizer):
    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    sorted_results = similarities.argsort()[::-1]
    sorted_documents = [documents[i] for i in sorted_results]
    return sorted_documents

def preprocess_text_data(texts):
    vectorizer = TfidfVectorizer(tokenizer=tokenize_and_stem)
    tfidf_matrix = vectorizer.fit_transform(texts)
    return tfidf_matrix, vectorizer

class SearchEngineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPP Faculty Search Engine")
        self.root.geometry("1000x700")
        self.root.configure(bg=CPP_LIGHT_GREEN)
        
        # Initialize database and search engine
        self.db = connectionDataBase()
        self.data = self.db['CollegeOfEngineering']
        self.documents = list(self.data.find())
        self.texts = [doc['tokens'] for doc in self.documents]
        self.tfidf_matrix, self.vectorizer = preprocess_text_data(self.texts)
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Title frame
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text="CPP Faculty Search Engine",
            font=("Helvetica", 24, "bold"),
            bg=CPP_LIGHT_GREEN,
            fg=CPP_GREEN
        )
        title_label.pack(pady=10)
        
        # Search frame
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill=tk.X)
        
        # Search entry with custom style
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=50,
            font=("Helvetica", 12),
            bg="white",
            fg=CPP_DARK_GREEN,
            insertbackground=CPP_GREEN
        )
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        # Search button with custom style
        search_button = tk.Button(
            search_frame,
            text="Search",
            command=self.perform_search,
            bg=CPP_GOLD,
            fg=CPP_GREEN,
            font=("Helvetica", 12, "bold"),
            relief="raised",
            padx=20,
            pady=5
        )
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.Frame(self.root, padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results text area with custom style
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            height=30,
            font=("Helvetica", 11),
            bg="white",
            fg=CPP_DARK_GREEN
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        # Add hover effect to search button
        search_button.bind('<Enter>', lambda e: search_button.configure(bg="#FFC72C"))
        search_button.bind('<Leave>', lambda e: search_button.configure(bg=CPP_GOLD))
        
    def perform_search(self):
        query = self.search_var.get()
        if query:
            self.results_text.delete(1.0, tk.END)
            results = search_engine(query, self.tfidf_matrix, self.documents, self.vectorizer)
            
            for i, res in enumerate(results[:5], 1):
                # Insert result number and URL with custom styling
                self.results_text.insert(tk.END, f"{i}. ", "number")
                self.results_text.insert(tk.END, f"{res['name']}\n", "url")
                
                # Insert preview text
                words = res['tokens'].split()[:50]
                preview = "   " + " ".join(words) + "...\n\n"
                self.results_text.insert(tk.END, preview)
                
                # Insert separator
                self.results_text.insert(tk.END, "─" * 80 + "\n\n")
                
            # Configure tags for styling
            self.results_text.tag_configure("number", foreground=CPP_GREEN, font=("Helvetica", 11, "bold"))
            self.results_text.tag_configure("url", foreground=CPP_GOLD, font=("Helvetica", 11, "bold"))
        else:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Please enter a search query.", "error")
            self.results_text.tag_configure("error", foreground="red", font=("Helvetica", 11, "bold"))

def main():
    root = tk.Tk()
    app = SearchEngineGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 