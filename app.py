import json

from flask import Flask
from flask import request
import requests

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
        response = requests.get(api_url+str(page*10), headers={'X-Api-Key': 'NurcILhyzDs3UAbN0EykdA==86JfdPcpA2ndS7dN'})
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

if __name__ == '__main__':
    app.run()
