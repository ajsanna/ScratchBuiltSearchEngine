# CPP Faculty Search Engine

A web-based search engine for Cal Poly Pomona faculty profiles, featuring a modern GUI interface with CPP's green and gold theme.

## Features

- Web scraping of CPP faculty profiles
- TF-IDF based search algorithm
- Cosine similarity for result ranking
- Modern GUI interface with CPP branding
- Real-time search results
- MongoDB integration for data storage

## Prerequisites

- Python 3.9 or higher
- MongoDB installed and running locally
- pip (Python package installer)

## Dependencies

The following Python packages are required:

```
beautifulsoup4>=4.12.0
pymongo>=4.6.0
scikit-learn>=1.4.0
nltk>=3.8.1
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ScratchBuiltSearchEngine
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure MongoDB is running locally on port 27017:
```bash
# On macOS with Homebrew
brew services start mongodb-community
```

## Usage

1. First, run the parser to collect faculty data:
```bash
python3 parser_1.py
```
This will scrape faculty profiles and store them in MongoDB.

2. Launch the search engine GUI:
```bash
python3 SearchEngineGUI.py
```

3. Use the search interface:
   - Type your search query in the search bar
   - Press Enter or click the Search button
   - View the top 5 matching results
   - Results are ranked by relevance

## How It Works

### Data Collection (parser_1.py)
- Scrapes faculty profiles from CPP's website
- Extracts text content from each profile
- Stores data in MongoDB for efficient retrieval

### Search Engine (SearchEngineGUI.py)
1. **Text Processing**:
   - Tokenizes and stems search queries
   - Removes stopwords
   - Converts text to lowercase

2. **Search Algorithm**:
   - Uses TF-IDF (Term Frequency-Inverse Document Frequency) to convert text to vectors
   - Applies cosine similarity to rank results
   - Returns most relevant matches

3. **User Interface**:
   - Modern GUI with CPP's green and gold theme
   - Real-time search results
   - Scrollable results view
   - Responsive design

## Troubleshooting

1. **MongoDB Connection Issues**:
   - Ensure MongoDB is running locally
   - Check if port 27017 is available
   - Verify MongoDB service status

2. **Import Errors**:
   - Make sure all dependencies are installed
   - Verify virtual environment is activated
   - Check Python version compatibility

3. **SSL Certificate Issues**:
   - The program includes SSL context handling
   - If issues persist, check your system's SSL certificates

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or feedback, please contact:
- Email: ajsanna@yahoo.com 