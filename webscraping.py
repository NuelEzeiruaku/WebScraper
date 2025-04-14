from bs4 import BeautifulSoup
import requests
import re
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv
import os
load_dotenv()


# sending message
def send_email(subject, body):
    email = "kamsonuel@yahoo.com"
    password = os.getenv("EMAIL_PASSWORD")
    to = "kamsonuel@yahoo.com"

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = to

    with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as smtp:
        smtp.login(email, password)
        smtp.send_message(msg)

# web scraper
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
        pages = 1
else:
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
                name = product.find("a", class_="item-title").text.strip() # name 
                link = product.find("a", class_="item-title")["href"] # the link
                price = product.find("li", class_="price-current").find("strong").text.strip().replace(",", "") # the link
                items_found[name] = {"price": int(price), "link": link} # the link
            except AttributeError:
                pass

# sort and "display"
sorted_items = sorted(items_found.items(), key=lambda x: x[1]['price'])

for item in sorted_items:
    print(item[0])
    print(f"${item[1]['price']}")
    print(item[1]['link'])
    print("---------------------------------")

# sending email
if sorted_items:
    subject = f"Yo, Newegg Alert. A new update regarding your items: {search_term}"
    body = "Here are the top 5 cheapest items for your search:\n\n"
for item in sorted_items[:5]:  # only include top 5 cheapest items
    body += f"Item: {item[0]}\n"
    body += f"Price: ${item[1]['price']}\n"
    body += f"Link: {item[1]['link']}\n\n"

send_email(subject, body)

