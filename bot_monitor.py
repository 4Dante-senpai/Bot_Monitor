import time 
from functions import *
from time import gmtime, strftime
from twython import Twython # fades
import wmi #fades
#from win32 import win32api
import os
#import pywin32 # fades  
#NECESARIO PARA LOS BINARIOS DE WINDOWS

w = wmi.WMI(namespace="root\OpenHardwareMonitor")

class gpu_obj():
	def __init__(self,datos):
		self.name = datos.get('name') 
		self.gpu_clock = datos.get('gpu_clock')
		self.mem_clock = datos.get('mem_clock')
		self.temp = datos.get('temp')
		self.fan = datos.get('fan')
		self.flagtemp = False
		self.flagfan = False
			
	def imprimir(self):
		print ('Name: ' + self.name)
		print ('GPU: ' + str(self.gpu_clock) + 'Mhz')
		print ('MEM: ' + str(self.mem_clock) + 'Mhz')
		print ('Temp: ' + str(self.temp) + 'ºC')
		print ('Fan: ' + str(self.fan) + ' %')
		
	def generar_texto(self):
		name = (self.name + '\n')
		clocks = ('Core: ' + str(self.gpu_clock) + 'Mhz   |   MEM: ' + str(self.mem_clock) + 'Mhz\n')
		temps = ('Temp: ' + str(self.temp)[0:2] + 'ºC   |   Fan: ' + str(self.fan) + ' %\n\n')
		total = name + clocks +temps
		return total
	
	def control(self,max_fan,max_temp):
		control_datos = {}
		fan_alto = False
		temp_alta = False
		print ('FAN A :' + str(self.fan) + '  Y LA ALERTA A LOS: ' + str(max_fan))
		print ('TEMP A :' + str(self.temp) + '  Y LA ALERTA A LOS: ' + str(max_temp))
		# if (max_fan != None) and (self.fan != None):
			# if self.fan >= max_fan:
				# fan_alto = True
				# print (fan_alto)
				# control_datos['fan_alto'] = fan_alto
		if max_temp != None :
			if self.temp >= temp_alta :
				temp_alta = True
				control_datos['temp_alta'] = temp_alto
		return (control_datos)
		
	def temp_check(self,estado):
		if estado == 1:
			self.flagtemp = True
		elif estado == 0:
			self.flagtemp = False
			
	def fan_check(self,estado):
		if estado == 1:
			self.flagfan = True
		elif estado == 0:
			self.flagfan = False		

def etiquetar(gpus,user):
	estado = ('')
	for gpu in gpus:
		pre_estado = ('')
		nombre = gpu.name
		if gpu.flagfan == True:
			fan = gpu.fan
			pre_estado = ('\nLa GPU ' + str(nombre) + ' tiene el fan al ' + str(fan)[0:2] +'%')
		if gpu.flagtemp == True:
			temp = gpu.temp
			if pre_estado == '' :
				pre_estado = ('\nLa GPU ' + str(nombre) + ' tiene la temp a ' + str(temp)[0:2] + 'ºC')
			else:
				pre_estado = (str(pre_estado) + ' y la temp a ' + str(temp)[0:2] + 'ºC')
		estado = (str(estado) + str(pre_estado) + '\n')
	return ('Hey ' + str(user) + '\n' + estado)


def tweet(estado):
	pic_arch = open("cache.png", "rb") #Si o si rb para cargar el archivo
	intentos = 1
	while intentos <=5:
		try :
			pic = twitter.upload_media(media = pic_arch)
			twitter.update_status(status = estado  , media_ids = pic.get("media_id"))
			print ("Tweet realizado a las: " + strftime("%d/%m/%Y %H:%M:%S"))
			break
		except:
			print ("Error al realizar el tweet, se intentara nuevamente en 20 seggundos, hasta 5 intentos")
			intentos = intentos + 1
			time.sleep(20)
	if intentos >= 5:
		print ('Se omitira la carga hasta el proximo tweet')
	
#class hardware():
#	def __init__(self):

def datos_gpus():
	sensors_infos = w.Sensor()
	lista_sensores = []
	for sensor in sensors_infos:
		if sensor.Name.count('GPU') == 1:
			data = {'id' : sensor.Parent, 'name' : sensor.Name, 'type' : sensor.SensorType, 'value' : sensor.Value}						
			lista_sensores.append(data)
	return lista_sensores

