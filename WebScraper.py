import requests
from bs4 import BeautifulSoup
import time 
import random
from database import insertBook, insertPrice


counter = 0

url = "https://books.toscrape.com/"
url2 = "https://books.toscrape.com/"
catalogueURL = "https://books.toscrape.com/catalogue/"
books = [] 
while url:
    time.sleep(0.1)
    response = requests.get(url)
    response.encoding = response.apparent_encoding #fixes encoding issue where strange symbols appear because of a mismatch
    soup = BeautifulSoup(response.text, "html.parser")
    counter += 1
    
    
    allBooks = soup.find_all("article", class_ = "product_pod")
    #above line gets chunk of html related to each book and stores all of it in a list

    for book in allBooks:
        title = book.find("h3").find("a") 
        bookTitle = title.get("title")
        #find first text element with the title tag to extract book name
        #have to use .find in a nested fashion to obtain the title since it isn't an actual html tag

        bookPrice = book.find("p", class_ = "price_color").text #find first p element with the price class to extract book price and have to use .text to extract just the actual text 
        bookPrice = float(bookPrice[1:]) #get rid of currency symbol so it's just numbers
        simulatedPrice = round(float(bookPrice) + random.uniform(-2.0, 2.0), 2)

        genreURL = book.find("a", href=True)
        genreURL = genreURL.get("href") #.get to obtain the actual href link instead of the tag contents(.text)
        if not genreURL.startswith("catalogue/"):
            completeURL = catalogueURL + genreURL 
        else:
            completeURL = url2 + genreURL #must connect the two urls for genre since genre isn't available in productpod

        response2 = requests.get(completeURL)
        response2.encoding = response2.apparent_encoding
        soup2 = BeautifulSoup(response2.text, "html.parser")
        listElements = soup2.find("ul", class_ = "breadcrumb") #gets the ul list elements and this is where the genre is stored
        listElements = listElements.find_all("li") #get elements into a list to extract the genre word
        if(len(listElements) < 3):
            continue #preventative measure in case the structure doesn't have a third element to access
        genre = listElements[2].text.strip() #genre is always the third element

        productPage = soup2.find("article", class_ = "product_page")
        bookDescription = productPage.find(id="product_description", class_="sub-header")
        if(bookDescription is not None):
            bookDescription = bookDescription.find_next("p").text.strip() #extract the description of the book
        else:
            bookDescription = "" #set to empty instead of None
        #parentAvailability = soup2.find("div", class_="row")
        availability = soup2.find_next("p", class_="availability")
        if(availability):
            availability = availability.text.strip()
        else:
            availability = "availability is unkown"
        

        #other properties of book to get still:
        #url

        bookDict = {
            "title": bookTitle,
            "price in pounds": bookPrice,
            "genre": genre,
            "book description": bookDescription,
            "availability": availability,
            "book URL": completeURL
        }
        books.append(bookDict) #dictionary to store key-value pairs based on book properties
        bookID = insertBook(bookTitle, genre, bookDescription, completeURL)
        insertPrice(bookID, simulatedPrice, availability)
        print(f"{bookTitle} is here and so is {genre}")

    nextPage = soup.find("li", class_="next")
    if(nextPage):
        nextPage = nextPage.find("a").get("href") #get link for next page
        if(nextPage.startswith("catalogue/")):
            url = url2 + nextPage
        else:
            url = catalogueURL + nextPage
    else:
        url = None #no more pages left
