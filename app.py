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
#
# from pymongo import MongoClient
# import certifi


app = Flask(__name__)

gym_access = True
proficiency = None
weight_goal = None
health_conditions = []
focus = None

# client = MongoClient(
#     'mongodb+srv://125group:QF6ATvGuz2raHmlF@cluster0.z7no1h6.mongodb.net/?retryWrites=true&w=majority',
#     tlsCAFile=certifi.where())
# db = client.userInfo
# info = db.info

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

# @app.route('/randomTimeAlternativeWorkout')
# def randomTimeAlternativeWorkout():
#     global randomTime
#     curr_hour = datetime.datetime.now().hour
#     curr_minute = datetime.datetime.now().minute
#
#     curr_hour = 14
#     curr_minute = 50
#
#     # if time is past 9 pm, return null_output
#     if (curr_hour >= 19):
#         randomTime = -1
#         return ""
#
#     # reset from military time and get PM or AM
#     isPM = False
#     if (curr_hour > 12):
#         curr_hour = curr_hour-12
#         isPM = True
#
#     p = random.random()
#     start = str(datetime.date.today().strftime("%m/%d/%Y")) + f" {curr_hour}:{curr_minute} "
#     if (isPM):
#         start += "PM"
#     else:
#         start += "AM"
#
#     end = str(datetime.date.today().strftime("%m/%d/%Y")) + " 7:00 PM"
#     time_format = '%m/%d/%Y %I:%M %p'
#
#     start_time = time.mktime(time.strptime(start, time_format))
#     end_time = time.mktime(time.strptime(end, time_format))
#
#     ptime = start_time + p * (end_time - start_time)
#
#     randomTime = time.strftime(time_format, time.localtime(ptime))
#     return ""
# @app.route('/findNearbyAlternativeWorkouts')
# def findNearbyAlternativeWorkouts():
#     '''Find nearby workouts to recommend based on live tracking information'''
#     randomTimeAlternativeWorkout()
#     global randomTime
#
#     # if time is past 9 PM, do not suggest workouts
#     if (randomTime == -1):
#         none_output = {"LiveWorkouts": [
#             {
#                 "workout_type": None,
#                 "name": None,
#                 "address": None,
#                 "rating": None,
#                 "maps_link": None,
#                 "time": None
#             },
#             {
#                 "workout_type": None,
#                 "name": None,
#                 "address": None,
#                 "rating": None,
#                 "maps_link": None,
#                 "time": None
#             },
#             {
#                 "workout_type": None,
#                 "name": None,
#                 "address": None,
#                 "rating": None,
#                 "maps_link": None,
#                 "time": None
#             }
#         ]}
#         return none_output
#
#     # Map client
#     MAPS_API_KEY = "AIzaSyD-ld44eeW8LxC2PZfHa9m2p1cEfzaRleE"
#     map_client = googlemaps.Client(MAPS_API_KEY)
#
#     # Get current location (longitude and latitude)
#     geo = geocoder.ip('me')
#     curr_lat = geo.latlng[0]
#     curr_lng = geo.latlng[1]
#     curr_location = curr_lat, curr_lng
#
#     # Get random alternative workout
#     workout_types = ['hiking', 'yoga', 'dancing', 'swimming', 'rock climbing', 'boxing', 'martial arts']
#     workout_type = workout_types[random.randrange(0,len(workout_types))]
#
#     distance = 8046.7 # 5 miles in meters
#     workout_list = list()
#     response = map_client.places_nearby(
#         location=curr_location,
#         keyword=workout_type,
#         radius=distance
#     )
#
#     workout_list.extend(response.get('results'))
#     next_p = response.get('next_p')
#
#     # Find nearby places according to workout type
#     while next_p:
#         time.sleep(2)
#         response = map_client.places_nearby(
#              location=curr_location,
#              keyword=workout_type,
#              radius=distance
#         )
#         workout_list.extend(response.get('results'))
#         next_p = response.get('next_p')
#
#
#     # Get alternative workout recommendation options and their attributes
#     workout_recommendation = dict()
#     #print(workout_list)
#     curr_time = datetime.datetime.now()
#     for w in workout_list:
#         if len(workout_recommendation) >= 3:
#             break
#
#         end = 'https://www.google.com/maps/dir/?api=1&'
#         dest_lat_lng = str(w['geometry']['location']['lat']) + "," + str(w['geometry']['location']['lng'])
#         str_curr_location = str(curr_location[0]) + "," + str(curr_location[1])
#         directions_request = f"origin={str_curr_location}&destination={dest_lat_lng}&key={MAPS_API_KEY}"
#         maps_link = end + directions_request
#         workout_recommendation[w['name']] = {'rating': w['rating'], 'address': w['vicinity'], 'directions': maps_link}
#
#     # Get list of destination names
#     t = []
#     for key in workout_recommendation.keys():
#         t.append(key)
#     name1 = t[len(t)-3]
#     name2 = t[len(t)-2]
#     name3 = t[len(t)-1]
#     output = {"LiveWorkouts": [
#         {
#             "workout_type": workout_type,
#             "name": name1,
#             "address": workout_recommendation[name1]['address'],
#             "rating": workout_recommendation[name1]['rating'],
#             "maps_link": workout_recommendation[name1]['directions'],
#             "time" : randomTime
#         },
#         {
#             "workout_type": workout_type,
#             "name": name2,
#             "address": workout_recommendation[name2]['address'],
#             "rating": workout_recommendation[name2]['rating'],
#             "maps_link": workout_recommendation[name2]['directions'],
#             "time": randomTime
#         },
#         {
#             "workout_type": workout_type,
#             "name": name3,
#             "address": workout_recommendation[name3]['address'],
#             "rating": workout_recommendation[name3]['rating'],
#             "maps_link": workout_recommendation[name3]['directions'],
#             "time": randomTime
#         }
#     ]}
#
#     return json.dumps(output)




