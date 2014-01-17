#!/usr/bin/python

#SAMPLE CONTROLLER OUTPUT:

#f Clients................................ 2051
#
#MAC Address       AP Name          Status         W/G/R(LAN) User Name
#----------------- ---------------- -------------- ---------- -----------------------------------------------------
#
#00:06:bb:9d:73:46 AXB335A           Associated   6          N/A
#00:09:ca:ba:65:2f BRX156            Associated   15         genericusername                                                                                                                                                                                              
import re
import paramiko
import datetime
import sqlite3
import os
import logging
import time
import getpass
import getopt
import sys
import pexpect

dbFilePath = '/DATABASE/FILE/PATH/GOES/HERE'


#Connect to the controller, run commands, and return the output in a string
def sshConnectAndGetOutput():
	ssh_cmd = ''
	try: 
		opts, args = getopt.getopt(sys.argv[1:], 'a:')
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(-1)
	for opt, arg in opts:
		if opt == '-a':
			ssh_cmd = 'ssh ' + arg
	try:
		p = pexpect.spawn(ssh_cmd)
		
		# IMPORTANT : PUT THE USER NAME AND PASSWORD INTO NEXT FOR LINES
		p.expect('User:')
		p.sendline('PUT CONTROLLER USERNAME HERE') #USERNAME
		p.expect('Password:')
		p.sendline('PUT CONTROLLER PASSWORD HERE') #PASSWORD
		p.expect('>')
		p.sendline('config paging disable')
		p.expect('>')
		p.sendline('show client summary extended username')
		out = ''
	except:
		print 'Could not connect to controller with command: ' + ssh_cmd
		sys.exit(-1)
	while True:
		try:
			p.expect('\n', timeout=10)
			out += p.before
		except:
			break
	#print out
	return out


#Parse raw output and return a list of lists of info
def parseOutput(out):
	all_info = []
	outsplit = out.splitlines()
	#print outsplit
	for line in outsplit:
		if line == '':
			continue
		else:
			#Finds lines containing a mac address
			match = re.search(r'((\d|\w){2}:){5}(\d|\w){2}', line)
			if match:
				line_info = re.split(r'\s+', line)
				try:
					if (line_info[2]=='Associated') & (line_info[4]!='N/A'):
						all_info.append(line_info)
				except:
					continue
	return all_info
				
#Initializes the database. This method is only called if the database does not exist yet.
def makeDB(db):
	db.execute('''CREATE TABLE clients (id INTEGER PRIMARY KEY AUTOINCREMENT, client text, macaddress text UNIQUE ON CONFLICT FAIL)''')
	db.execute('''CREATE TABLE history (id INTEGER PRIMARY KEY AUTOINCREMENT, clientid INTEGER, time TEXT, accesspoint TEXT, network INTEGER)''')
	print '########## DATABASE INITIALIZED ##########'


#Update the database with the info returned from parseOutput() (which is a list of lists)
def dbUpdate(db, all_info, conn):
	timestamp = datetime.datetime.now()
	for line_info in all_info:
		client = line_info[4]
		macaddress = line_info[0]
		accesspoint = line_info[1]
		network = line_info[3]
		tempmac = (macaddress,)
		db.execute('SELECT macaddress FROM clients WHERE macaddress = ?', tempmac)
		returnObject = db.fetchone()
		lastRowId = db.lastrowid
		if returnObject:
			logging.info('(db): Skipping macddress: %s already found in database.', macaddress)
		else:
			logging.info('(db): New mac address found, inserting %s into database.', macaddress)
			db.execute('INSERT INTO clients VALUES (?,?,?)', [None, client, macaddress])
			lastRowId = db.lastrowid
		db.execute('SELECT id FROM clients WHERE macaddress = ?', tempmac)
		returnObject = db.fetchone()
		clientID = returnObject[0]
		lasRowId = db.lastrowid
		db.execute('INSERT INTO history VALUES (?,?,?,?,?)', [None, clientID, str(timestamp), accesspoint, int(network)])
	conn.commit()
	conn.close()
	
			
def main():
	out = sshConnectAndGetOutput()
	all_info = parseOutput(out)			
	if not os.path.isfile(dbFilePath):
		conn = sqlite3.connect(dbFilePath)
		conn.text_factory = str
		c = conn.cursor()
		makeDB(c)
		dbUpdate(c, all_info, conn)
	else:
		conn = sqlite3.connect(dbFilePath)
		conn.text_factory = str
		c = conn.cursor()
		dbUpdate(c, all_info, conn)
		

			
main()			
