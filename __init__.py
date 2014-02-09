import bs4, datetime, flask, json, requests, urllib, time
from bs4 import BeautifulSoup
from datetime import date
from flask import Flask

app = Flask(__name__)

@app.route("/")

def Littoral():

	return '<!DOCTYPE html><html><head><title>Littoral</title></head><body><h1>Littoral</h1><p>Nothing to see here.</p></body></html>'


@app.route("/station/<id>")

def Station(id):

	y = str(date.today().year)
	m = str(date.today().month)
	d = str(date.today().day)
	tz = time.tzname[0]
		
	sock = urllib.urlopen('http://tides.gc.ca/eng/station?type=0&date='+y+'%2F'+m+'%2F'+d+'&sid='+id+'&tz='+tz+'&pres=2')
	source = sock.read()
	sock.close()
	
	soup = BeautifulSoup(source)
	header = soup.find('div',{'class':'stationTextHeader'}) # isolate the station header
	predictions = soup.find('div',{'class':'stationTextData'}) # isolate the station data table 
	predictions = predictions.text.split('\n') # create list based on newline characters
	predictions = filter(lambda l: l.strip(), predictions) # strip empty lines
	predictions = [item.lstrip() for item in predictions] # strip whitespace from beginning of lines
	predictions = [item.rstrip() for item in predictions] # strip whitespace from end of lines
	predictions = [item.split(';') for item in predictions] # split each line into components
	
	header = header.text.split('\n')
	header = header[1]
	header = header[12:]
	index = header.find('(')
	header = header[0:index-1]
	
	r = requests.get('http://geoportal-geoportail.gc.ca/ArcGIS/rest/services/tides-marees/allstations-toutestations/MapServer/find?searchText='+header+'&contains=true&searchFields=&sr=&layers=0&layerdefs=&returnGeometry=true&maxAllowableOffset=&f=json')
	
	station = r.json()
	
	station = station.get('results')[0]
	
	output = '<!DOCTYPE html><html><head><title>Littoral &middot; ' + station.get('value') + '</title></head><body>'
	
	output += '<h1>Littoral</h1><h2>' + station.get('value') + '</h2>'
	
	for index, item in enumerate(predictions):
		# make sure that we only show data points in the future
		if datetime.datetime.strptime(item[0]+' '+item[1], '%Y/%m/%d %I:%M %p') > datetime.datetime.now():
			try: # compare to the subsequent item to determine whether reading is for high or low tide
				next = predictions[index + 1]
				if item[2] > next[2]:
					status = 'High'
				else:
					status = 'Low'
			except IndexError: # if there is no subsequent item, compare to the previous item
				previous = predictions[index - 1]
				if item[2] > previous[2]:
					status = 'High'
				else:
					status = 'Low'
			output += '<p>' + status + ' at ' + item[1] + ' on ' + item[0] + ' (' + item[2] + 'm)</p>'
	
	output += '</body></html>'
	
	return output
		
if __name__ == '__main__':
    app.run()