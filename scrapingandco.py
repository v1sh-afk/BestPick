import requests
from bs4 import BeautifulSoup
import time
import random
import emoji
import analyzer
import pickle
import threading

def search(searchterm):
    print("Searching up stuff")
    words = searchterm.split()
    query = "+".join(words)
    request = f"https://www.amazon.in/s?k={query}"
    print(f"Request URL: {request}")

    contents = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "accept-language": "en-IN,en;q=0.9",
    }
    
    response = requests.get(request, headers=contents)
    soup = BeautifulSoup(response.text, "lxml")
    asin_elements = soup.find_all("div", {"data-asin": True})
    print(f"ASIN Elements Found: {len(asin_elements)}")

    final_list = []
    for i in asin_elements:
        if i["data-asin"] != "":
            image = i.find("img")
            if image:
                asin = i["data-asin"]
                url = image["src"]
                final_list.append([asin, url])

    asin_list = final_list
    print(f"ASIN List: {asin_list}")

    return asin_list[:10]


def extract_from_asin(asin):
    image = asin[1]
    asin = asin[0]
    print(f"Extracting from ASIN: {asin}")

    contents = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "accept-language": "en-IN,en;q=0.9",
    }
    
    url = f"https://www.amazon.in/dp/{asin}"
    response = requests.get(url, headers=contents)
    soup = BeautifulSoup(response.text, "lxml")
    
    title_element = soup.select_one("#productTitle")
    print(f"Title Element: {title_element}")

    review_elements = soup.select("div.review")
    scrapedreviews = [review.select_one("span.review-text").text for review in review_elements if review.select_one("span.review-text")]
    
    final = ["".join(c for c in review if c not in emoji.EMOJI_DATA) for review in scrapedreviews]
    
    print(f"Scraped Reviews: {final}")

    return title_element.contents[0].strip() if title_element else "No Title", final


def process_query(query):
    print("Query processing")
    asins = search(query)
    #time.sleep(random.uniform(0.2, 1.0))
    master_reviews = {}
    for asin in asins:
        name, reviews = extract_from_asin(asin)
        master_reviews[(asin[0], name, asin[1])] = reviews
    return master_reviews

def thread_work(asin,master_reviews):
    print("Searching Asin")
    #time.sleep(random.uniform(0.2, 1.0))
    name, reviews = extract_from_asin(asin)
    master_reviews[(asin[0], name, asin[1])] = reviews
    

def process_query_thread(query):
    print("Query processing")
    asins = search(query)
    #time.sleep(random.uniform(0.2, 1.0))
    master_reviews = {}
    threads = []
    for asin in asins:
        threads.append(threading.Thread(target=thread_work,args=[asin,master_reviews]))
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    return master_reviews

def generate_score(reviews):
    pass

def get_product_info(query):
    print(query)
    #Without Threading
    #d = process_query(query)
    #With Threading, risk of amazon ban
    d = process_query_thread(query)
    answers = []
    for product in d:
        asin = product[0]
        title = product[1]
        image = product[2]
        reviews = d[product]
        print("Analyzing",product)
        #score = analyzer.save_training_model(reviews, r"dataset2.csv")
        score = analyzer.train_with_data(reviews, "dataset2.csv")
        url = f"https://www.amazon.in/dp/{asin}"
        answers.append([score, title, url, image])
    answers.sort(reverse = True)
    return answers

def thread_work2(product,answers,reviews):
    asin = product[0]
    title = product[1]
    image = product[2]
    #reviews = d[product]
    print("Analyzing",product)
    #score = analyzer.save_training_model(reviews, r"dataset2.csv")
    score = analyzer.train_with_data(reviews, "dataset2.csv")
    url = f"https://www.amazon.in/dp/{asin}"
    answers.append([score, title, url, image])

def get_product_info_threads(query):
    d = process_query(query)
    answers = []
    threads = []
    for product in d:
        threads.append(threading.Thread(target=thread_work2,args=[product,answers,d[product]]))
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    answers.sort(reverse = True)
    return answers

if "__name__" == "__main__":
    query = input("Query: ")
    d = process_query(query)
    answers = []
    for product in d:
        asin = product[0]
        title = product[1]
        image = product[2]
        reviews = d[product]
        print("Analyzing",product)
        #score = analyzer.save_training_model(reviews, r"dataset2.csv")
        score = analyzer.train_with_data(reviews, "dataset2.csv")
        answers.append([score, title, image])

    print(answers)
    answers.sort()

    print("Best:", answers[-1][:15])
    print()
    print("Second:", answers[-2][:15])
    print()
    print("Third:", answers[-3][:15])
