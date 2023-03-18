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

muscle_groups = [['abdominals','lower_back','middle_back','chest'],
                 ['biceps','forearms','triceps','traps'],
                 ['calves','glutes','hamstrings','quadriceps']]


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
        "gym_access": None,
        "proficiency": None,
        "previous_weights": dict(),
        "previous_reps": dict(),
        "exercise_difficulty": dict(),
        "workouts": dict(), #key is day and value is workouts
        "exercise_scores": dict(),
        "goal": "strength",
        "total_weight": 0,
        "onboarded": False
    }
    info.insert_one(user)
    return ""

@app.route('/gettotalweight/<username>')
def getTotalWeight(username):
    data = info.find_one({"name": username})
    return str(data['total_weight'])


@app.route('/hasonboarded/<username>')
def hasOnboarded(username):
    data = info.find_one({"name": username})
    return str(data['onboarded'])

@app.route("/rateexercise/<username>/<exercise>/<difficulty>") #sets workout weight and difficulty
def rateExercise(exercise,username,difficulty):
    current_vals = info.find_one({"name": username})
    exercise_difficulty = current_vals['exercise_difficulty']
    exercise_difficulty[exercise] = difficulty

    info.update_one({"name": username}, {"$set": {"exercise_difficulty": exercise_difficulty}})
    return ""

@app.route('/setgymaccess/<username>/<hasaccess>')
def setGym(username,hasaccess):  # sets whether or not the user has access to gyms, hasaccess is either true or false
    if hasaccess == 'false':
        info.update_one({"name": username}, {"$set": {"gym_access": False, "onboarded": True}})

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
    exercise_ratings=data['exercise_scores']
    if exercise not in exercise_ratings:
        exercise_ratings[exercise] = 1
    if rating=='0':
        exercise_ratings[exercise] = 0.8*exercise_ratings[exercise]
    else:
        exercise_ratings[exercise] = 1.2*exercise_ratings[exercise]

    info.update_one({"name": username}, {"$set": {"exercise_scores": exercise_ratings}})

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
    exercise_scores = data['exercise_scores']
    goal = data['goal']
    previous_weights=data['previous_weights']
    previous_reps=data['previous_reps']
    exercise_difficulty = data['exercise_difficulty']
    total_weight = data['total_weight']

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
    exercises = []
    if goal=='strength':
        muscle_group = muscle_groups[day%len(muscle_groups)]
        # api_url+="muscle="+muscle+"&"
        # api_url += "offset="
        # page = 0
        exercise_categories = []
        for i in range(4):
            muscle = muscle_group[i]

            page = 0
            e = []
            while len(e) < numexercises * 3:
                temp_url=api_url+"muscle="+muscle+"&offset="+str(page*10)
                response = requests.get(temp_url,
                                        headers={'X-Api-Key': 'NurcILhyzDs3UAbN0EykdA==86JfdPcpA2ndS7dN'})
                page += 1
                if response.status_code == requests.codes.ok:
                    js = json.loads(response.text)
                    if len(js) == 0:
                        break
                    e.extend(js)
                else:
                    print("Error:", response.status_code, response.text)
            exercise_categories.append(e)
        i = 0
        while len(exercises)<numexercises*10:
            if len(exercise_categories[i])==0:
                continue
            exercises.append(exercise_categories[i][0])
            exercise_categories[i].pop(0)
            i+=1
            i%=4

    else:
        workout = weight_loss[day%len(weight_loss)]
        if workout=='cardio':
            api_url+="type=cardio&"
        else:
            api_url += "muscle=" + workout + "&"
        api_url+="offset="
        page = 0
        while len(exercises)<numexercises*10:
            response = requests.get(api_url + str(page * 10),
                                headers={'X-Api-Key': 'NurcILhyzDs3UAbN0EykdA==86JfdPcpA2ndS7dN'})
            page += 1
            if response.status_code == requests.codes.ok:
                js = json.loads(response.text)
                if len(js) == 0:
                    break
                exercises.extend(js)
            else:
                print("Error:", response.status_code, response.text)
    scores = dict()
    name_to_muscle = dict()
    for exercise in exercises:
        score = 1
        if not gym_access:
            if exercise['equipment']=='body_only':
                score*=1.2
            else:
                score*=0.8
        if "".join(exercise['name'].split(" ")) in exercise_scores:
            score*=exercise_scores["".join(exercise['name'].split(" "))]
        else:
            score*=1.2
        scores[exercise['name']] = score
        name_to_muscle[exercise['name']] = exercise['muscle']
    final_exercises = []
    for exercise, score in sorted(scores.items(), key=lambda x: x[1],reverse=True):
        ex = dict()
        if len(final_exercises)<numexercises:
            ex['name'] = exercise
            ex['muscle'] = name_to_muscle[exercise]
            remove_spaces = "".join(exercise.split(" "))
            if remove_spaces in previous_weights:
                weight = previous_weights[remove_spaces]
                reps = previous_reps[remove_spaces]
                if remove_spaces in exercise_difficulty:
                    if exercise_difficulty[remove_spaces]=='easy':
                        ex['weight'] = int(weight*1.2)
                        previous_weights[remove_spaces] = int(weight*1.2)
                        total_weight+=int(weight*1.2)
                        ex['reps'] = int(reps*1.2)
                        previous_reps[remove_spaces] = int(reps*1.2)
                    elif exercise_difficulty[remove_spaces]=='medium':
                        ex['weight'] = int(weight*1.2)
                        total_weight+=int(weight*1.2)
                        previous_weights[remove_spaces] = int(weight*1.2)
                    else:
                        ex['weight'] = int(weight*0.8)
                        total_weight+=int(weight*0.8)
                        previous_weights[remove_spaces] = int(weight*0.8)
                        ex['reps'] = int(reps*0.8)
                        previous_reps[remove_spaces] = int(reps*0.8)
                else:
                    ex['weight'] = int(weight*1.2)
                    total_weight+=int(weight*1.2)
                    ex['reps'] = int(reps)
                    previous_weights[remove_spaces] = int(weight*1.2)
            else:
                #recommend weight of 10lb
                previous_weights[remove_spaces] = 10
                ex['weight'] = 10
                total_weight+=10
                previous_reps[remove_spaces] = 15
                ex['reps'] = 15
            final_exercises.append(ex)
        else:
            break


    d = {"exercises": final_exercises[:min(len(final_exercises),numexercises)]}
    temp = json.dumps(d)
    workouts[str(today)] = temp
    info.update_one({"name": username}, {"$set": {"workouts": workouts,"previous_weights": previous_weights,'previous_reps': previous_reps,"total_weight":total_weight}})
    return temp

if __name__ == '__main__':
    app.run()
