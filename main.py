from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room
import json
import os
import math

print("Zaczynamy zabawe")

secret_key = os.urandom(16).hex()
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key 
socketio = SocketIO(app, cors_allowed_origins='*')

def normal_round(number):
    if number - math.floor(number) <0.5:
        return math.floor(number)
    else:
        return math.ceil(number)

##########SOCKET IO#######################
random_client_number = 0
random_room_number = 0

@socketio.on('joiningRoom')
def joining_room(roomName):
    print(roomName)
    join_room(roomName)

@socketio.on('messageFromClient')
def msg_from_client(data):
    emit('messageFromServer',data['message'], to=data["roomName"])


@socketio.on('joiningRandom')
def random_room_client():
    global random_client_number
    random_client_number+=1
    random_room_number = normal_round(random_client_number/2)
    join_room(random_room_number)
    emit('randomFromServer', random_room_number)


###############FLASK LOGIC##########
rooms = []
@app.get('/')
def home():
    return render_template('index.html')

@app.post('/addroom')
def add_room():
    room_name = request.form.get('roomName')
    rooms.append(room_name)
    url = "http://127.0.0.1:5000/" + room_name
    return redirect(url)

@app.get('/<room_name>')
def entering_room(room_name):
    if room_name in rooms:
        return render_template('privateroom.html', data = json.dumps(room_name))
    else:
        flash("Nie ma takiego pokoju!")
        return redirect(url_for('home'))
    
@app.post('/wanttojoin')
def asking_to_join():
    room_name = request.form.get('roomName')
    if room_name in rooms:
        url = "http://127.0.0.1:5000/" + room_name
        return redirect(url)
    else:
        flash("Nie ma takiego pokoju!")
        return redirect(url_for('home'))
@app.get('/randomroom')
def random_room():
    return render_template("randomroom.html")

if __name__ == '__main__':
    socketio.run(app)