@app.route('/api/randomTimeAlternativeWorkout/')
def randomTimeAlternativeWorkout():
    global randomTime
    # data = info.find_one({"name": username})

    curr_hour = datetime.datetime.now().hour
    curr_minute = datetime.datetime.now().minute

    curr_hour = 18
    curr_minute = 50

    # if time is past 7 pm, return null_output
    if (curr_hour >= 19):
        randomTime = -1
        #info.update_one({"name": username}, {"$set": {"randomTime": randomTime}})
        return ""

    # reset from military time and get PM or AM
    isPM = False
    if (curr_hour > 12):
        curr_hour = curr_hour-12
        isPM = True

    p = random.random()
    start = str(datetime.date.today().strftime("%m/%d/%Y")) + f" {curr_hour}:{curr_minute} "
    if (isPM):
        start += "PM"
    else:
        start += "AM"

    end = str(datetime.date.today().strftime("%m/%d/%Y")) + " 7:00 PM"
    time_format = '%m/%d/%Y %I:%M %p'

    start_time = time.mktime(time.strptime(start, time_format))
    end_time = time.mktime(time.strptime(end, time_format))

    ptime = start_time + p * (end_time - start_time)

    randomTime = time.strftime(time_format, time.localtime(ptime))

    # info.update_one({"name": username}, {"$set": {"randomTime": randomTime}})

    return ""
@app.route('/api/findNearbyAlternativeWorkouts')
def findNearbyAlternativeWorkouts():#username):
    '''Find nearby workouts to recommend based on live tracking information'''
    # data = info.find_one({"name": username})
    randomTimeAlternativeWorkout()
    # randomTime = data['randomTime']
    global randomTime

    # if time is past 9 PM, do not suggest workouts
    if (randomTime == -1):
        none_output = {"LiveWorkouts": [
            {
                "workout_type": None,
                "name": None,
                "address": None,
                "rating": None,
                "maps_link": None,
                "time": None
            },
            {
                "workout_type": None,
                "name": None,
                "address": None,
                "rating": None,
                "maps_link": None,
                "time": None
            },
            {
                "workout_type": None,
                "name": None,
                "address": None,
                "rating": None,
                "maps_link": None,
                "time": None
            }
        ]}

        # info.update_one({"name": username}, {
        #
        # })
        return none_output

    # Map client
    MAPS_API_KEY = "AIzaSyD-ld44eeW8LxC2PZfHa9m2p1cEfzaRleE"
    map_client = googlemaps.Client(MAPS_API_KEY)

    # Get current location (longitude and latitude)
    geo = geocoder.ip('me')
    curr_lat = geo.latlng[0]
    curr_lng = geo.latlng[1]
    curr_location = curr_lat, curr_lng

    # Get random alternative workout
    workout_types = ['hiking', 'yoga', 'dancing', 'swimming', 'rock climbing', 'boxing', 'martial arts']
    workout_type = workout_types[random.randrange(0,len(workout_types))]

    distance = 8046.7 # 5 miles in meters
    workout_list = list()
    response = map_client.places_nearby(
        location=curr_location,
        keyword=workout_type,
        radius=distance
    )

    workout_list.extend(response.get('results'))
    next_p = response.get('next_p')

    # Find nearby places according to workout type
    while next_p:
        time.sleep(2)
        response = map_client.places_nearby(
             location=curr_location,
             keyword=workout_type,
             radius=distance
        )
        workout_list.extend(response.get('results'))
        next_p = response.get('next_p')


    # Get alternative workout recommendation options and their attributes
    workout_recommendation = dict()
    #print(workout_list)
    curr_time = datetime.datetime.now()
    for w in workout_list:
        if len(workout_recommendation) >= 3:
            break

        end = 'https://www.google.com/maps/dir/?api=1&'
        dest_lat_lng = str(w['geometry']['location']['lat']) + "," + str(w['geometry']['location']['lng'])
        str_curr_location = str(curr_location[0]) + "," + str(curr_location[1])
        directions_request = f"origin={str_curr_location}&destination={dest_lat_lng}&key={MAPS_API_KEY}"
        maps_link = end + directions_request
        workout_recommendation[w['name']] = {'rating': w['rating'], 'address': w['vicinity'], 'directions': maps_link}

    # Get list of destination names
    t = []
    for key in workout_recommendation.keys():
        t.append(key)
    name1 = t[len(t)-3]
    name2 = t[len(t)-2]
    name3 = t[len(t)-1]
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

    # info.update_one({"name": username}, {
    #     "$set": {"workout_type": }
    # })
    return json.dumps(output)

if __name__ == '__main__':
    app.run()

