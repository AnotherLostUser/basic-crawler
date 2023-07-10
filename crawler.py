import requests, time, string, json, nltk
from bs4 import BeautifulSoup
from collections import Counter


base = 'https://quotes.toscrape.com/' # Base url
todo = [base] # Starting URL to crawl
crawled = []
dict = {}


def build(): # Starts Index Building Process
    global todo, crawled
    last = 0
    nltk.download('punkt') # Required package for tokenizer

    while todo: 
        if time.time() - last > 5: # Check 5 seconds past since last loop call
            
            last = time.time() # Update time of last url crawl (last iteration of loop)

            url = todo.pop(0) # Get and remove next url from todo list

            crawl(url)  # Crawl url

        else:   # Try again in 1 second
            time.sleep(1)

    outTerms = open("index.json", "w")
    json.dump(dict, outTerms)   # Save Index to JSON file
    outTerms.close()


def crawl(url): # Crawls passed url
    global todo, crawled

    response = requests.get(url)  # Get page

    if response.status_code == 200: # If httml page retrieved

        if response.url not in crawled: # If webpage url after any redirects not in crawled list
            
            crawled.append(response.url)    # Add to crawled list
            print(len(crawled), "Indexing:", url)   

            html = BeautifulSoup(response.text.replace("<", " <"), "html.parser")   # Add spacing after elements to allow for better text seperation
            
            getUrls(html) # Adds any valid urls on retrieved page that require crawling to todo list
            
            index(html.get_text(separator=' '),  response.url) # Add text on page to Inverted Index
        else:
            print("discarded:", url)
    else:
        print("Error retrieving:", url)


def pursue(url): # Simple rules to check if url should be crawled that greatly reduce amount of redirect urls being crawled

    if '#' in url: # Skip as no new content
        return False

    """ 
    ####  SITE SPECIFIC FILTERING ###

    if 'user' in url: # Skip as user login, search etc pages not required for indexing
        return False

    if 'edit' in url: # Skip as edit pages redirect to countries
        return False

    if 'iso' in url: # Skip as redirect to corresponding countries
        return False """
    
    return True


def index(text, doc):
    global dict

    text = text.replace(",", " ") # Remove specific punctuations with space replacement
    text = text.replace(":", " ")
    text = text.replace("-", " ")

    text = ''.join([i for i in text if not i.isdigit()]) # Remove digits from text

    text = text.translate(str.maketrans('', '', string.punctuation)) # Remove all remaining punctuation

    words = nltk.word_tokenize(text) # Tokenize text into list of words

    #words = [x for x in tidierText if x not in string.punctuation]

    tidyWords = list(dict.fromkeys(words)) # List of words without duplicates

    for word in tidyWords: # For each word in list
        if word in dict:
            dict[word].append([words.count(word), doc])  # If word in dicionary already, add new occurence with word frequency
        else:
            dict[word] = [[words.count(word), doc]] # If word not already in dicionary, add new word with occurence including frequency

    return


def getUrls(html): # Checks page for urls worth crawling and adds any to todo list
    global base, todo, crawled

    for link in html.find_all('a'): # Search all atributes

        if pursue(str(link.get('href'))): # Check if atribute link is worth pursuing (i.e. not obvious redirect)
            
            url = base+link.get('href') # Compose full url

            if url not in crawled and url not in todo: # If url has not already been crawled or exists in todo list, append to todo list
                todo.append(url)
    
    return

build()