import requests
import sys
import os
import sqlite3
import overcastLogin
from bs4 import BeautifulSoup

# Send the HTML POST request required to change the saved location in the serverUpdate
# player is the webplayer html, time is the new time, and version is the version provided by the server
def updateServers(player, time, version):
	update = session.post("https://overcast.fm/podcasts/set_progress/%s" % player.get('data-item-id'), headers = { "Content-Type": "application/x-www-form-urlencoded" }, data = {"p": time, "speed": "0", "v": version } )
	return update.text # the server provides the version number necessary to preform the next update request

# Open the internet session with the required cookies
session = requests.session()
# Login if not logged in
if not os.path.isfile("%s\\UUID.txt" % sys.path[0]):
	print("No cookie detected, logging in!")
	overcastLogin.login()

uuid = open("%s\\UUID.txt" % sys.path[0],"r")
session.cookies.set("o",uuid.read())
uuid.close()


# An sqlite database will be used to keep track of the downloaded podcasts
# A table in the database will track the podcast, title, file location, data-item-id, and play location of each podcast downloaded
conn = sqlite3.connect("%s\\overcast.db" % sys.path[0])
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='podcasts';")
if (c.fetchall() == []):
	print("Creating new table!")
	c.execute("CREATE TABLE podcasts (dataItemId INTEGER(15), time INTEGER, podcast VARCHAR(255), title VARCHAR(255), location VARCHAR(255));")

while True:
	res = input("Download New?> ")
	if (res == "y"):
		# Download the Overcast Homepage
		try:
			mainPage = session.get("https://overcast.fm/")
		except requests.exceptions.ConnectionError:
			print("Connection Error!")
			break
		# Parse the downloaded html
		parsedOvercast = BeautifulSoup(mainPage.text,"html.parser")
		allCasts = parsedOvercast.find_all("a", class_="episodecell")
		podcastNum = 0
		# Iterate through the list of podcasts
		for podcast in allCasts:
			print("%d.) %s: %s" % ((podcastNum + 1), podcast.find("div", class_="caption2 singleline").get_text(),podcast.find("div", class_="title singleline").get_text()))
			podcastNum += 1
		podcastNum -= 1
		while True:
			try:
				# Select a podcast, catching any out-of-range entries
				selectedCast = (int(input("Which podcast?> ")) - 1)
				if ((selectedCast > podcastNum) or (selectedCast < 0)):
					raise ValueError
				break
			except ValueError:
				print("Invalid Number!")
		selCast = allCasts[selectedCast]
		selCastShow = selCast.find("div", class_="caption2 singleline").get_text()
		selCastTitle = selCast.find("div", class_="title singleline").get_text()
		print("You have selected %d which is %s: %s" % ((selectedCast + 1), selCastShow, selCastTitle))
		# Download the podcast page
		podcastHREF = "https://overcast.fm%s" % selCast.get('href')
		print("This podcast is at %s" % podcastHREF)
		try:
			podcastPage = session.get(podcastHREF)
		except requests.exceptions.ConnectionError:
			print("Connection Error!")
			break
		# Parse the downloaded html
		parsedPodcast = BeautifulSoup(podcastPage.text,"html.parser")
		audioPlayer = parsedPodcast.find(id="audioplayer")
		# Set the update number to the one provided by the server
		# This must be set by the return value of the updateServers function every time it is called
		serverUpdate = audioPlayer.get('data-sync-version')
		if not os.path.exists("%s\\podcasts\\%s\\" % (sys.path[0], selCastShow)):
			os.makedirs("%s\podcasts\\%s\\" % (sys.path[0], selCastShow))
		with open ("%s\\podcasts\\%s\\%s.mp3" % (sys.path[0], selCastShow, audioPlayer.get("data-item-id")), "wb") as pFile:
			try:
				pResponse = session.get(audioPlayer.find("source").get("src"), stream=True)
			except requests.exceptions.ConnectionError:
				print("Connection Error!")
				break
			for chunk in pResponse.iter_content(1024):
				pFile.write(chunk)
		
		# Test code to see if setting the time works as expected
		serverUpdate = updateServers(audioPlayer, input("New Time?> "), serverUpdate)
		print(serverUpdate)
		
		break
	elif (res == "n"):
		break
	else:
		print("Invalid entry!")