from flask import Flask
import requests

app = Flask(__name__)

workoutAPIKey = '9BqMCmqH+81LMd1zjFXhxw==ocVIvWHb5irurBrY'
workoutAPIUrlBase = 'https://api.api-ninjas.com/v1/exercises?'
cardioURLBase = 'type=cardio'
strengthURLBase = 'type=strength'
difficultyURLBase = 'difficulty='


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/cardio')
def getCardioWorkout():
    response = requests.get(workoutAPIUrlBase + cardioURLBase, headers={'X-Api-Key': workoutAPIKey})
    if response.status_code == requests.codes.ok:
        print(response.text)
        return response.text
    else:
        print("Error:", response.status_code, response.text)


@app.route('/strength')
@app.route('/strength/<difficulty>')
def getStrengthWorkout(difficulty='beginner'):
    difficultyURL = '&' + difficultyURLBase + difficulty
    response = requests.get(workoutAPIUrlBase + strengthURLBase + difficultyURL, headers={'X-Api-Key': workoutAPIKey})
    if response.status_code == requests.codes.ok:
        print(response.text)
        return response.text
    else:
        print("Error:", response.status_code, response.text)


if __name__ == '__main__':
    app.run()
