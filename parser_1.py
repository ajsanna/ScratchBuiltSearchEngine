# Group Project Final: Web Scrape and Recommendation System
# Names: 		Alexander Sanna, Ryan Larson, Parth Singh,
#				Priyanshu Shekhar, Christian Williams
# Due: 			May 15th, 2024
# Hours 		spent: ~10

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
import ssl
from pymongo import MongoClient

# Create SSL context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

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
This is the main scraping method. 

This is where we locate the desired URL. Process all data we want and store the 
data we collect as entries in our mongoDB database. The data is stored as key-value sets
where the key is the professor website URL's and the value is the String value
found on said website representing all text on the page.  
'''
def run(db, url):
    global name, tokens		# Global Variables used throughout 
    try:
        html = urlopen(url, context=ssl_context)		# open seed url
        soup = BeautifulSoup(html.read(), 'html.parser')	#define BeautifulSoup Object
        
        # This is where we collect all of the professor profiles on the original website
        # We look based upon class: what all the professor profiles have in common in HTML
        # define num_entries to keep track of how many successful entries we make into DB.
        # we also had to define a collected set so that we avoided repeat entries.
        professor_info = soup.find_all('div', class_='col-md directory-listing')
        num_entries = 0
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
                # If we have found a website: Store the URL as name, increment counter
                name = name_element.text.strip()
                num_entries += 1
                
                try:
                    # opens the personal website to parse in the next steps
                    # Uses beautiful soup to read and parse the HTML. 
                    # Specifying class = container allows us to access ONLY relevant text.
                    html = urlopen(name, context=ssl_context)
                    soup = BeautifulSoup(html.read(), 'html.parser')
                    container = soup.find("main", class_="container")
                    if container:
                        raw_text = container.get_text()
                        text = re.sub(r'[^\w\s]', '', raw_text)
                        tokens = text

                        # Create Document using python object syntax.
                        # Specified attributes are name: Website URL, tokens: all words found on website
                        professor_doc = {
                            "name": name,
                            "tokens": tokens
                        }
                        
                        # This line sends the document object to the createDocument Method. 
                        # This serves as entering the data we have into the database as a new entry. 
                        createDocument(db, professor_doc)
                except Exception as e:
                    print(f"Error processing professor {name}: {str(e)}")
                    continue
        
        print(str(num_entries) + " Successful Entries Into Database.")
    except Exception as e:
        print(f"Error accessing URL {url}: {str(e)}")
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

            html = urlopen(current_url, context=ssl_context)
            soup = BeautifulSoup(html.read(), 'html.parser')
            visited.append(current_url)

            # Look for faculty page
            if "faculty" in current_url.lower():
                print("Faculty page found:", current_url)
                return current_url

            # Add new URLs to frontier
            for link in soup.find_all('a', href=True):
                new_url = link['href']
                if new_url.startswith('/'):
                    new_url = url_start + new_url
                if new_url not in visited and new_url not in frontier:
                    frontier.append(new_url)
                    result_urls.append(new_url)

        except Exception as e:
            print(f"Error crawling {current_url}: {str(e)}")
            continue

    print("No faculty page found after", MAX_CRAWL_LIMIT, "attempts")
    return None

'''
Main function to get the ball rolling. 
Serves to initiate crawl, connect to DB, collect wanted data and enter into DB. 
'''
def main():
    # Main seed URL. DO NOT CHANGE
    # Crawler Starts here to begin searching for what we want.
    seed = "https://www.cpp.edu/engineering/ce/faculty.shtml"
    want = crawl(seed)

    # Connect to the database we specify in the connectionDataBase method above.
    # Define name of table to be used.
    db = connectionDataBase()
    name = "CollegeOfEngineering"
    collection = db[name]
    run(collection, want)


if __name__ == "__main__":
    main()
