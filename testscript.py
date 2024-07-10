import scrapingandco

query = "bags under 10000"
print(f"Testing with query: {query}")

results = scrapingandco.get_product_info(query)
print(f"Results: {results}")
