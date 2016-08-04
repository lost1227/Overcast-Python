import requests
import sys
from bs4 import BeautifulSoup

def updateServers(player, time, version):
	update = session.post("https://overcast.fm/podcasts/set_progress/%s" % player.get('data-item-id'), headers = { "Content-Type": "application/x-www-form-urlencoded" }, data = {"p": time, "speed": "0", "v": version } )
	return update.text

session = requests.session()
uuid = open("%s\UUID.txt" % sys.path[0],"r")
session.cookies.set("o",uuid.read())
mainPage = session.get("https://overcast.fm/")
parsedOvercast = BeautifulSoup(mainPage.text,"html.parser")
allCasts = parsedOvercast.find_all("a", class_="episodecell")
podcastNum = 0
for podcast in allCasts:
	print("%d.) %s: %s" % ((podcastNum + 1), podcast.find("div", class_="caption2 singleline").get_text(),podcast.find("div", class_="title singleline").get_text()))
	podcastNum += 1
podcastNum -= 1
while True:
	try:
		selectedCast = (int(raw_input("Which podcast?> ")) - 1)
		if ((selectedCast > podcastNum) or (selectedCast < 0)):
			raise ValueError
		break
	except ValueError:
		print("Invalid Number!")
selCast = allCasts[selectedCast]
selCastShow = selCast.find("div", class_="caption2 singleline").get_text()
selCastTitle = selCast.find("div", class_="title singleline").get_text()
print("You have selected %d which is %s: %s" % ((selectedCast + 1), selCastShow, selCastTitle))
podcastHREF = "https://overcast.fm%s" % selCast.get('href')
print("This podcast is at %s" % podcastHREF)
podcastPage = session.get(podcastHREF)
parsedPodcast = BeautifulSoup(podcastPage.text,"html.parser")
audioPlayer = parsedPodcast.find(id="audioplayer")
serverUpdate = audioPlayer.get('data-sync-version')
serverUpdate = updateServers(audioPlayer, raw_input("New Time?> "), serverUpdate)
print(serverUpdate)
