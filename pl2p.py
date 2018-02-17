import webbrowser
from sys import argv, exit
from os import path
from googleapiclient.discovery import build

def clean(string, splitting=True):
	if splitting:
		string = string.split('(')[0].split('[')[0].split('<')[0].split('|')[0]
		string = string.split('feat')[0].split(' ft')[0]
		#Drop asides from the end of strings
	string = string.strip().strip('.').strip('"').strip("'").strip()
	#Strip padding spaces/characters
	return string

def config():
	print("\n\nWelcome to `Playlist 2 Purchase`!\n")
	print("In order to use this service, you'll need a YouTube API key.")
	print("When you're ready, your browser will be opened to the YouTube API page of Google's Developer console.")
	print("Once you've created an API key, you'll need to paste it here.")
	cont = input("When ready, enter any letter to continue.  ")
	if cont:
		webbrowser.open('https://console.developers.google.com/apis/library/youtube.googleapis.com/?q=youtube')
		key = input("\nAPI Key:  ")
		with open('api_key.txt', 'w+') as key_store:
			key_store.write(clean(key, splitting=False))
	print("Your API key has been saved. You can now use PL2P.\n")

def help():
	print("\n\nPlaylist 2 Purchase (PL2P) is a utility that creates purchase links from a YouTube playlist.\n")
	print("The options that can be used with it are [<playlist url> | --config | --help]\n")
	print("This is --help. --config allows you to set your YouTube API key.")
	print("Entering a playlist url will cause a webpage to be openned with links to purchase each song.")
	print("The supported vendors are Google Play and Amazon.\n")
	print("This utility does not currently use affiliate links.")
	print("As such, if you want to support the developer, the best way is to tell her thank you directly.\n")

def create_page(playlist_name, all_songs):
	filepath = playlist_name+' (links).html'
	with open(filepath, 'w+') as page:
		page.write('<html lang="en-US">\n')
		page.write('  <head>\n    <title>'+playlist_name+' (links)</title>\n  </head>\n')
		page.write('  <body>\n    <h2><i>'+playlist_name+'</i></h2>\n    <ul>\n')
		for s in all_songs:
			item = '      <li>\n'
			item += '        <b>'+s.title+'</b> '
			item += '[<a href="'+s.google_link+'">Google Play</a>'
			item += ' | <a href="'+s.amazon_link+'">Amazon Music</a>]\n'
			item += '      </li>\n'
			page.write(item)
		page.write('    </ul>\n  </body>\n')
		page.write('</html>')
	return path.abspath(filepath)

class song:
	def __init__(self, id, title):
		self.youtube_id = id
		self.title = clean(title)
		self.google_link = googlify(self.title)
		self.amazon_link = amazonify(self.title)

def googlify(title):
	return 'https://play.google.com/store/search?q='+title+'&c=music&hl=en'

def amazonify(title):
	return 'https://music.amazon.com/search/'+title

def run(url):
	try:
		with open('api_key.txt', 'r') as key_store:
			DEVELOPER_KEY = key_store.read().strip()
	except FileNotFoundError:
		config()
		exit()
	youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)

	playlist_id = url.split('list=')[1]
	playlist = youtube.playlistItems().list(playlistId=playlist_id, maxResults=50, part='snippet').execute()
	playlist_name = youtube.playlists().list(id=playlist_id, part='snippet').execute()['items'][0]['snippet']['title']

	all_songs = []
	for vid in playlist.get('items', []):
		all_songs.append(song(vid['id'], vid['snippet']['title']))

	page = create_page(clean(playlist_name), all_songs)
	webbrowser.open('file://' + page)

def main():
	if len(argv) > 1:
		arg = argv[1]
		if arg == '--config':
			config()
		elif arg == '--help':
			help()
		else:
			run(arg)
	else:
		help()

if __name__ == '__main__':
	main()
