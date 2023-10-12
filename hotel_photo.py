import requests
import sqlite3
# import pandas as pd
# import mysql.connector
import googlemaps
# import request
import time


api_key = 'AIzaSyDzpYVlDrGTPA1UVRVUkr5e8_V82IvnsYY'
def find_name_without_hotel():
      
        gmaps=googlemaps.Client(key=api_key)
        geocode_result = gmaps.geocode('台南火車站')
        loc = geocode_result[0]['geometry']['location']
        rad = 1000
        hotel = gmaps.places_nearby(keyword="飯店",location=loc, radius=rad)['results']
        for result in hotel:
            name = result['name']
            place_id = result['place_id']
            get_photo_src(place_id, name)
        next_page_token = result.get('next_page_token')
        if next_page_token:
            get_more_results(next_page_token)

            

def find_hotels(keyword):
    location = 'Taiwan'  
    url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={keyword}+in+{location}&key={api_key}'
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        results = data['results']
        for result in results:
            place_id = result['place_id']
            name = result['name']
            get_photo_src(place_id,name)
            
        next_page_token = data.get('next_page_token')
        if next_page_token:
            get_more_results(next_page_token)
            
def get_more_results(next_page_token):
    url =  f'https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={next_page_token}&key={api_key}'
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        results = data['results']
        for result in results:
            place_id = result['place_id']
            name = result['name']
            get_photo_src(place_id,name)
        next_page_token = data.get('next_page_token')
        if next_page_token:
            get_more_results(next_page_token)
            
def get_photo_src(place_id,name):
    url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=photos&key={api_key}'
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        photos = data['result'].get('photos', [])
        if photos:
            photo_info = photos[0]
            photo_reference = photo_info['photo_reference']
            photo_src = construct_photo_src(photo_reference)
            save_photo_src(place_id,name, photo_src)
            

def construct_photo_src(photo_reference):
    return f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={api_key}'


def save_photo_src(place_id,name,photo_src):
    con = sqlite3.connect('photo_src.db')
    cursor = con.cursor()
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS photo2 (id INTEGER PRIMARY KEY AUTOINCREMENT,place_id TEXT,name TEXT, src TEXT)")
        time.sleep(0.1) 
        cursor.execute("INSERT INTO photo2 (place_id,name,src) VALUES(?,?,?)",(place_id,name,photo_src))
        con.commit()
        print("done")
    except Exception as e:
        print(e)
    finally:
        con.close()



if __name__ == "__main__":
    keyword = "光華觀光商務大飯店"

    find_hotels(keyword)
    # find_name_without_hotel()
