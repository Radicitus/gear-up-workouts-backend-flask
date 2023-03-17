import json
from pymongo import MongoClient

from flask import Flask
from flask import request
import requests

from datetime import date

app = Flask(__name__)

client = MongoClient('mongodb+srv://125group:QF6ATvGuz2raHmlF@cluster0.z7no1h6.mongodb.net/?retryWrites=true&w=majority')
db = client.userInfo
info = db.info

muscle_groups = ['abdominals','abductors','adductors','biceps','calves','chest','forearms','glutes','hamstrings',
                 'lats','lower_back','middle_back','neck','quadriceps','traps','triceps']

weight_loss = ['abdominals','cardio','biceps','cardio','chest','cardio','lower_back','cardio','quadriceps','cardio']

@app.route('/')
def hello_world():  # put application's code here
    return "Hello world"


@app.route('/setgoal/<username>/<goal>')
def setGoal(username,goal): #goal can be either strength or weightloss, default is strength
    info.update_one({"name": username},{"$set": {"goal": goal}})
    return ""


@app.route('/newuser/<username>')
def new_user(username):
    info.delete_one({"name": username})
    user = {
        "name": username,
        "gym_access": True,
        "proficiency": None,
        "previous_weights": dict(),
        "exercise_difficulty": dict(),
        "exercises_to_avoid": [],
        "workouts": dict(), #key is day and value is workouts
        "goal": "strength"
    }
    info.insert_one(user)
    return ""

@app.route('/recommendweight/<username>/<exercise>') #recommends workout weight based on past workouts and difficulty, must set history first
def recommend_exercise(username,exercise):
    data = info.find_one({"name": username})
    previous_weights = data['previous_weights']
    exercise_difficulty = data['exercise_difficulty']
    print(exercise_difficulty)
    if exercise not in previous_weights:
        return "Please set exercise history first" #must set past weight and reps and difficulty before algorithm can recommend
    if exercise_difficulty[exercise] == 'easy':
        new_weight = int(previous_weights[exercise] * 1.5)
        return str(new_weight)
    if exercise_difficulty[exercise]=='medium':
        new_weight = int(previous_weights[exercise] * 1.2)
        return str(new_weight)
    if exercise_difficulty[exercise]=='hard':
        new_weight = int(previous_weights[exercise] * 0.8)
        return str(new_weight)
    return ""

@app.route("/setweight/<username>/<exercise>/<weight>/<difficulty>") #sets workout weight and difficulty
def setWeight(exercise,username, weight,difficulty):
    current_vals = info.find_one({"name": username})
    previous_weights = current_vals['previous_weights']
    exercise_difficulty = current_vals['exercise_difficulty']
    previous_weights[exercise] = int(weight)
    exercise_difficulty[exercise] = difficulty

    info.update_one({"name": username}, {"$set": {"previous_weights": previous_weights, "exercise_difficulty": exercise_difficulty}})
    return ""

@app.route('/setgymaccess/<username>/<hasaccess>')
def setGym(username,hasaccess):  # sets whether or not the user has access to gyms, hasaccess is either true or false
    if hasaccess == 'false':
        info.update_one({"name": username}, {"$set": {"gym_access": False}})

    elif hasaccess == 'true':
        info.update_one({"name": username}, {"$set": {"gym_access": True}})
    return ""

@app.route('/setproficiency/<username>/<proficiency>')
def setProficiency(username, proficiency): #can be beginner, intermediate, or expert
    info.update_one({"name": username}, {"$set": {"proficiency": proficiency}})
    return ""


@app.route('/getworkouthistory/<username>')
def workoutHistory(username):
    data = info.find_one({"name": username})
    return json.dumps(data['workouts'])

@app.route('/setworkoutrating/<username>/<exercise>/<rating>') #rating is either 0 or 1, 0 being bad 1 being good
def setWorkoutRating(username,exercise,rating):
    data = info.find_one({"name": username})
    exercises_to_avoid=data['exercises_to_avoid']
    if rating=='0':
        exercises_to_avoid.append(exercise)

    exercises_to_avoid = list(set(exercises_to_avoid))

    info.update_one({"name": username}, {"$set": {"exercises_to_avoid": exercises_to_avoid}})

    return ""


@app.route('/recommend/<username>/<numexercises>')
def recommend(username, numexercises): #pass in num_exercises as param
    api_url = 'https://api.api-ninjas.com/v1/exercises?'
    data = info.find_one({"name": username})


    numexercises = int(numexercises)
    #if the user already has a workout for the day then return it
    today = date.today()
    workouts = data['workouts']

    if str(today) in workouts:
        return workouts[str(today)]


    gym_access = data['gym_access']
    proficiency = data['proficiency']
    exercises_to_avoid = data['exercises_to_avoid']
    goal = data['goal']

    if not gym_access:
        api_url+="equipment=body_only"
    if proficiency!=None:
        if api_url[-1]!='?':
            api_url+='&'
        api_url+="difficulty="+proficiency

    if api_url[-1]!='?':
        api_url+='&'
    #set muscle group based on day
    day = int(str(date.today())[5:7])
    if goal=='strength':
        muscle = muscle_groups[day%len(muscle_groups)]
        api_url+="muscle="+muscle+"&"
    else:
        workout = weight_loss[day%len(weight_loss)]
        if workout=='cardio':
            api_url+="type=cardio&"
        else:
            api_url += "muscle=" + workout + "&"
    api_url+="offset="

    exercises = []
    page = 0
    while len(exercises)<numexercises:
        response = requests.get(api_url+str(page*10), headers={'X-Api-Key': 'NurcILhyzDs3UAbN0EykdA==86JfdPcpA2ndS7dN'})
        page+=1
        if response.status_code == requests.codes.ok:
            js = json.loads(response.text)
            if len(js)==0:
                break
            if not gym_access:
                for i in js:
                    if i['equipment']=='body_only':
                        if "".join(i['name'].split()) not in exercises_to_avoid:
                            exercises.append(i)
            else:
                for i in js:
                    print("".join(i['name'].split()))
                    if "".join(i['name'].split()) not in exercises_to_avoid:
                        exercises.append(i)
        else:
            print("Error:", response.status_code, response.text)
    d = {"exercises": exercises[:min(len(exercises),numexercises)]}
    temp = json.dumps(d)
    workouts[str(today)] = temp
    info.update_one({"name": username}, {"$set": {"workouts": workouts}})
    return temp

if __name__ == '__main__':
    app.run()
