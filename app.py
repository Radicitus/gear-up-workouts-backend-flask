import json

from flask import Flask
from flask import request
import requests
import googlemaps
import time
import geocoder
import random
import datetime
import itertools
from collections import Counter


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

@app.route('/randomTimeAlternativeWorkout')
def randomTimeAlternativeWorkout():
    prop = random.random()
    start = str(datetime.date.today().strftime("%m/%d/%Y")) + " 9:00 AM"
    end = str(datetime.date.today().strftime("%m/%d/%Y")) + " 9:00 PM"
    time_format = '%m/%d/%Y %I:%M %p'

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    global randomTime
    randomTime = time.strftime(time_format, time.localtime(ptime))
    return ""
@app.route('/findNearbyAlternativeWorkouts')
def findNearbyAlternativeWorkouts():
    '''Find nearby workouts to recommend based on live tracking information'''
    MAPS_API_KEY = "AIzaSyD-ld44eeW8LxC2PZfHa9m2p1cEfzaRleE"

    map_client = googlemaps.Client(MAPS_API_KEY)

    geo = geocoder.ip('me')
    curr_lat = geo.latlng[0]
    curr_lng = geo.latlng[1]
    curr_location = curr_lat, curr_lng # get current location

    #randomize types of workout places to recommend
    workout_types = ['gym', 'hiking', 'yoga', 'dancing', 'swimming', 'rock climbing', 'boxing', 'martial arts']
    if gym_access:
        workout_type = workout_types[random.randrange(0,len(workout_types))]
    else:
        workout_type = workout_types[random.randrange(1,len(workout_types))]

    distance = 8046.7 # 5 miles in meters
    workout_list = list()
    response = map_client.places_nearby(
        location=curr_location,
        keyword=workout_type,
        radius=distance
    )

    workout_list.extend(response.get('results'))
    next_p = response.get('next_p')

    while next_p:
        time.sleep(2)
        response = map_client.places_nearby(
             location=curr_location,
             keyword=workout_type,
             radius=distance
        )
        workout_list.extend(response.get('results'))
        next_p = response.get('next_p')


    workout_recommendation = dict()
    print(workout_list)
    # get workout recommendation and its attributes
    curr_time = datetime.datetime.now()
    for w in workout_list:
        if len(workout_recommendation) >= 3:
            break

        end = 'https://www.google.com/maps/dir/?api=1&'
        dest_lat_lng = str(w['geometry']['location']['lat']) + "," + str(w['geometry']['location']['lng'])
        str_curr_location = str(curr_location[0]) + "," + str(curr_location[1])
        directions_request = f"origin={str_curr_location}&destination={dest_lat_lng}&key={MAPS_API_KEY}"
        maps_link = end + directions_request

        #if w['opening_hours']['open_now'] == True:
        workout_recommendation[w['name']] = {'rating': w['rating'], 'address': w['vicinity'], 'directions': maps_link} #, 'maps_link': w['photos'][0]['html_attributions'][0].split("\"")[1]}







    # returns a list where the first index is the type of workout
    # and the second is a dictionary keyed by the name and val
    # is another dictionary containing the address and rating
    randomTimeAlternativeWorkout()
    global randomTime
    #return [workout_type, randomTime, workout_recommendation]
    t = []
    for key in workout_recommendation.keys():
        t.append(key)
    name1 = t[0]
    name2 = t[1]
    name3 = t[2]
    output = {"LiveWorkouts": [
        {
            "workout_type": workout_type,
            "name": name1,
            "address": workout_recommendation[name1]['address'],
            "rating": workout_recommendation[name1]['rating'],
            "maps_link": workout_recommendation[name1]['directions'],
            "time" : randomTime
        },
        {
            "workout_type": workout_type,
            "name": name2,
            "address": workout_recommendation[name2]['address'],
            "rating": workout_recommendation[name2]['rating'],
            "maps_link": workout_recommendation[name2]['directions'],
            "time": randomTime
        },
        {
            "workout_type": workout_type,
            "name": name3,
            "address": workout_recommendation[name3]['address'],
            "rating": workout_recommendation[name3]['rating'],
            "maps_link": workout_recommendation[name3]['directions'],
            "time": randomTime
        }
    ]}

    print(output)
    return json.dumps(output)

    #Information from maps:
    #business_status, geometry (lat/lng), icon, name, opening_hours, photos, vicinity (address), rating



# @app.route('/randomTimeAlternativeWorkout')
# def timeRecommendAlternativeWorkout():
# api route to generate custom workout for the day


# google maps embed link
# postman to get format of json







if __name__ == '__main__':
    app.run()

