import json

from flask import Flask
from flask import request
import requests
import googlemaps
import time
import geocoder
import random

app = Flask(__name__)

gym_access = True
proficiency = None
weight_goal = None
health_conditions = []
focus = None


@app.route('/')
def hello_world():  # put application's code here
    return "Hello world"


@app.route('/setgymaccess')
def setGym():  # put application's code here
    global gym_access
    results = request.args.get("access")
    if results == 'false':
        gym_access = False
    elif results == 'true':
        gym_access = True
    return ""
@app.route('/setfocus')
def setFocus():
    global focus
    results = request.args.get("proficiency")
    focus = results
    return ""

@app.route('/setproficiency')
def setProficiency(): #can be beginner, intermediate, or expert
    global proficiency
    results = request.args.get("proficiency")
    proficiency = results
    return ""


@app.route('/setweightgoal')
def setWeightGoal():
    global weight_goal
    results = request.args.get("weight_goal")
    weight_goal = results
    return ""

@app.route('/addHealthCondition')
def addHealthCondition():

    global health_conditions
    results = request.args.get("health_condition")
    health_conditions.append(results)
    return ""

@app.route('/recommend')
def recommend(): #pass in num_exercises as param
    #api_url = 'https://api.api-ninjas.com/v1/exercises?muscle={}'.format('biceps')
    api_url = 'https://api.api-ninjas.com/v1/exercises?'
    num_exercises = int(request.args.get("num_exercises"))

    if not gym_access:
        api_url+="equipment=body_only"
    if proficiency!=None:
        if api_url[-1]!='?':
            api_url+='&'
        api_url+="difficulty="+proficiency

    if api_url[-1]!='?':
        api_url+='&'
    api_url+="offset="

    exercises = []
    page = 0
    while len(exercises)<num_exercises:
        response = requests.get(api_url+str(page*10), headers={'X-Api-Key': 'NurcILhyzDs3UAbN0EykdA==86JfdPcpA2ndS7dN'}) # Angela's API Key
        page+=1
        if response.status_code == requests.codes.ok:
            js = json.loads(response.text)
            if not gym_access:
                for i in js:
                    if i['equipment']=='body_only':
                        exercises.append(i)
            else:
                exercises.extend(js)
        else:
            print("Error:", response.status_code, response.text)
    d = {"exercises": exercises[:min(len(exercises),num_exercises)]}
    return json.dumps(d)
@app.route('/findNearbyWorkouts')
def findNearbyWorkouts():
    '''Find nearby workouts to recommend based on live tracking information'''
    MAPS_API_KEY = "AIzaSyD-ld44eeW8LxC2PZfHa9m2p1cEfzaRleE"

    map_client = googlemaps.Client(MAPS_API_KEY)

    geo = geocoder.ip('me')
    lat = geo.latlng[0]
    lng = geo.latlng[1]
    location = lat, lng # get current location

    #randomize types of workout places to reccomend
    workout_types = ['gym', 'park', 'hike', 'yoga', 'dance', 'swim']
    if gym_access:
        search_workout = workout_types[random.randrange(0,len(workout_types))]
    else:
        search_workout = workout_types[random.randrange(1,len(workout_types))]

    distance = 8046.7 # 5 miles in meters
    workout_list = list()
    response = map_client.places_nearby(
        location=location,
        keyword=search_workout,
        radius=distance
    )

    workout_list.extend(response.get('results'))
    next_p = response.get('next_p')

    while next_p:
        time.sleep(2)
        response = map_client.places_nearby(
             location=location,
             keyword=search_workout,
             radius=distance
        )
        workout_list.extend(response.get('results'))
        next_p = response.get('next_p')
    workout_option_names = list()
    #print(workout_list)
    for w in workout_list:
        workout_option_names.append('NAME=' + w['name'] + ' | ' + 'RATING='+  w['rating'] + ' | ' + 'ADDRESS=' + w['vicinity'])

    workout_option_names.insert(0, search_workout)
    return workout_option_names


    #Information from maps:
    #business_status, geometry (lat/lng), icon, name, opening_hours, photos, vicinity (address), rating







if __name__ == '__main__':
    app.run()
