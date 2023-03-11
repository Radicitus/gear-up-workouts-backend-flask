import json

from flask import Flask
from flask import request
import requests

app = Flask(__name__)

gym_access = True
proficiency = None

previous_weights = dict() #key is exercise name
exercise_difficulty = dict() #difficulty can be easy medium or hard

exercises_to_avoid = set()

@app.route('/')
def hello_world():  # put application's code here
    return "Hello world"



@app.route('/recommend/<exercise>') #recommends workout weight based on past workouts and difficulty, must set history first
def recommend_exercise(exercise):
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

@app.route("/setweight/<exercise>/<weight>/<difficulty>") #sets workout weight and difficulty
def setWeight(exercise,weight,difficulty):
    previous_weights[exercise] = int(weight)
    exercise_difficulty[exercise] = difficulty
    return ""

@app.route('/setgymaccess')
def setGym():  # sets whether or not the user has access to gyms
    global gym_access
    results = request.args.get("access")
    if results == 'false':
        gym_access = False
    elif results == 'true':
        gym_access = True
    return ""

@app.route('/setproficiency')
def setProficiency(): #can be beginner, intermediate, or expert
    global proficiency
    results = request.args.get("proficiency")
    proficiency = results
    return ""


@app.route('/setworkoutrating/<exercise>/<rating>') #rating is either 0 or 1, 0 being bad 1 being good
def setWorkoutRating(exercise,rating):
    if rating=='0':
        exercises_to_avoid.add(exercise)
    print(exercises_to_avoid)
    return ""


@app.route('/recommend')
def recommend(): #pass in num_exercises as param
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
    d = {"exercises": exercises[:min(len(exercises),num_exercises)]}
    return json.dumps(d)

if __name__ == '__main__':
    app.run()
