import requests
import sys
import re
import zipfile
import os
from bs4 import BeautifulSoup
from tqdm import tqdm

def extract_song_info(table):	
	row_1 = table.find_all('tr')[0]
	row_2 = table.find_all('tr')[1]
	row_3 = table.find_all('tr')[2]
	row_4 = table.find_all('tr')[3]
	row_5 = table.find_all('tr')[4]

	song = {}
	song["uploader"] = row_1.find_all('th')[1].find('a').text
	song["song"] = row_2.find_all('td')[0].text.split(' ', 1)[1]
	song["version"] = row_2.find_all('td')[1].text.split(' ', 1)[1]
	song["author"] = row_3.find_all('td')[0].text.split(' ', 1)[1]
	song["difficulties"] = row_3.find_all('td')[1].text.split(' ', 1)[1]
	result = re.findall(r'\d+', row_4.td.text)
	result = list(map(int, result))
	song["downloads"] = result[0]
	song["finished"] = result[1]
	song["completionRate"] = (0 if result[1] == 0 else result[0]/result[1])
	song["likes: "] = result[2]
	song["dislikes: "] = result[3]
	song["rating"] =  (0 if result[2]+result[3] == 0 else result[2]/(result[2]+result[3]))
	song["lightingEvents"] = str("Yes" in row_4.find_all('td')[1].text)
	song["download"] = row_5.td.a.get('href')

	return song 

def main():
	if len(sys.argv) != 2:
		print("Usage: python3 main.py [nameOfSong]" )
		quit(1)

	songName = sys.argv[1]
	
	extractDir = ""
	if not os.path.isfile('configFile.txt'):
		print("You need a \'configFile.txt\' in the same directory as this script.\nInside please put your beatsaber custom songs directory.")
	else:
		with open('configFile.txt', 'r') as configFile:
			extractDir = configFile.readline()
			extractDir = extractDir.strip()
				
	print(extractDir)

	with requests.session() as client:
		url = 'https://beatsaver.com/search/all/' + songName
		r = client.get(url)

		soup = BeautifulSoup(r.content, 'html.parser')
		
		songList = []
		for table in soup.find_all('table'):
			if "song" in table.get('id'):
				songList.append(extract_song_info(table))
		print(songList)

		
		for song in songList:
			response = input("Do you want to download the song " + song['song'] + "? [y|N]")
			if(response == "y"):
				url = song['download']
				response = requests.get(url, stream=True)
				with open((song['song']+".zip"), "wb") as handle:
					for data in tqdm(response.iter_content()):
						handle.write(data)
				print("unzipping")
				zip_ref = zipfile.ZipFile(song['song']+".zip", 'r')
				zip_ref.extractall(extractDir)
				zip_ref.close()
				
				os.remove(song['song'] + ".zip")

if __name__== "__main__":
	main();
