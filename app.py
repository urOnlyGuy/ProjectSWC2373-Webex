from flask import Flask, render_template, request, redirect, url_for 
import requests , json
 
app = Flask(__name__) 
 
WEBEX_API_BASE = 'https://webexapis.com/v1' 
 
#function to get user info
def get_user_info(access_token): 
    headers = { 
        'Authorization': f'Bearer {access_token}' 
    } 
    response = requests.get(f'{WEBEX_API_BASE}/people/me', headers=headers) 
    if response.status_code == 200: 
        return response.json()  # User information 
    else: 
        return None

#function to get room
def get_rooms(access_token): 
    headers = { 
        'Authorization': f'Bearer {access_token}' 
    } 
    response = requests.get(f'{WEBEX_API_BASE}/rooms', headers=headers) 
    if response.status_code == 200: 
        return response.json().get('items', [])  # List of rooms 
    else: 
        return None
    
#function to CREATE ROOM
def create_roomAPI(access_token):
    room_name=request.form['create_room']
    headers = { 
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    params = {"title": room_name}
    response = requests.post(f'{WEBEX_API_BASE}/rooms', headers=headers, json=params)
    print(response.status_code)
    if response.status_code == 200: 
        print("Submitted!")
        print("Response: ", response.json()) 
    elif response.status_code == 201:
        print("Room created successfully!")
        print("Response: ", response.json())
    else:
        print('Create room failed.')

#function to check webex connnection 
def test_connection(access_token):
        headers = {
        'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(f'{WEBEX_API_BASE}/meetings', headers=headers)

        if response.status_code == 200:
            print({"status": "Connection Successful", "data": response.json()})
            return response.status_code
        else:
            print({"status": "Connection Failed", "error": response.text}), response.status_code
            return response.status_code


#first app route
@app.route('/', methods=['GET', 'POST']) 
def index(): 
    if request.method == 'POST': 
        access_token = request.form.get('access_token')
        if len(access_token) > 5: 
            print ("Logged in! Ur access token: ", access_token)
            return redirect(url_for('home', access_token=access_token))
        else: 
            return "Invalid access token. Please try again.", 400 

    return render_template('index.html')

#test page
@app.route('/test/<access_token>', methods=['GET'])
def test(access_token):
    response=test_connection(access_token)
    return render_template('test_connection.html', response=response, access_token=access_token)
    
#home page
@app.route('/home/<access_token>', methods=['GET', 'POST']) 
def home(access_token): 
    user_info = get_user_info(access_token)
    return render_template('home.html', access_token=access_token, user_info=user_info)
 

#app route to ROOMS LIST
@app.route('/rooms/<access_token>', methods=['GET']) 
def rooms(access_token): 
    rooms = get_rooms(access_token) 
    if rooms is not None: 
        return render_template('rooms.html', rooms=rooms, access_token=access_token) 
    else: 
        return "Failed to retrieve rooms.", 400 
    

#app route to USER INFO
@app.route('/user/<access_token>', methods=['GET']) 
def user(access_token): 
    user_info = get_user_info(access_token) 
    if user_info: 
            return render_template('real_user_info.html', user_info=user_info, 
access_token=access_token) 
    else: 
        return "Failed to retrieve user info", 400

#route to CREATE ROOM
@app.route('/create-a-room/<access_token>', methods=['GET','POST'])
def create_room(access_token):
    print (access_token)
    if request.method == 'POST':
        create_roomAPI(access_token)
    return render_template('create_room.html', access_token=access_token)

#route for messaging STEP 1
@app.route('/message-room-list/<access_token>', methods=['GET','POST'])
def message_room_list(access_token):
    rooms = get_rooms(access_token)

    #Action when user submit message form
    if request.method == 'POST': 
        headers = { 
        'Authorization': f'Bearer {access_token}' 
    } 
        # If the user submits a message form, send a message to the selected room 
        room_id = request.form['room_id'] 
        message = request.form['message'] 
         
        message_data = { 
            'roomId': room_id, 
            'text': message 
        } 
         
        # Send the message to the specified room 
        send_message_response = requests.post(f'{WEBEX_API_BASE}/messages', headers=headers, json=message_data) 
         
        if send_message_response.status_code == 200: 
            print("Message sent to room {room_title}, {room_id} successfully!")
        else: 
            print("Failed to send the message. Please try again.") 

    return render_template('room_list_to_message.html', access_token=access_token, rooms=rooms)


#route for WEBEX
@app.route('/webex/<access_token>/<room_id>', methods=['GET','POST'])
def webex(access_token, room_id):
    return render_template('webex.html', access_token=access_token, room_id=room_id)



if __name__ == '__main__': 
    app.run(debug=True) 