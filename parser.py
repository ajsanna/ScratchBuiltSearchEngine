#Group Project Final
#Due 4/24/2024
#hours spent: ~4


#Imports
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
from MDB_Connection import *
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS



from pymongo import MongoClient
def connectionDataBase():
    client = MongoClient("mongodb://localhost:27017")
    db = client["Final_Project"]
    return db

def createDocument(col,doc):
    insert_result = col.insert_one(doc)
    return
def custom_tokenizer(text):
    #ENGLISH_STOP_WORDS = sklearn
    tokens = text.split()  # Split text into tokens
    tokens = [token.lower() for token in tokens if token.lower() not in ENGLISH_STOP_WORDS]  # Remove stopwords
    return tokens

def run(db, url):
    global name, tokens
    #open seed url :
    html = urlopen(url)
    #define beautiful soup
    soup = BeautifulSoup(html.read(), 'html.parser')
    #find all professor profiles on website
    professor_info = soup.find_all('div', class_='col-md directory-listing')

    #cycle through all professors found on main page
    for professor in professor_info:
        #finds personal website link for each professor.
        name_element = professor.find('span',class_= 'sr-only', text = re.compile("https"))

        if name_element:
            name = name_element.text.strip()
            # opens the personal website to parse in the next steps
            html = urlopen(name)

            soup = BeautifulSoup(html.read(), 'html.parser')
            text = soup.find("main", class_="container").get_text()
            #tokenized_text = custom_tokenizer(text)
            tfidf_vectorizer = TfidfVectorizer(stop_words = 'english')

            tfidf_matrix = tfidf_vectorizer.fit_transform(custom_tokenizer(text))
            tokens = tfidf_vectorizer.get_feature_names_out()

            print(name)
            print(tokens)
            #print(tfidf_matrix)
            print()


        professor_doc = {
            "name": name,
            "tokens": tokens.tolist()
            # "office": office,
            # "phone": phone,
            # "email": email,
            # "website": website
        }
        createDocument(db, professor_doc)

    return


def crawl(seed_url):

    frontier = [seed_url]
    visited = []
    result_urls = []

    while frontier and len(visited) < 50:
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


def main():
    seed = "https://www.cpp.edu/engineering/ce/index.shtml "
    want = crawl(seed)
    db = connectionDataBase()
    name = "CollegeOfEngineering"
    collection = db[name]
    run(collection, want)


if __name__ == "__main__":
    main()



