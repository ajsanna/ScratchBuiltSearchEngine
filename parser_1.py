# Group Project Final: Web Scrape and Recommendation System
# Names: 		Alexander Sanna, Ryan Larson, Parth Singh,
#				Priyanshu Shekhar, Christian Williams
# Due: 			May 15th, 2024
# Hours 		spent: ~6

'''
Overall Description: 
	This is a scratch built web scraper designed to support basic functionality of a 
	Recommender System. All methods indicate respective functionality through comments.
'''


# Imports
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from pymongo import MongoClient

'''
ConnectionDataBase serves to connect our program with a local database to store data
collected through web scraping. To run this on your own platform you must dedicate 
a local mongoDB database with host number 27017. 
'''
def connectionDataBase():
    client = MongoClient("mongodb://localhost:27017")
    db = client["Final_Project"]
    return db


'''
CreateDocument serves to create and store all documents we intend to keep in the database. 
This will insert the data into the table on mongoDB. 
'''
def createDocument(col,doc):
    insert_result = col.insert_one(doc)
    return

'''
We could not get the SK-Learn tokenizer to work the way we intended it to, so 
we designed our own. This tokenizer works by taking in the text from any given website,
splitting into dedicated words, and removing all stopwords using the SK learn pre-defined
stopword library. 
'''
def custom_tokenizer(text):
    #ENGLISH_STOP_WORDS = sklearn
    tokens = text.split()  # Split text into tokens
    tokens = [token.lower() for token in tokens if token.lower() not in ENGLISH_STOP_WORDS]  # Remove stopwords
    return tokens


'''
This is the main scraping method. 

This is where we locate the desired URL. Process all data we want and store the 
data we collect as entries in our mongoDB database. The data is stored as key-value sets
where the key is the professor website URL's and the values are the tokenized String values
found on said website. We also store a TF-IDF matrix here to keep track of how unique 
specific terms are for recommender system implementation later on. 

'''
def run(db, url):
    global name, tokens		# Global Variables used throughout 
    html = urlopen(url)		# open seed url
    soup = BeautifulSoup(html.read(), 'html.parser')	#define BeautifulSoup Object
    
	# This is where we collect all of the professor profiles on the original website
	# We look based upon class: what all the professor profiles have in common in HTML
	# define num_entries to keep track of how many successful entries we make into DB.
	# we also had to define a collected set so that we avoided repeat entries.
    professor_info = soup.find_all('div', class_='col-md directory-listing')
    num_entries = 1
    names_collected = []
    
    #cycle through all professors found on main page
    for professor in professor_info:
        # finds personal website link for each professor.
        # Using class and regex function we narrowed down where to find every link. 
        name_element = professor.find('span',class_= 'sr-only', string = re.compile("https"))
        if name_element in names_collected:
            continue
        names_collected.append(name_element)
        
        if name_element:
            # If we have found a website: Store the URL as name
            name = name_element.text.strip()
            num_entries += 1
            
            # opens the personal website to parse in the next steps
            # Uses beautiful soup to read and parse the HTML. 
            # Specifying class= container allows us to access ONLY relevant text. 
            html = urlopen(name)
            soup = BeautifulSoup(html.read(), 'html.parser')
            text = soup.find("main", class_="container").get_text()
            #tokenized_text = custom_tokenizer(text)
            
			# TFIDF Calculations and tokenization for data storage in next steps: 
            tfidf_vectorizer = TfidfVectorizer(stop_words = 'english')
            tfidf_matrix = tfidf_vectorizer.fit_transform(custom_tokenizer(text))
            tokens = tfidf_vectorizer.get_feature_names_out()

			# Debugging functions used in design: 
            #print(name)
            #print(tokens)
            #print(tfidf_matrix)
            #print()

		# Create Document using python object syntax.
		# Specified attributes are name: Website URL, tokens: all words found on website
        professor_doc = {
            "name": name,
            "tokens": tokens.tolist()
            # "office": office,
            # "phone": phone,
            # "email": email,
            # "website": website
        }
        
		# This line sends the document object to the createDocument Method. 
		# This serves as entering the data we have into the database as a new entry. 
        createDocument(db, professor_doc)
        
    print(str(num_entries) + " Successful Entries Into Database.")
    return

'''
Basic web crawling function serving to explore the web until our desired URL is found.
In this case we are searching for the Faculty and Staff page, so once we locate and 
navigate to this page we stop the crawl and begin collecting data in our Run Method. 
'''
def crawl(seed_url):

    frontier = [seed_url]
    visited = []
    result_urls = []
    MAX_CRAWL_LIMIT = 50

    while frontier and len(visited) < MAX_CRAWL_LIMIT:
        current_url = frontier.pop(0)
        try:
            url_start = "https://www.cpp.edu"

            html = urlopen(current_url)
            soup = BeautifulSoup(html.read(), 'html.parser')
            visited.append(current_url)

            if soup.find('title', string=re.compile("Faculty and Staff")):
                print("results found:", current_url)
                frontier.clear()
                return current_url
            frontier_elements = soup.select("a[href]")
            for frontier_element in frontier_elements:
                new_url = frontier_element['href']
                if "/engineering/ce/faculty.shtml" in new_url:
                    new_url = url_start + new_url
                    if new_url not in visited and new_url not in frontier:
                        frontier.append(new_url)
                        result_urls.append(new_url)
        except AttributeError as e:
            pass
        except HTTPError as e:
            pass
        except URLError as e:
            pass
    return

'''
Main function to get the ball rolling. 
Serves to initiate crawl, connect to DB, collect wanted data and enter into DB. 
'''
def main():
    # Main seed URL. DO NOT CHANGE
    # Crawler Starts here to begin searching for what we want.
    seed = "https://www.cpp.edu/engineering/ce/index.shtml "
    want = crawl(seed)
    
	# Connect to the database we specify in the connectionDataBase method above.
	# Define name of table to be used.
    db = connectionDataBase()
    name = "CollegeOfEngineering"
    collection = db[name]
    run(collection, want)


if __name__ == "__main__":
    main()
