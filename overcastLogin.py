import requests
import sys
def login():
	s = requests.Session()
	login = {'email': input("Enter your email> "), 'password': input("Enter your password> ")}
	try:
		r = s.post("https://overcast.fm/login", data=login)
	except requests.exceptions.ConnectionError:
		print("You are not connected to the Internet!")
		exit()
	print("Your UUID is : %s" % s.cookies["o"])
	f = open("%s\\UUID.txt" % sys.path[0],"w")
	f.write(s.cookies['o'])
	f.close()
