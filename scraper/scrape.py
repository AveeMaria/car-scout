from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json

def scrape(driver):
    try:
        with open("log.json", "r", encoding="utf-8") as f:
            log_items = json.load(f)
    except FileNotFoundError:
        log_items = []

    existing_links = set(item["link"] for item in log_items)
    last_id = log_items[-1]["id"] if log_items else 0

    url = "https://www.avto.net/Ads/results_100.asp"
    driver.get(url)
    cars = driver.find_elements(By.CLASS_NAME, "GO-Results-Row")

    scraped_items = []
    iteration = 0

    print("Starting scrape...")

    for car in cars:
        iteration += 1
        #print(iteration)

        title = car.find_element(By.CLASS_NAME, "GO-Results-Naziv").text
        soup = BeautifulSoup(car.get_attribute("outerHTML"), "html.parser")

        if car.find_elements(By.CLASS_NAME, "GO-Results-Price-Akcija-TXT"):
            price = soup.select_one(".GO-Results-Price-TXT-AkcijaCena").get_text(strip=True)

        elif car.find_elements(By.CLASS_NAME, "GO-Results-Top-BadgeTop"):
            if car.find_elements(By.CLASS_NAME, "GO-Results-Top-Price-TXT-Regular"):
                price = soup.select_one(".GO-Results-Top-Price-TXT-Regular").get_text(strip=True)

            elif car.find_elements(By.CLASS_NAME, "GO-Results-Top-Price-TXT-AkcijaCena"):
                price = soup.select_one(".GO-Results-Top-Price-TXT-AkcijaCena").get_text(strip=True)

        else:
            price = soup.select_one(".GO-Results-Price-TXT-Regular").get_text(strip=True)

        price = int(price.replace(".", "").replace(" €", ""))

        link = car.find_element(By.CLASS_NAME, "stretched-link").get_attribute("href")
        img_link = car.find_element(By.TAG_NAME, "img").get_attribute("src")

        broken = False #pokvarjen avto
        if car.find_elements(By.CLASS_NAME, "fa-exclamation-triangle"):
            #print("BROKEN CAR: " + link)
            broken = True

        oldtimer = False #ce oldtimerji
        if car.find_elements(By.CLASS_NAME, "fa-institution"):
            print("ALTTIMER")
            oldtimer = True

        data = []
        data_div = car.find_elements(By.CLASS_NAME, "GO-Results-Data-Top")
        if data_div:
            for td in data_div[0].find_elements(By.TAG_NAME, "td"):
                data.append(td.text)
        elif car.find_elements(By.CLASS_NAME, "GO-Results-Top-Data-Top"):
            for td in car.find_elements(By.CLASS_NAME, "GO-Results-Top-Data-Top")[0].find_elements(By.TAG_NAME, "td"):
                data.append(td.text)
        else:
            print(f"data ERROR at {title}")
            continue

        if link in existing_links:
            print("Already in log.json, skipping:", link)
            continue

        if broken:
            print("broken")
            continue

        key_renames = {
            "1.registracija": "1.reg",
            "Prevoženih": "mileage",
            "Gorivo": "fuel",
            "Menjalnik": "transmission",
            "Motor": "engine"
        }

        raw_data = dict(zip(data[::2], data[1::2]))

        data = {}
        for key, value in raw_data.items():
            new_key = key_renames.get(key, key)
            data[new_key] = value

        data["oldtimer"] = oldtimer

        scraped_items.append({
            "id": 0,
            "title": title,
            "price": price,
            "data": data,
            "link": link,
            "img_link": img_link
        })

    print("Items scraped.")
    return scraped_items
