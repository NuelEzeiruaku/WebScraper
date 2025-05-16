from bs4 import BeautifulSoup
import requests
import re
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv
import os
import schedule
import time
import logging

# set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()]
)

load_dotenv()

# configure search terms - replace manual input with predefined list
SEARCH_TERMS = ["graphics card", "monitor", "SSD"]  # add your desired search terms

def send_email(subject, body):
    email = "kamsonuel@yahoo.com"
    password = os.getenv("EMAIL_PASSWORD")
    to = "kamsonuel@yahoo.com"

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = to

    try:
        with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as smtp:
            smtp.login(email, password)
            smtp.send_message(msg)
            logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")

def scrape_products(search_term):
    logging.info(f"Scraping products for: {search_term}")
    
    items_found = {}
    url = f"https://www.newegg.ca/p/pl?d={search_term}&N=4131"
    
    try:
        page = requests.get(url, timeout=30).text
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

        # limit pages to scan to avoid timeouts
        pages = min(pages, 3)
        
        for page_number in range(1, pages + 1):
            page_url = f"https://www.newegg.ca/p/pl?d={search_term}&N=4131&page={page_number}"
            page = requests.get(page_url, timeout=30).text
            doc = BeautifulSoup(page, "html.parser")

            div = doc.find_all(class_="item-container")
            if div:
                for product in div:
                    try:
                        name = product.find("a", class_="item-title").text.strip()
                        link = product.find("a", class_="item-title")["href"]
                        price_elem = product.find("li", class_="price-current").find("strong")
                        if price_elem:
                            price = price_elem.text.strip().replace(",", "")
                            items_found[name] = {"price": int(price), "link": link}
                    except (AttributeError, ValueError) as e:
                        logging.debug(f"Error parsing product: {str(e)}")
                        continue
            
            # brief pause between page requests to be respectful
            time.sleep(2)
            
        return items_found
    except Exception as e:
        logging.error(f"Error scraping {search_term}: {str(e)}")
        return {}

def run_scraper():
    for search_term in SEARCH_TERMS:
        items_found = scrape_products(search_term)
        
        # sort items
        sorted_items = sorted(items_found.items(), key=lambda x: x[1]['price'])
        
        # sending email if items were found
        if sorted_items:
            subject = f"Price Update: {search_term} - {time.strftime('%Y-%m-%d')}"
            body = f"Here are the top 5 best deals for {search_term}:\n\n"
            
            for item in sorted_items[:5]:  # only include top 5 cheapest items
                body += f"Item: {item[0]}\n"
                body += f"Price: ${item[1]['price']}\n"
                body += f"Link: {item[1]['link']}\n\n"
                
            send_email(subject, body)
            logging.info(f"Email sent for {search_term} with {len(sorted_items[:5])} items")
        else:
            logging.warning(f"No items found for {search_term}")
        
        # pause between different search terms
        time.sleep(5)

# schedule the job - examples
def setup_schedule():
    # run once a day at 9 am
    schedule.every().day.at("09:00").do(run_scraper)
    
    # alternatively, run every 12 hours
    # schedule.every(12).hours.do(run_scraper)
    
    logging.info("Scheduler set up successfully")
    
    # run immediately once at startup
    run_scraper()
    
    # keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # check for pending tasks every minute

if __name__ == "__main__":
    setup_schedule()