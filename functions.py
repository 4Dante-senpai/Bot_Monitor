import PIL #fades
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import requests
from twython import Twython # fades
import os
import time

#---------------------------------------------#
#-FUNCIONES USADAS EN EL MAIN DEL BOT_MONITOR-#
#---------------------------------------------#

def check_internet():
	url='http://www.google.com/'
	timeout=5
	try:
		__ = requests.get(url, timeout=timeout)
		return True
	except requests.ConnectionError:
		return False
		
def check_nanopool():
	url='https://api.nanopool.org/v1/xmr/pool/activeminers'
	timeout=5
	try:
		data = requests.get(url, timeout=timeout)
		if data.json().get('status') == True:
			return data.json()
		else:
			return None
	except requests.ConecctionError:
		print ('Error al usar la API de Nanopool')
		return None		

def check_background():
	bg = Image.open('bg.jpg', 'r')
	if bg.size == (475,110) :
		return bg
	else:
		bg = bg.resize((475,110))
		bg.save('bg.jpg')
		return bg	
		
def check_durmiendo(gpus,min_temp):
	lista_durmiendo = []
	for gpu in gpus:
		if gpu.temp <= min_temp	:
			print ('La gpu ' + gpu.name + ' esta durmiendo')
			lista_durmiendo.append(gpu)
	return lista_durmiendo
				
def reiniciar(twitter,estado):
	try: 
		twitter.update_status(status = estado)
		print ('Tweet realizado con exito')
	except:
		print ('Error al generar el tweet, se reiniciara igualmente')
	print ('El dispositivo se reiniciara en 30 segundos')
	time.sleep(30)
	print ("REBOOTING")
	time.sleep(2)
	os.system("shutdown -t 0 -r -f")
	time.sleep(600)	
			
def generar_imagen(gpus,max_fan,max_temp):
	total = ''
	en_peligro = []
	bg = check_background()
	font = ImageFont.truetype("arial.ttf", 25)
	img = Image.new("RGB", (475,110*len(gpus)))
	draw = ImageDraw.Draw(img)
	posy = 0
	for gpu in gpus:
		offset = ((0,posy))
		img.paste(bg, offset)
		posy = posy + 110
		if gpu.temp >= max_temp :
			#print ('La temp es alta')
			gpu.temp_check(1)
			en_peligro.append(gpu)
		else:
			#print ('La temp es normal')
			gpu.temp_check(0)
		if gpu.fan != None:  #Workaround para la notebook
			if gpu.fan >= max_fan :
				#print ('El fan es alto')
				gpu.fan_check(1)
				en_peligro.append(gpu)
			else:
				#print('El fan es normal')
				gpu.fan_check(0)	
		texto = gpu.generar_texto()
		total = total + texto	
	draw.text((10, 10), total , fill=(255,255,255), font= font)
	draw = ImageDraw.Draw(img)
	img.save("cache.png")
	en_peligro = list(set(en_peligro)) 
	return (en_peligro)
	
	
	
def leer_config():
	data = {}
	archivo = open("config.txt", 'r')	
	texto = archivo.read()
	texto_line = texto.split('\n')
	for line in texto_line:
		if 'time' in line:
			data['tiempo'] = int(line.split(' ')[1].strip())
			#print ('Se cargo el tiempo correctamente')
		if 'user' in line:
			data['user'] = str(line.split(' ')[1].strip())
			#print ('se cargo el usuario correctamten')
		if 'max_fan' in line:
			data['max_fan'] = int(line.split(' ')[1].strip())
			#print ('se cargo el max_fan correctamente')
		if 'max_temp' in line:
			data['max_temp'] = int(line.split(' ')[1].strip())
			#print ('se cargo el max_temp correctamente')
		if 'min_temp' in line:
			data['min_temp'] = int(line.split(' ')[1].strip())
			#print ('se cargo el min_temp correctamente')
		if 'CONSUMER_KEY' in line:
			data['CONSUMER_KEY'] = str(line.split(' ')[1].strip())
			#print ('Se cargo el consumer_key correctamente')
		if 'CONSUMER_SECRET' in line:
			data['CONSUMER_SECRET'] = str(line.split(' ')[1].strip())
			#print ('Se cargo el consumer_secret correctamente')
		if 'ACCESS_KEY' in line:
			data['ACCESS_KEY'] = str(line.split(' ')[1].strip())
			#print ('Se cargo el access_key correctamente')
		if 'ACCESS_SECRET' in line:
			data['ACCESS_SECRET'] = str(line.split(' ')[1].strip())
			#print ('Se cargo el access_secret correctamente')	
		if 'only_alert' in line:
			data['only_alert'] = int(line.split(' ')[1].strip())
		if 'gpu_amount' in line:
			data['gpu_amount'] = int(line.split(' ')[1].strip())
		if 'force_reset' in line:
			data['force_reset'] = int(line.split(' ')[1].strip())		
	return data
