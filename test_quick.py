from tools import search_listings, create_fit_card
results = search_listings("vintage graphic tee", size=None, max_price=50)
print(create_fit_card("", results[0]))
