import scraper
from bs4 import BeautifulSoup
from utils.response import Response
from urllib.parse import urlparse
import re



# helper function to aid with finding the 50 most common words
def tokenize(text: str) -> list:
    token_list = []

    # use regex on apostrophes to unite contractions
    p = re.compile('[\']')
    text = p.sub('', text)

    # use regex on any non-alphabetic chars
    p = re.compile('[^a-zA-Z]')
    # USE THIS LINE TO INCLUDE NUMBERS 
    #p = re.compile('[^a-zA-Z0-9]')

    # replace them with a space
    text = p.sub(' ', text)

    # add each word to the token list
    for word in text.split():
        token_list.append(word)
    
    return token_list


# this class is intended to preserve information needed between analyses on different
# pages. 
class Report():
    def __init__(self):
        # Question 2: What is the longest page in terms of the number of words? 
        # (HTML markup doesn’t count as words)
        self.longest_page = ('', 0)

        #Question 4 how mainy subdomains did you find and the number of unique pages
        self.unique_subdomains = {}


    # accessor to retrieve the longest page's word count. this allows for easy
    # comparison between a current page's word count and the previous longest page
    def get_page_word_count(self) -> int:
        return self.longest_page[1]

    # accessor to retrieve the longest page in string format
    def get_page_url(self) -> str:
        return self.longest_page[0]



    #function to add the unqiue subdomain found
    def add_subdomain(self, url):
        
        #checks to make sure the url is valid first
        if(scraper.is_valid(url)):
            parsed = urlparse(url)
            #print(url)
            #checks to make sure the url was not already looked at and that it is a subdomain of .ics.uci.edu
            if parsed.netloc not in self.unique_subdomains.keys() and re.search('\.ics\.uci\.edu', url):
                print(parsed.netloc)
                self.unique_subdomains.update({parsed.netloc: 0})
        
 

    # this function expects the response received by the scraper function. 
    # this function will use BeautifulSoup to get just the text content
    # from the current page, and return the count of the total number of 
    # words (not including HTML markup) in the current page
    def count_total_page_words(self, url, resp: Response):
        # only check the current page if it's valid and returned OK status
        if scraper.is_valid(url) and resp.status == 200:
            soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
            # get plain text from the current page
            text = soup.get_text()
            # split the text into a list
            words = text.split()

            # the length of the list is the total number of words in this page
            # if total is higher than the previous high, update the highest
            if len(words) > self.longest_page[1]:
                # self.update_page_word_count(url, len(words))
                self.longest_page = (url, len(words))

    # print the report
    def __repr__(self) -> str:
        one = ''
        two = 'The longest page is ' + self.longest_page[0] + ' with ' + str(self.longest_page[1]) + ' words.\n'
        three = ''
        four = ''
        # #print(self.unique_subdomains.keys())
        # for page in self.unique_subdomains.keys():
        #     print(page)
    
        return (one + two + three + four)