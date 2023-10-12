# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 16:28:09 2023

@author: liupe
"""
import googlemaps
import time
from flask import Flask,render_template,request,redirect,url_for
# from bs4 import BeautifulSoup
import sqlite3
import requests


app = Flask(__name__)



# route放這裡
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        where = request.form.get('where')
        star = request.form.get('star')
        rad = request.form.get('rad')
        action = request.form.get('action')
        if action == '找飯店':
            return redirect(f'/hotel?where={where}&star={star}&rad={rad}')
        elif action == '找餐廳':
            return redirect(f'/restaurant?where={where}&star={star}&rad={rad}')
    return render_template('index.html')




@app.route('/hotel',methods=['GET', 'POST'])
def hotel():
    # where = request.args.get('where')
    # star = request.args.get('star')
    # rad = request.args.get('rad')
    # print(f"地點 (where): {where}")
    # print(f"where: {where}")
    # print(f"rad: {rad}")
    # print(f"star: {star}")
    sorted_hotel = []
    image_url = []
    if request.method == 'GET':
        
        where = request.args.get('where')
        star = request.args.get('star')
        rad = request.args.get('rad')
        print(f"地點 (where): {where}")
        print(f"where: {where}")
        print(f"rad: {rad}")
        print(f"star: {star}")
        # print(f"hotels_and_images: {hotels_and_images}")
        gmaps=googlemaps.Client(key="AIzaSyDzpYVlDrGTPA1UVRVUkr5e8_V82IvnsYY")
        geocode_result = gmaps.geocode(where)
        # 找到where的google maps資料
        # loc= where的經緯度
        loc = geocode_result[0]['geometry']['location']
        # 利用where搜尋關鍵字 經緯度 跟距離 :rad公尺為單位
        hotel = gmaps.places_nearby(keyword="飯店",location=loc, radius=rad)['results']
        hotel_place_id = []
        #只取出result裡面place_id的部分加到list裏頭
        for i in hotel:
            hotel_place_id.append(i['place_id'])
            
        hotel_info = []
        for id in hotel_place_id:
            hotel_info.append(gmaps.place(place_id = id,language = 'zh-tw'))
            # 其中讓每次request中間隔0.3秒，原因是太快容易造成取聯繫API timeout。
            time.sleep(0.3)    
            # 以下是抓到result內我想要的資料
        hotel = []
        for i in hotel_info:
            hotel_info_dict = {}
            if 'rating' in i['result'] and i['result']['rating'] >= eval(star):
                hotel_info_dict['place_id'] = i['result']['place_id']
                hotel_info_dict['name'] = i['result']['name']
                hotel_info_dict['rating'] = i['result']['rating']
                address = i['result']['formatted_address']
                hotel_info_dict['address'] = address[3:]
    
                # 如果該店家無提供的例外處理
                try:
                    phone = i['result']['formatted_phone_number']
                    hotel_info_dict['phone'] = phone.replace(" ", "-")
                except KeyError:
                    hotel_info_dict['phone'] = "該店家無此資料"
                except Exception as e:
                    hotel_info_dict['phone'] = "該店家無此資料"
                    print(f"An error occurred: {str(e)}")
                hotel.append(hotel_info_dict)
        # sorted_hotel = sorted(hotel, key=lambda x: x.get('rating',0), reverse=True)
        if hotel:
            sorted_hotel = sorted(hotel, key=lambda x: x.get('rating', 0), reverse=True)
        else:
            sorted_hotel = []
                # sorted 用星等做排序
        
            
        
                
            # print(hotel_name)
            
            # 用place_id對應資料庫內的圖片src 因為有些旅館的名字可能跟抓到的圖片名稱不相同
            # place_id是唯一值
        hotel_places_id= [hotel['place_id']for hotel in sorted_hotel]
        try:
            con = sqlite3.connect("photo_src.db")
            cursor = con.cursor()
            image_url = []
            
            for place_id in hotel_places_id:
                cursor.execute("SELECT src FROM photo2 WHERE place_id = ?",(place_id,))
                rows = cursor.fetchall()
                images_url = [row[0] for row in rows]
                
                if not images_url:
                    default_image_url = "https://www.bravonia.com.tw/images/no_img.png"
                    images_url.append(default_image_url)
                image_url.extend(images_url)
                
            
        except Exception as e:
            print(e)
        finally:
            if con:
                con.close()
    
    
        
        
    hotels_and_images = list(zip(sorted_hotel,image_url))


    
    
    
    return render_template('search_result.html',where=where,rad=rad,star=star,hotels_and_images=hotels_and_images)
# where=where,rad=rad,star=star,hotels_and_images=hotels_and_images)
# return render_template('home.html')



@app.route('/restaurant', methods=['GET','POST'])
def find_food_result():
    where = request.args.get('where')
    star = request.args.get('star')
    rad = request.args.get('rad')
    
    image_url = []
    sorted_food = []
    if request.method == 'GET':
        image_url = []
        where = request.args.get('where')
        star = request.args.get('star')
        rad = request.args.get('rad')
        gmaps=googlemaps.Client(key="AIzaSyDzpYVlDrGTPA1UVRVUkr5e8_V82IvnsYY")
        geocode_result = gmaps.geocode(where)
        # 用google api 搜尋where
        # loc是where的經緯度
        loc = geocode_result[0]['geometry']['location']
        # food是以where的經緯度搜尋關鍵字為餐廳 radius方圓rad公尺的範圍 result是搜尋的所有結果
        food = gmaps.places_nearby(keyword="餐廳",location=loc, radius=rad)['results']
        food_place_id = []
        # 用一個空陣列塞where要的place id 
        # print(restaurant)
        for i in food:
            food_place_id.append(i['place_id'])
        # 再用id 放到google maps api裡
        food_info = []
        for id in food_place_id:
            food_info.append(gmaps.place(place_id = id,language = 'zh-tw'))
        # 怕資料回傳需要時間所以sleep0.3秒
            time.sleep(0.3)    
            # 從food result 抓想要的資料
            food_result = []
            for i in food_info:
                food_info_dict = {}
                if 'rating' in i['result'] and i['result']['rating'] >= eval(star):
                    food_info_dict['place_id'] = i['result']['place_id']
                    food_info_dict['name'] = i['result']['name']
                    food_info_dict['rating'] = i['result']['rating']
                    address = i['result']['formatted_address']
                    food_info_dict['address'] = address[3:]
                    
    
                    # 如果該店家無提供以下資料的例外處理
                    try:
                        opening_hours = i['result']['current_opening_hours']
                        food_info_dict['opening_hours']=opening_hours
                    except KeyError:
                        food_info_dict['opening_hours'] = "該店家無此資料"
                    except Exception as e:
                        food_info_dict['opening_hours'] = "該店家無此資料"
                        print(f"An error occurred: {str(e)}")
    
                    try:
                        phone = i['result']['formatted_phone_number']
                        food_info_dict['phone'] = phone.replace(" ", "-")
                    except KeyError:
                        food_info_dict['phone'] = "該店家無此資料"
                    except Exception as e:
                        food_info_dict['phone'] = "該店家無此資料"
                        print(f"An error occurred: {str(e)}")
                    food_result.append(food_info_dict)
                    # 依照星等排名
                # sorted_food = sorted(food_result , key=lambda x: x.get('rating',0), reverse=True)
        if food_result:
            sorted_food = sorted(food_result, key=lambda x: x.get('rating', 0), reverse=True)
        else:
            sorted_food = []
            # food_name = []
            # for i in sorted_food:
            #     food_name.append(i.get('name'))
            
    
                
            # print(food_name)
            food_places_id= [food_result['place_id']for food_result in sorted_food]
            # 因為會依照星等排名 所以如果要抓照片 place_id也需要依照排名後的順序
            # 從db抓取圖片的src
            try:
                con = sqlite3.connect("photo_src.db")
                cursor = con.cursor()
                image_url = []
                
                for place_id in food_places_id:
                    cursor.execute("SELECT src FROM food_photo WHERE place_id = ?",(place_id,))
                    rows = cursor.fetchall()
                    images_url = [row[0] for row in rows]
                    # 如果沒有該店家的src 就使用default_image_url
                    if not images_url:
                        default_image_url = "https://www.bravonia.com.tw/images/no_img.png"
                        images_url.append(default_image_url)
                    image_url.extend(images_url)
                    
                
            except Exception as e:
                print(e)
            finally:
                if con:
                    con.close()
    restaurant_and_images = list(zip(sorted_food,image_url))

    return render_template('restaurant.html', where=where,rad=rad,star=star,restaurant_and_images=restaurant_and_images)




# find_food_photo,get_more_results,get_photo_src,construct_photo_src,save_photo_src是從google maps找餐廳的照片放到資料庫


# 啟動，不要改
if __name__ == "__main__":
    app.run(debug = True,use_reloader=False)
    # app.debug = True
    # debug = True