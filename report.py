from urllib.parse import urldefrag
import scraper
from bs4 import BeautifulSoup
from utils.response import Response
import re
from urllib.parse import urlparse

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
        token_list.append(word.lower())
    
    return token_list

# this class is intended to preserve information needed between analyses on different
# pages. 
class Report():
    def __init__(self):
        # Question 2: What is the longest page in terms of the number of words? 
        # (HTML markup doesn’t count as words)
        self.longest_page = ('', 0)

        # Question 3: What are the 50 most common words in the entire set of pages 
        # crawled under these domains? (Ignore English stop words)
        self.word_frequencies = {}
        self.stop_words = {}
        self.page_set = set()
        # read every stop word from file and add it to a dictionary for quick look-up
        with open('stopwords.txt') as f:
            for line in f:
                for word in line.split():
                # remove newlines from each word before adding to dictionary
                    self.stop_words[word] = 1

        #Question 4 how mainy subdomains did you find and the number of unique pages
        self.unique_subdomains = {}
        self.unique_subdomains_unique_pages = set()


    # accessor to retrieve the longest page's word count. this allows for easy
    # comparison between a current page's word count and the previous longest page
    def get_page_word_count(self) -> int:
        return self.longest_page[1]

    # accessor to retrieve the longest page in string format
    def get_page_url(self) -> str:
        return self.longest_page[0]

    # this function expects the response and url received by the scraper function. 
    # this function will use BeautifulSoup to get just the text content
    # from the current page, and return the count of the total number of 
    # words (not including HTML markup) in the current page
    def count_total_page_words(self, url, resp: Response) -> None:
        # only check the current page if it's valid and returned OK status
        if scraper.is_valid(url) and resp.status == 200:
            soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
            # get plain text from the current page
            text = soup.get_text()
            # split the text into a list
            words = tokenize(text)

            # only count words with 2 letters or more
            words = [word for word in words if len(word) > 1]

            # the length of the list is the total number of words in this page
            # if total is higher than the previous high, update the highest
            if len(words) > self.longest_page[1]:
                # self.update_page_word_count(url, len(words))
                self.longest_page = (url, len(words))

    #function to add the unqiue subdomain found
    def add_subdomain(self, url):
        
        #checks to make sure the url is valid first
        if(scraper.is_valid(url)):
            url =  url.replace('www.','')
            parsed = urlparse(url)
            url_removed_fragment = urldefrag(url).url
            #print(url)
            #checks to make sure the url was not already looked at and that it is a subdomain of .ics.uci.edu
            if parsed.netloc.lower() not in self.unique_subdomains.keys() and re.search('\.ics\.uci\.edu',parsed.netloc.lower()) and parsed.netloc.lower() != 'www.ics.uci.edu'\
             and not re.search('edu:', parsed.netloc.lower()):
                self.unique_subdomains.update({parsed.netloc.lower(): 1})
                self.unique_subdomains_unique_pages.add(url_removed_fragment.lower())
            #if the subdomain has already been looked at checks to see if the page is unique. 
            elif parsed.netloc.lower() in self.unique_subdomains.keys() and re.search('\.ics\.uci\.edu', parsed.netloc.lower()) and parsed.netloc.lower() != 'www.ics.uci.edu'\
             and not re.search('edu:', parsed.netloc.lower()):
                #checks to see if the page is unique to this domain and if it is updates the page count for that subdomain. 
                if not url_removed_fragment.lower() in self.unique_subdomains_unique_pages:
                    self.unique_subdomains_unique_pages.add(url_removed_fragment.lower())
                    num = self.unique_subdomains.get(parsed.netloc.lower())
                    self.unique_subdomains.update({parsed.netloc.lower(): num + 1})


    # this function expects the response received by the scraper function. 

    # this function expects both the url and the response received by scraper(url, resp).
    # this function should be called once for each URL, so that it can count the number
    # of words in valid pages. this function does not return anything, but instead it
    # stores values in a dictionary data member of this Report class. each page's word
    # frequencies are totaled in this dictionary, which will facilitate printing the 
    # results at the end of the program
    def count_each_page_word(self, url, resp: Response) -> None:
        # only check the current page if it's valid and returned OK status
        if scraper.is_valid(url) and resp.status == 200:
            soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
            # get plain text from the current page
            text = soup.get_text()
            # split the text into a list of lowercase words 
            words = tokenize(text)
            
            for word in words:
                # first ensure it's not a stopword
                if word not in self.stop_words.keys() and len(word) > 1:
                    # increment its counter if it's in the list
                    if word in self.word_frequencies.keys():
                        self.word_frequencies[word] += 1
                    # or add it if it isn't
                    else:
                        self.word_frequencies[word] = 1

    # print the report
    def __repr__(self):
        # the four different strings that will be concatenated to print the final report
        one = 'The number of unique pages is ' + str(len(self.page_set)) + '.\n'
        two = 'The longest page is ' + self.longest_page[0] + ' with ' + str(self.longest_page[1]) + ' words.\n'
        three = self.question_three_helper()
        four = ''
        five = ''
        subdomains_sorted = sorted(self.unique_subdomains.keys(), key=str.lower)
        for subdomain in subdomains_sorted:
            five = five + 'http://' + subdomain + ", " + str(self.unique_subdomains.get(subdomain)) + '\n'

        return (one + two + three + four + five + '\n')

    # this function helps to format the string for Q3 that will be returned by __repr__
    def question_three_helper(self) -> str:
        # sort the map of words of the entire set of pages by frequency
        self.word_frequencies = sorted(self.word_frequencies.items(), key=lambda x: x[1], reverse=True)
        
        three = 'The 50 most common words in the entire set of pages are:\n'

        # only include the 50 most frequent words
        for i, pair in enumerate(self.word_frequencies):
            if i >= 50:
                break
            three += pair[0] + ': ' + str(pair[1]) + ', '

        # get rid of the last comma and add a newline
        return three[0:-2] + '\n'

    # this function takes a list of valid links and split the link from the # point
    # and only takes the left side of the result
    # this is how a unique page is defined according to the requirement
    def count_unique_page(self, url, resp: Response):
        # only check the current page if it's valid and returned OK status
        if scraper.is_valid(url) and resp.status == 200:
            split_url = urldefrag(url)[0]
            # split_url = str_url.split('#',1)[0]       # split from the first #, only take the left part 
            self.page_set.add(split_url)                # add to page_set
            

