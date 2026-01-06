import csv
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import io
import math

card_image_dir = '/c/Pictures/'
deck = "/c/Downloads/flubs.csv"
q_base = 'https://api.scryfall.com/cards/search?'

standard_back = Image.open("mtg_back.jpeg").convert("RGBA")
print(f'Standard back mode: {standard_back.mode}')
proxy = Image.new('RGBA', (745, 1040), (255,255,255,0))
font = ImageFont.truetype('DejaVuSans.ttf', 200)
#ImageDraw.Draw(proxy).text((40,420), 'PROXY', fill=(0,0,0,100), font=font)
proxy=proxy.rotate(45)
width = 2.5
height = 3.5
sheet_w = 5100
sheet_h = 6600
dpi = 600
sheet_color_r = 255
sheet_color_g = 255
sheet_color_b = 255
sheet_color_a = 1
fill_page = False
offsets=[(150,75),(1775,75),(3350,75),
        (150,2250),(1775,2250),(3350,2250),
        (150,4400),(1775,4400),(3350,4400)]


with open(deck) as csv_deck:
    reader = csv.reader(csv_deck, delimiter=',')
    
    sheet = Image.new('RGBA', (sheet_w, sheet_h), (sheet_color_r,sheet_color_g,sheet_color_b, sheet_color_a))
    back = Image.new('RGBA', (sheet_w, sheet_h), (sheet_color_r,sheet_color_g,sheet_color_b, sheet_color_a))
    if fill_page == True:
        print("filling...")
        sheet.paste( (sheet_color_r,sheet_color_g,sheet_color_b), (0, 0, sheet.size[0], sheet.size[1]))
        back.paste( (sheet_color_r,sheet_color_g,sheet_color_b), (0, 0, back.size[0], back.size[1]))
    
    card_count = 0
    sheet_count = 0
    for row in reader:
        qty=int(row[0])
        q=f'q=e%3A{row[2]}+cn%3A{row[3]}'        
        json = requests.get(f'{q_base}{q}').json()        
        face_png = None
        back_png = standard_back
        try:
            png_uri = json['data'][0]['image_uris']['png']
            card_name = json['data'][0]['name'].lower().replace(' ', '_').replace(',', '-')
        
            png_data = requests.get(png_uri).content
            face_png = Image.open(io.BytesIO(png_data))               
        except:            
            face_uri = json['data'][0]['card_faces'][0]['image_uris']['png']
            back_uri = json['data'][0]['card_faces'][1]['image_uris']['png']
            
            face_png_data = requests.get(face_uri).content
            back_png_data = requests.get(back_uri).content
            face_png = Image.open(io.BytesIO(face_png_data))
            back_png = Image.open(io.BytesIO(back_png_data))
            
        if face_png == None or back_png == None:
            print(f'Failed to find images for ')
            continue
        
        proxy_card_face = Image.alpha_composite(face_png, proxy)
        proxy_card_back = Image.alpha_composite(back_png, proxy)   
        proxy_card_face = proxy_card_face.resize((math.floor(width * dpi), math.floor(height * dpi)))
        proxy_card_back = proxy_card_back.resize((math.floor(width * dpi), math.floor(height * dpi)))
            
        for z in range(qty):
            sheet.paste(proxy_card_face, offsets[card_count])            
            back.paste(proxy_card_back, ((sheet_w - offsets[card_count][0] - proxy_card_back.width), offsets[card_count][1]))
            card_count += 1
                    
            if card_count >= 9:
                card_count = 0
                sheet_count += 1            
                sheet_name = f'{card_image_dir}sheet_{sheet_count}.png'
                back_name = f'{card_image_dir}sheet_{sheet_count}_back.png'
                print(sheet_name)
                sheet.save(sheet_name, dpi=(dpi, dpi))
                back.save(back_name, dpi=(dpi, dpi))
                sheet = Image.new('RGBA', (sheet_w, sheet_h), (sheet_color_r,sheet_color_g,sheet_color_b, sheet_color_a))
                back = Image.new('RGBA', (sheet_w, sheet_h), (sheet_color_r,sheet_color_g,sheet_color_b, sheet_color_a))
                if fill_page == True:
                    sheet.paste( (sheet_color_r,sheet_color_g,sheet_color_b), (0, 0, sheet.size[0], sheet.size[1]))
                    back.paste( (sheet_color_r,sheet_color_g,sheet_color_b), (0, 0, back.size[0], back.size[1]))
           
    sheet_name = f'{card_image_dir}sheet_{sheet_count+1}.png'
    back_name = f'{card_image_dir}sheet_{sheet_count+1}_back.png'
    print(sheet_name)
    sheet.save(sheet_name, dpi=(dpi, dpi))
    back.save(back_name, dpi=(dpi, dpi))
        
        
