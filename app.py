from flask import Flask
import requests

app = Flask(__name__)

workoutAPIKey = '9BqMCmqH+81LMd1zjFXhxw==ocVIvWHb5irurBrY'
workoutAPIUrlBase = 'https://api.api-ninjas.com/v1/exercises?'
cardioURLBase = 'type=cardio'
strengthURLBase = 'type=strength'
stretchingURLBase = 'type=stretching'
difficultyURLBase = 'difficulty='


@app.route('/')
def hello_world():
    return 'Hello World!'


### CARDIO
@app.route('/cardio')
@app.route('/cardio/<difficulty>')
def getCardioWorkout(difficulty=''):
    difficultyURL = '&' + difficultyURLBase + difficulty
    response = requests.get(workoutAPIUrlBase + cardioURLBase + difficultyURL, headers={'X-Api-Key': workoutAPIKey})
    if response.status_code == requests.codes.ok:
        return response.text
    else:
        print("Error:", response.status_code, response.text)


### STRENGTH
@app.route('/strength')
@app.route('/strength/<difficulty>')
def getStrengthWorkout(difficulty=''):
    difficultyURL = '&' + difficultyURLBase + difficulty
    response = requests.get(workoutAPIUrlBase + strengthURLBase + difficultyURL, headers={'X-Api-Key': workoutAPIKey})
    if response.status_code == requests.codes.ok:
        return response.text
    else:
        print("Error:", response.status_code, response.text)


### STRETCHING
@app.route('/stretching')
@app.route('/stretching/<difficulty>')
def getStretchingWorkout(difficulty=''):
    difficultyURL = '&' + difficultyURLBase + difficulty
    response = requests.get(workoutAPIUrlBase + stretchingURLBase + difficultyURL, headers={'X-Api-Key': workoutAPIKey})
    if response.status_code == requests.codes.ok:
        return response.text
    else:
        print("Error:", response.status_code, response.text)


if __name__ == '__main__':
    app.run()
