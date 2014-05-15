Andrew Hannebrink - 2014

These are Python scripts I wrote for Washington University's systems administrators and security analysts. The ciscoctrlparse.py ssh's into every Cisco controller on campus every five minutes with a crontab command, and then runs commands for retrieving which users are logged onto which access points using regular expressions. Then, with this data, the script either constructs or updates a database depending on its existence in the current directory. The database contains two tables, one for indexing clients and their corresponding macaddresses (where each mac address is unique), and a table for indexing connection histories, where client ID is a foreign key referencing the clients table. The history table also contains fields for access point, time of connection, and network.

The next script, ciscoctrlsearch.py, is used by our network security analysts for helping to pinpoint when and whre malicious activity occurs on our network. The command 'python ciscoctrlsearch.py -h' returns its usage:


To search by mac address, use the option "-m "
To search by the client's wustl key, use the option "-c "
To search by time, use the option "-t <'YYYY-MM-DD HH:MM:SS.00'>" (military time surrounded by quote ticks), or <'Month(first 3 letters) DD HH:MM:SS YYYY'>, where YYYY is optional. If a year is not specified, the last occurence of the date will be used. Follow the time with the option "-i ", which specifies how long of a time increment you want to search over"


The program returns a clean easy to read table displaying the clients's username, every time they were connected to an access point during the time window provided by the parameters, which access points they were connected to, and which mac address they were using at the given time. I've also written a very similar pair of scripts for logging into Washington University's Meru controllers, as the University has recently been undergoing a campus-wide shift from Meru to Cisco equipment.

