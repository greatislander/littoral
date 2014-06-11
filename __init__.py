import bs4, datetime, flask, json, requests, time, math, yaml, os
from bs4 import BeautifulSoup
from datetime import date
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

def distance_on_unit_sphere(lat1, long1, lat2, long2):

	# Convert latitude and longitude to
	# spherical coordinates in radians.
	degrees_to_radians = math.pi/180.0
	
	# phi = 90 - latitude
	phi1 = (90.0 - lat1)*degrees_to_radians
	phi2 = (90.0 - lat2)*degrees_to_radians
	
	# theta = longitude
	theta1 = long1*degrees_to_radians
	theta2 = long2*degrees_to_radians
	
	# Compute spherical distance from spherical coordinates.
	
	# For two locations in spherical coordinates
	# (1, theta, phi) and (1, theta, phi)
	# cosine( arc length ) =
	#	sin phi sin phi' cos(theta-theta') + cos phi cos phi'
	# distance = rho * arc length
	
	cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
	arc = math.acos( cos )
	
	# Remember to multiply arc by the radius of the earth
	# in your favorite set of units to get length.
	return arc


@app.route("/", methods=['GET', 'POST'])

def Index():

	if request.method == 'POST':
		lat1 = float(request.form['latitude'])
		long1 = float(request.form['longitude'])
		root = os.path.dirname(os.path.abspath(__file__))
		src = os.path.join(root, 'static/stations.yaml')
		f = open(src)
		stations = yaml.load(f.read())
	
		comps = {}
	
		for k, v in stations.iteritems():
			lat2 = v['latitude']
			long2 = v['longitude']
			comps[k] = distance_on_unit_sphere(lat1, long1, lat2, long2)
	
		id = str(min(comps, key = comps.get))
		return redirect("/station/"+id)
	else:
		return render_template('index.html', locate='true', pageclass='index')

@app.route("/station/<id>")

def Station(id):

	y = str(date.today().year)
	m = str(date.today().month)
	d = str(date.today().day)

	r = requests.get('http://tides.gc.ca/eng/station?type=0&date='+y+'%2F'+m+'%2F'+d+'&sid='+id+'&pres=2')
	
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
				data.append(status + ' at ' + item[1] + ' on ' + item[0] + ' (' + height + ')')
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
	
	return render_template('station.html', station=station_name, data=data, pageclass='station')
	
@app.route("/colophon")

def Colophon():
	return render_template('colophon.html', pageclass='colophon')
		
if __name__ == '__main__':
    app.run()