def datos_hardware():
	nombres_gpu = w.Hardware()
	dic_devices = {}
	for nombre in nombres_gpu:
		dic_devices[nombre.Identifier] = nombre.Name
	return dic_devices
	
def cargar_gpus(datos,devices):
	gpus = {}
	for sensor in datos:
		gpuid = sensor['id']
		# print ("VGA: " + gpuid)
		# print ("SENSOR: ")
		# print (sensor)
		# print ("\n")
		datos_f = {}
		datos_f['name'] = devices[gpuid]  #Se lo actualiza cada vez que pone un sensor
		for dato in sensor:							
			if sensor[dato] == 'Temperature':
				datos_f['temp'] = sensor.get('value')
			if sensor[dato] == 'Clock':
				if sensor.get('name').count('Core') == 1:
					datos_f['gpu_clock'] = int(sensor.get('value'))
				if sensor.get('name').count('Memory') == 1:
					datos_f['mem_clock'] = int(sensor.get('value'))
			if sensor[dato] == 'Control': 
				if sensor.get('name').count('Fan') == 1:
					datos_f['fan'] = int(sensor.get('value'))
		if not gpuid in gpus:
			gpus[gpuid] = datos_f
		else:
			gpus[gpuid].update(datos_f)
	gpu_list_obj = []
	for gpu in gpus:			
		vga = gpu_obj(gpus[gpu])
		gpu_list_obj.append(vga)	
	return gpu_list_obj


if __name__ == "__main__":
	print ("El script se empezo a ejecutar correctamente a las: " + strftime("%d/%m/%Y %H:%M:%S\n"))
	config = leer_config()
	print (config)
	nano = check_nanopool()
	print (nano)
	try :
		twitter = Twython(config.get('CONSUMER_KEY'), config.get('CONSUMER_SECRET'), config.get('ACCESS_KEY'), config.get('ACCESS_SECRET'))
		print ("Logeo en Twitter hecho correctamente")
		try: 
			devices = datos_hardware()
			print ("Hardware leido correctamente")
			while True:
				try:
					datos = datos_gpus()
					if len(datos) == 0 :
						print ("Error no se detecto ninguna GPU, por favor cerrar el script, verificar los drivers y/o abrir OpenHardwareMonitor")
						time.sleep(999999)
						
						#Reiniciar aca?
						
						
					print ("Sensores leidos correctamente")
					try:						
						gpus = cargar_gpus(datos,devices)
						if len(gpus) < config.get('gpu_amount') :
							print ('Cantidad de gpus incorrectas')
							print ("Se necesita reiniciar")
							if config.get('force_reset') == 1:
								estado = ("Hey! " + config.get('user') + '\n¡No se detectaron todas las gpu!\nSe reiniciara el rig')
								reiniciar(twitter,estado)
							else:
								print ('No se especifico el "force reset" en los parametros')
								print ('Se notificara via Twitter pero no se reiniciara el rig')
								estado = ("Hey! " + config.get('user') + '\n¡No se detectaron todas las GPU!\nTe recominedo que revises a ver que pasa')
								enviado = False
								intentos = 0
								while ((enviado == False) and (intentos <= 5)):
									try:
										twitter.update_status(status = estado)
										print ('Tweet realizado con exito')
										enviado = True
									except:
										print ('Error al enviar tweet, se intentara nuevamente')
										time.sleep(10)
										intentos = intentos + 1
						en_peligro = generar_imagen(gpus,config.get('max_fan'),config.get('max_temp'))
						durmiendo = check_durmiendo(gpus,config.get('min_temp'))
						internet = check_internet()
						if ((len(durmiendo) != 0) and (internet == True)):
							if config.get('force_reset') == 1 :	
								print ('Hay ' + str(len(durmiendo)) + ' placas durmiendo y hay conexion a internet')
								
								#Chequear conexcion con Nicehash/nanopool
												
								print ("Se necesita reiniciar")
								estado = ("Hey! " + config.get('user') + '\n¡Algunas gpu estan durmiendo!\nSe reiniciara el rig')
								reiniciar(twitter,estado)
							else:
								print ('No se especifico el "force reset" en los parametros')
								print ('Se notificara via Twitter pero no se reiniciara el rig')
								estado = ("Hey! " + config.get('user') + '\n¡Algunas gpu estan durmiendo!\nTe recominedo que revises a ver que pasa')
								enviado = False
								intentos = 0
								while ((enviado == False) and (intentos <= 5)):
									try:
										twitter.update_status(status = estado)
										print ('Tweet realizado con exito')
										enviado = True
									except:
										print ('Error al enviar tweet, se intentara nuevamente')
										time.sleep(10)
										intentos = intentos + 1
						elif (internet == False):
							print ('Hay ' + str(len(durmiendo)) + ' placas durmiendo, pero no hay conexion a internet')
							print ('El script se continuara ejecutando con normalidad')
						print ("Infomracion generada correctamente")
						if config.get('only_alert') == 1:
							if len(en_peligro) != 0:
								estado = etiquetar(en_peligro, config.get('user'))
								tweet(estado)
							else:
								print('Temperaturas y velocidad correctas')
							time.sleep(config.get('tiempo')*60)
						else: 
							if len(en_peligro) == 0:
								estado = u'Temperaturas y velocidades normales'
								tweet(estado)
								time.sleep(config.get('tiempo')*60)
							else:
								estado = etiquetar(en_peligro, config.get('user'))
								tweet(estado)
								time.sleep(config.get('tiempo')*60)		
					except (RuntimeError, TypeError, NameError) as e:
						print (e)
						print("Error al generar la imagen")
				except (RuntimeError, TypeError, NameError) as e:
					print (e)
					print ("Error al leer los sensores")
		except (RuntimeError, TypeError, NameError) as e:
			print (e)
			print("Error al leer el hardware")
	except (RuntimeError, TypeError, NameError) as e:
		print (e)
		print ("Error en el logeo a Twitter")




















