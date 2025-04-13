from bs4 import BeautifulSoup
import requests
import re

search_term = input("What product would you like to search for? : ")

url = f"https://www.newegg.ca/p/pl?d={search_term}&N=4131"
page = requests.get(url).text
doc = BeautifulSoup(page, "html.parser")

page_text = doc.find(class_="list-tool-pagination-text")
if page_text:
    pages = page_text.get_text(strip=True).split("/")[-2]
    try:
        pages = int(pages)
    except ValueError:
        #print("Failed to extract number of pages, defaulting to 1 page.")
        pages = 1  
else:
    #print("No pagination element found. Defaulting to 1 page.")
    pages = 1  
 

items_found = {}

for page_number in range(1, pages + 1):
    url = f"https://www.newegg.ca/p/pl?d={search_term}&N=4131&page={page_number}"
    page = requests.get(url).text
    doc = BeautifulSoup(page, "html.parser")

    div = doc.find_all(class_="item-container")
    if div:
        for product in div:
            try:
                name = product.find("a", class_="item-title").text.strip()  
                link = product.find("a", class_="item-title")["href"]  
                price = product.find("li", class_="price-current").find("strong").text.strip().replace(",", "")  
                
                items_found[name] = {"price": int(price), "link": link}
            except AttributeError:
                pass  

sorted_items = sorted(items_found.items(), key=lambda x: x[1]['price'])

for item in sorted_items:
    print(item[0])  
    print(f"${item[1]['price']}")  
    print(item[1]['link'])  
    print("---------------------------------")
