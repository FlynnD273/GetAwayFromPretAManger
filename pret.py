import json
import pickle
import requests
from bs4 import BeautifulSoup

# Store the coordinates of each location
pret_coordinates = []

# I downloaded the search for london Pret A Mangers after scrolling to the bottom to load all results
with open("file.html", "r") as file:
    # Parse the HTML content of the page
    soup = BeautifulSoup(file.read(), "html.parser")

    # Extract the information about Pret a Manger locations
    locations = soup.find_all("div", class_="ubsf_locations-list-item-main-content")

    # Convert addresses to lat/long coordinates
    for location in locations:
        address = location.find("div", class_="ubsf_locations-list-item-street").get_text(strip=True)
        address += ", "
        address += location.find("div", class_="ubsf_locations-list-item-zip-city").get_text(strip=True)
        print(address)
        response = requests.get(f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1")
        jsoncontent = json.loads(response.text)
        if len(jsoncontent) > 0:
            coords = jsoncontent[0]
            pret_coordinates.append((coords["lat"], coords["lon"]))
        else:
            print(f"Skipping {address}")

# Print the coordinates
if pret_coordinates:
    with open("pret.pickle", "wb") as file:
        pickle.dump(pret_coordinates, file)
    for i, coord in enumerate(pret_coordinates, start=1):
        print(f"Location {i}: Latitude {coord[0]}, Longitude {coord[1]}")
else:
    print("no locations")
