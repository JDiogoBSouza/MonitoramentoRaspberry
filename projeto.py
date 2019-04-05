
# ISRAEL MEDEIROS FONTES
import math
# --Algoritmo feito em python --

import os, re
import time
import Adafruit_ADS1x15
import Adafruit_DHT
import thingspeak
import math
import datetime

#rede = raw_input("Digite o IP/mascara: ")

GAIN = 1
ADC_SOM = 0
ADC_LUZ = 2
GPIO_TEMP = 23

network = '192.168.0.0/24'
comand = "nmap -sP " + network + " | egrep -o " + network[:3] + ".* " 
totalWatts = 0 
wattsPcs = 0 #Consumo de um computador por minuto
channelThingspeak = thingspeak.Channel(id=728245, write_key='NIGM0C4XPR3VG5WX')
channelThingspeak2 = thingspeak.Channel(id=751523,write_key='I1JAE0U53ET1PJLK')

adc = Adafruit_ADS1x15.ADS1115()
dht11 = Adafruit_DHT.DHT11

def consumptionOfPcs():
	tempoAnterior = 0
	if( (int(time.time())-tempoAnterior ) >= 60 ):
		tempoAnterior = int(time.time())
		ipsOn = "".join(os.popen(comand).readlines()).split()
		qntdDePcs = len(ipsOn)-1
		totalWatts = totalWatts + qntDePcs*wattsPc1
	
def getTemperatura():
	tempT = Adafruit_DHT.read_retry(dht11, GPIO_TEMP)[1]
	if tempT is not None:
		return tempT

def getRuido():
	tempR = 0
	for i in range(200):
		ruido = adc.read_adc(ADC_SOM, gain=GAIN, data_rate=860) 
		if(ruido > tempR):
			tempR = ruido
	return tempR

def getLuminosidade():
	luminosidade = adc.read_adc(ADC_LUZ, gain=GAIN)
	return round((luminosidade*0.00377273070),2)

def sendThings(temp, ruid, lumi, cons, pres, usoAr, usoluzes):
	update = {'field1': temp, 'field2': ruid, 'field3': lumi,'field4': cons, 'field5': pres, 'field6': usoAr, 'field7': usoluzes}
	
	fail = True
	
	while( fail == True ) :
		try:
			print('Tentando Enviar dados ao Thingspeak...')
			channelThingspeak.update(update)
			channelThingspeak2.update(update)
			fail = False
			print('Dados Enviados !')
		except:
			print('Falha no Envio !')
			pass

def getTime():
	return int(time.time())

tempoInicial15 = getTime()
tempoInicial5m = getTime()	
tempoInicial5mluz = getTime()	
tempoInicial3mAr = getTime()
tempoInicial1m = getTime()

presenca = 0	
luzes = 0
noite = False
ruido = 0
ctlAr = 0
temperaturaInicial = 0
arLigado = 0
temperaturaAnterior = 0
qntdLuzes = 0

consumoAr = 26.66 #Consumo por minuto
consumoLuzes = 5.33 #Consumo por minuto
consumoTotal = 0
consumoInstant = 0

while(1):

	if(getTime() - tempoInicial1m > 60):
		consumoTotal += consumoAr*arLigado + consumoLuzes*qntdLuzes
		tempoInicial1m = getTime()

	temperaturaAtual = getTemperatura()
	if(temperaturaAnterior - temperaturaAtual == 1.0 and ctlAr == 0):
		temperaturaInicial = temperaturaAnterior;
		ctlAr = 1
		tempoInicial3mAr = getTime()

	if(temperaturaInicial - temperaturaAtual == 2.0 and (getTime() - tempoInicial3mAr) < 1800):
		arLigado = 1

	elif(getTime() - tempoInicial3mAr > 1800):
		ctlAr = 0
	
	if(temperaturaAtual == temperaturaInicial):
		arLigado = 0

	temperaturaAnterior = getTemperatura()

	if( datetime.datetime.now().hour >= 18):
		noite = True
	else :
		noite = False
	
	luz = getLuminosidade();

	if(getTime()-tempoInicial15 > 15):
		ruido = (int(getRuido()*0.12452)/1000.0)*24
		sendThings(temperaturaAnterior, ruido, luz, consumoTotal/1000, presenca, arLigado, qntdLuzes)		
		tempoInicial15 = getTime()

	if(getTime()-tempoInicial5m > 180):
		presenca = 0
		tempoInicial5m = getTime()

	elif(ruido > 41):
		presenca = 1
		tempoInicial5m = getTime()

	if(getTime()-tempoInicial5mluz > 1):
		
		if(luz > 27.5 and luz < 38.0):
			print("Um lado aceso")
			qntdLuzes = 1

		elif(luz > 38.0):
			print("Dois lados acesos")
			qntdLuzes = 2
			
		else:
			print("luzes apagadas")
			qntdLuzes = 0

		tempoInicial5mluz = getTime()
	
	