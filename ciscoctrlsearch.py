#!/usr/bin/python
#Andy Hannebrink
#This script uses the ciscocontroller.db sqlite3 database to allow the user to search client-access point history using wustl key, mac address, and time command line arguments.
#Run '$ python ciscoctrlsearch.py -h' for information about using the script.

import sys
import getopt
import sqlite3
import datetime
import dateutil.parser

dbFilePath = '/DB/FILE/PATH/GOES/HERE'

def main():
	helpBool = False
	searchMac = False
	searchClient = False
	searchTime = False
	searchIncrement = False

	#Connect to the database
	conn = sqlite3.connect(dbFilePath)
	sqdb = conn.cursor()
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hm:c:t:i:')
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			helpBool = True
		if (opt == '-m') & (arg != ''):
			searchMac = True
			macAddressArg = arg.lower()
		if (opt == '-c') & (arg != ''):
			searchClient = True
			clientArg = arg
		if (opt == '-t') & (arg != ''): 
			searchTime = True
			timeArgStr = arg
		if (opt == '-i') & (arg != ''):
			searchIncrement = True
			incrementArg = arg
	
	if helpBool == True:
		print 'To search by mac address, use the option "-m <mac address>"'
		print 'To search by the client\'s wustl key, use the option "-c <wustl key>"'
		print 'To search by time, use the option "-t <\'YYYY-MM-DD HH:MM:SS.00\'>" (military time surrounded by quote ticks), followed by the option "-i <time increment (in minutes)>", which specifies how long of a time increment you want to search over"'
		sys.exit(0)
		
	if (searchTime != True) | (searchIncrement !=True):
		print 'Please search using a start time with the "-t" option, and a time increment with the "-i" option. Use the -h option for more information.'
		sys.exit(-1)
	#Create a query to find the client id of the specified client or macaddress
	query = 'SELECT * FROM clients WHERE '
	#How many ands go into the query search
	if searchMac == True:
		temp = 'macaddress = \'' + macAddressArg + '\''
		query = query + temp
		sqdb.execute(query)
		nameGetter = sqdb.fetchone()
		try:
			(cid, clientArg, ma) = nameGetter
		except:
			print 'No user with mac address ' + macAddressArg + ' found in database.'
			sys.exit(-1)
	elif searchClient == True:
		temp = 'client = \'' + clientArg + '\''
		query = query + temp
	else:
		print 'Please search by mac address or clients wustl name with either the "-m" or "-c" options. Use the "-h" option for help.'
		sys.exit(-1)	

	#clientId will hold the client's primary key id in the table 'clients'
	
	print '####################################################################################################'
	print 'Client\'s wustl key: ' + clientArg
	print '####################################################################################################'
	print 'Access point             Time                               Mac address'
	print '----------------------------------------------------------------------------------------------------' 
	sqdb.execute(query)
	returnClients = sqdb.fetchall()
	for returnClient in returnClients: 
		(clientid, client, macaddress) = returnClient
		

		#Make a second query to find where the client was logged in during the specified time
		query2 = 'SELECT * FROM history WHERE clientid = ' + str(clientid)
		sqdb.execute(query2)
		returnHistory = sqdb.fetchall()
	
		#returnEntries only holds entries from the history table that fall within the supplied times
		timeArg = dateutil.parser.parse(timeArgStr)
		returnEntries = []
		for entry in returnHistory: 
			(hisid, cid, timestr, ap, network) = entry
			time = dateutil.parser.parse(str(timestr))
			timeDelta = time - timeArg	
			if (time > (timeArg-datetime.timedelta(minutes=int(incrementArg)))) & (time < (timeArg+datetime.timedelta(minutes=int(incrementArg)))):
				returnEntries.append(entry)
	
		#Print the output in a pretty table
		#print returnEntries #Returns actual sqlite entries (for debugging purposes)
		for entry in returnEntries:
			(hisid, cid, timestr, ap, network) = entry
			blankStr = '                         '	
			blankStr2 = '                                   '	
			tempStr = ap + blankStr[len(ap):]
			tempStr2 = timestr + blankStr2[len(timestr):]
			print tempStr + tempStr2 + macaddress
	



main()
