import requests
from bs4 import BeautifulSoup


url = "https://books.toscrape.com/"
response = requests.get(url)
response.encoding = response.apparent_encoding #fixes encoding issue where strange symbols appear because of a mismatch
soup = BeautifulSoup(response.text, "html.parser")
print(soup.prettify())