# -*- coding: utf-8 -*-
import feedparser
import urllib
import json
import telegram
from telegram.error import NetworkError, Unauthorized
import time
from datetime import datetime
import pytz
from pytz import timezone
import schedule
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from multiprocessing import Process
import multiprocessing

weekdays = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
months = ["Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno","Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"]

TOKEN_TELEGRAM = '322540065:AAG1oe2RO1FaOnaqt6CSN6mK92twcq9fbzA' #altre rss
MY_CHAT_ID = 31923577
bot = telegram.Bot(TOKEN_TELEGRAM)
keyboard = [	
				[
					InlineKeyboardButton("<<", callback_data='previous'),
					InlineKeyboardButton(">>", callback_data='next'),
				]
					]
reply_markup = InlineKeyboardMarkup(keyboard)

previous_title = 0
avviato = False
userChoicebtnTelegramArrayIndex = 0

try:
	update_id = bot.getUpdates()[0].update_id
except IndexError:
	update_id = None
listDaily=[]
def RSS():
	global avviato
	global listDaily
	global previous_title
	feed = feedparser.parse(	"http://www.servizitelevideo.rai.it/televideo/pub/rss101.xml"	)
	title = feed.entries[0].title.encode('utf-8')
	description = feed.entries[0].description.encode('utf-8')
	#print description
	if title != previous_title:
		previous_title = title
		oggi_utc = datetime.now(timezone('UTC'))
		oggi = oggi_utc.astimezone(timezone('Europe/Rome'))
		format = "%Y-%m-%d %H:%M:%S %Z%z"
		print (oggi.strftime(format))
		
		nomeGiorno = weekdays[	oggi.weekday() ]
		nomeMese = months[	oggi.month - 1 ]
		anno = oggi.year
		nGiorno = oggi.day
		ora = str(oggi.hour) + ":" + str(oggi.minute)
		TITOLO = "<strong>" + title.decode('utf-8') + "</strong>"
		DATA =  "\n<i>" + ora + " " + nomeGiorno + " " + str(nGiorno) + " " + nomeMese + " " + str(anno) + "</i>"
		#print(description)
		ARTICOLO = description
		print( title.decode('utf-8') )
		text = TITOLO + DATA + "\n\n<i>" + "\n".join(ARTICOLO.decode('utf-8').split("\n")[1:]) + "</i>"
		if len(listDaily) == 0: #send only one message per day and if user wants to read more daily news, they use arrows
			bot.sendMessage(chat_id = MY_CHAT_ID,text=text, parse_mode="Html", disable_web_page_preview=True,reply_markup = reply_markup)
		listDaily.append(text)
	if avviato == False:
		p = multiprocessing.Process(target=listenIncomingUserRequests)
		p.start()
		avviato = True
	
def echo():
	RSS()

def send_photo_telegram_televideo_103():
	try:
		bot.sendPhoto(chat_id = MY_CHAT_ID, photo = "http://www.servizitelevideo.rai.it/televideo/pub/tt4web/Nazionale/16_9_page-103.png")
	except:
		pass
		
def delete_old_entries():
	global listDaily
	del listDaily[:] #delete all content
	
	
def listenIncomingUserRequests():
	global update_id
	global userChoicebtnTelegramArrayIndex
	global listDaily
	'''
	CHANGE
	'''
	listDaily.append(r"""20.01 "Il futuro dell'Ue non si gioca sul fiscal compact sì o no, altrimenti facciamo una battaglia ideologica, nel senso negativo del termine". Lo ha puntualizzato il ministro dell'Economia, Padoan. Padoan ha ammesso che il fiscal compact presenta "problemi tecnici" che già sono stati posti all'attenzione della commissione Ue dall'Italia e da altri Paesi. E quindi si possono immaginare modi per "migliorarlo e aggiustarlo" ma "il futuro dell'Europa si deve giocare su cose più serie".""")
	listDaily.append(r"""19.36 E' indagato per lesioni il macchinista della metropolitana romana che si trovava sul convoglio che, ripartendo da una fermata, ha trascinato per metri una donna che era rimasta incastrata dopo la chiusura delle porte. La procura di Roma ha acquisito una serie di filmati oltre all'informativa messa a punto dalla polizia.""")
	#print("len(listDaily): {}".format(len(listDaily)))
	#print("userChoicebtnTelegramArrayIndex: ".format(userChoicebtnTelegramArrayIndex))
	while True:
		for update in bot.getUpdates(offset=update_id, timeout=10):
			update_id = update.update_id + 1
			if update:
				try:
					#print("len(listDaily): {}".format(len(listDaily)))
					
					query = update.callback_query
					if query is not None:
						bot.answerCallbackQuery(callback_query_id = query.id,)
						print("user :{}   {}".format(userChoicebtnTelegramArrayIndex,query.data))
						if query.data == "next":
							userChoicebtnTelegramArrayIndex = userChoicebtnTelegramArrayIndex + 1
							userChoicebtnTelegramArrayIndex = min(userChoicebtnTelegramArrayIndex, len(listDaily)-1)
						if query.data == "previous":
							userChoicebtnTelegramArrayIndex = userChoicebtnTelegramArrayIndex - 1
							userChoicebtnTelegramArrayIndex = max(userChoicebtnTelegramArrayIndex, 0)
						index = userChoicebtnTelegramArrayIndex
						try:
							bot.editMessageText(text=listDaily[index],
									    chat_id = query.message.chat_id,
									    message_id = query.message.message_id,
									    reply_markup = reply_markup,
									    parse_mode="Html")
						except telegram.error.BadRequest:
							pass
							#print ("There is no text in the message to edit")
					update_id = update.update_id + 1
				except Exception as e:
					print("error listenIncomingUserRequests(): {}".format(e))
		time.sleep(1)
	
#schedule.every(1).minutes.do( send_photo_telegram_televideo_103 )
schedule.every().day.at("12:00").do( delete_old_entries )
'''
p = multiprocessing.Process(target=listenIncomingUserRequests)
p.start()
'''
while True:
	try:
		echo()
		time.sleep(10)
		schedule.run_pending()
	except NetworkError:
		time.sleep(1)
	except Unauthorized:
		update_id += 1
