import bs4, datetime, flask, json, requests, time
from bs4 import BeautifulSoup
from datetime import date
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")

def Index():
	return render_template('index.html')

@app.route("/station/<id>/<tz>/")

def Station(id, tz):

	y = str(date.today().year)
	m = str(date.today().month)
	d = str(date.today().day)

	r = requests.get('http://tides.gc.ca/eng/station?type=0&date='+y+'%2F'+m+'%2F'+d+'&sid='+id+'&tz='+tz+'&pres=2')
	
	soup = BeautifulSoup(r.text)
	predictions = soup.find('div',{'class':'stationTextData'}) # isolate the station data table
	if predictions != None:
		predictions = predictions.text.split('\n') # create list based on newline characters
		predictions = filter(lambda l: l.strip(), predictions) # strip empty lines
		predictions = [item.lstrip() for item in predictions] # strip whitespace from beginning of lines
		predictions = [item.rstrip() for item in predictions] # strip whitespace from end of lines
		predictions = [item.split(';') for item in predictions] # split each line into components
		
		data = []
		
		for index, item in enumerate(predictions):
			# make sure that we only show data points in the future
			if datetime.datetime.strptime(item[0]+' '+item[1], '%Y/%m/%d %H:%M:%S') > datetime.datetime.now():
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
				height = item[2].replace('(m)', 'm')
				data.append(status + ' at ' + item[1] + ' ' + tz + ' on ' + item[0] + ' (' + height + ')')
	else:
		data = ['No data found.']

	header = soup.find('div',{'class':'stationTextHeader'}) # isolate the station header
	if header != None:
		header = header.text.split('\n')
		header = header[1]
		header = header[12:]
		index = header.find('(')
		header = header[0:index-1]
	
		r = requests.get('http://geoportal-geoportail.gc.ca/arcgis/rest/services/tides_marees/allstations_toutestations/MapServer/0/query?text='+header+'&f=json')
		
		station = r.json()
		
		station = station.get('features')[0]
		station = station.get('attributes')
		station_name = station.get('STATION_NAME')
	else:
		station_name = 'Station Unavailable'
	
	return render_template('station.html', station=station_name, data=data)
	
@app.route("/colophon")

def Colophon():
	return render_template('colophon.html')
		
if __name__ == '__main__':
    app.run()