# if __name__ == "__main__":
	# print ("El script se empezo a ejecutar correctamente a las: " + strftime("%d/%m/%Y %H:%M:%S\n"))
	# config = leer_config()
	# print (config)
	# try :
		# twitter = Twython(config.get('CONSUMER_KEY'), config.get('CONSUMER_SECRET'), config.get('ACCESS_KEY'), config.get('ACCESS_SECRET'))
		# print ("Logeo en Twitter hecho correctamente")
		# try: 
			# devices = datos_hardware()
			# print ("Hardware leido correctamente")
			# while True:
				# datos = datos_gpus()
				# if config.get('gpu_amount') != None :
					# print ('Se va chequear la cantidad de gpus')
					# print ('Cantidad de GPUS detectadas ' + str(len(datos)))
					# if len(datos) >= config.get('gpu_amount'):
						# print ('Cantidad de gpus correctas')
					# else :
						# print ('Cantidad de gpus INCORRECTAS')
						# print ('El dispositivo se reiniciara en 30 segundos')
						# time.sleep(30)
						# print ("REBOOTING")
						# time.sleep(2)
						# #os.system("shutdown -t 0 -r -f")
				# print ("Sensores leidos correctamente")
				# try:						
					# gpus = cargar_gpus(datos,devices)
					# en_peligro = generar_imagen(gpus,config.get('max_fan'),config.get('max_temp'))
					# print ("Infomracion generada correctamente")
					# if config.get('only_alert') == 1:
						# if len(en_peligro) != 0:
							# estado = etiquetar(en_peligro, config.get('user'))
							# tweet(estado)
						# else:
							# print('Temperaturas y velocidad correctas')
						# time.sleep(config.get('tiempo')*60)
					# else: 
						# if len(en_peligro) == 0:
							# estado = u'Temperaturas y velocidades normales'
							# tweet(estado)
							# time.sleep(config.get('tiempo')*60)
						# else:
							# estado = etiquetar(en_peligro, config.get('user'))
							# tweet(estado)
							# time.sleep(config.get('tiempo')*60)		
				# except:
					# print("Error al generar la imagen")
			# #except:
			# #	print ("Error al leer los sensores")
		# except: 
			# print("Error al leer el hardware")
	# except:
		# print ("Error en el logeo a Twitter")


	
	

