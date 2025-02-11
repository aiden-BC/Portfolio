# SERVER AND DATABASE SETUP
import socket
import sqlite3
import json
import os

global db_path
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "foodiematchDB.db")

def start_server():
    """Start the server and listen for incoming connections."""
    try:
        # Create a TCP socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reuse of the address to avoid 'Address already in use' error
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind to all interfaces and port 8000
        server.bind(("0.0.0.0", 8000))
        server.listen(5)
        print("Server listening on port 8000")
        return server
    except Exception as e:
        print(f"ERROR--Failed to start server: {e}")
        exit(1)


global_user_handles = {}

""" Handles connection with a client socket """
def handle_client(client_socket):
    with client_socket:
        data = client_socket.recv(1024)
        if not data:
            return

        try:
            request = data.decode().split('--')
            print("Client request:", request)

            if len(request) < 2:
                response = "ERROR--Invalid request format"
                print("Sending response:", response)
                client_socket.send(response.encode())
                return

            code = request[0].strip()
            data = request[1].strip()

            print(f"Action: {code}, Data: {data}")
            
            # Possible actions
            match code:
                case "SIGNIN":
                    response = signin(data)
                case "SIGNUP":
                    response = signup(data)
                case "EVENTS":
                    response = get_events()
                case "JOIN_EVENT":
                    response = join_event(data)
                case "CREATE_EVENT":
                    response = create_event(data)
                case "UPDATE_EVENT":
                    response = update_event(data)
                case "MY_CREATED_EVENTS":
                    response = get_created_events(data)
                case "MY_JOINED_EVENTS":
                    response = get_joined_events(data)
                case "CLOSE_EVENT":
                    response = close_event(data)
                case "LEAVE_EVENT" :
                    response = leave_event_joined(data)
                case "CANCEL_EVENT" :
                    response = cancel_event(data)
                case "UPDATE_USER":
                    response = update_user(data)
                case "DELETE_USER":
                    response = delete_user(data)
                case "GET_JOINED_USERS":
                    response = get_joined_users(data)
                case _:
                    response = "ERROR--Unknown action"

        except Exception as e:
            response = f"ERROR--{str(e)}"

        print("Sending response:",response)
        client_socket.send(response.encode())

""" 
User sign in
params: data - JSON string containing userHandle and userPassword
returns: JSON string containing user data if successful, error message otherwise
"""
def signin(data):
    try:
        user = json.loads(data)
        user_handle = user["userHandle"]
        password = user["userPassword"]
    except (ValueError, KeyError) as e:
        return f"ERROR--Invalid data format: {str(e)}"

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT userPassword FROM users WHERE userHandle = ?", (user_handle,))
            result = cursor.fetchone()

            if not result:
                return "ERROR--User not found"

            if result[0] == password:
                cursor.execute("SELECT * FROM users WHERE userHandle = ?", (user_handle,)) # Get user data from database
                user_data = cursor.fetchone()
                print("RETRIEVED USER", user_data[1])

                global current_user_handle
                current_user_handle = user_data[0]  # Save the user handle in a global variable

                # Fetch events joined by the user
                cursor.execute("SELECT eventId FROM events_joined WHERE userHandle = ?", (user_handle,))
                joined_events = [row[0] for row in cursor.fetchall()]

                # Fetch user food preferences
                cursor.execute("SELECT foodPreference FROM user_food_preferences WHERE userHandle = ?", (user_handle,))
                food_preferences = [row[0] for row in cursor.fetchall()]

                # Fetch user interests
                cursor.execute("SELECT interest FROM user_interests WHERE userHandle = ?", (user_handle,))
                interests = [row[0] for row in cursor.fetchall()]

                user["userName"] = user_data[1]
                user["userLocation"] = user_data[2]
                user["userDescription"] = user_data[3]
                user["eventsJoined"] = joined_events
                user["userFoodPreferences"] = food_preferences
                user["userInterests"] = interests

                return json.dumps(user)
            else:
                return "ERROR--Incorrect password"
    except sqlite3.Error as e:
        return f"ERROR--Database error: {str(e)}"

"""
User registration
params: data - JSON string containing userHandle, userName, userPassword
returns: JSON string containing user data if successful, error message otherwise
"""
def signup(data):
    try:
        user = json.loads(data)
        user_handle = user["userHandle"]
        user_name = user["userName"]
        password = user["userPassword"]
    except (ValueError, KeyError) as e:
        return f"ERROR--Invalid data format: {str(e)}"

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE userHandle = ?", (user_handle,))
            if cursor.fetchone():
                return "ERROR--User already exists"

            # Insert new user into the database
            cursor.execute(
                "INSERT INTO users (userHandle, userName, userLocation, userDescription, userPassword) VALUES (?, ?, ?, ?, ?)",
                (user_handle, user_name, "", "", password)
            )
            conn.commit()  # Save changes to the database
            print("REGISTERED USER", user_name)

            return signin(data)
    except sqlite3.Error as e:
        return f"ERROR--Database error: {str(e)}"

"""
Get all event data form the database
returns: JSON string containing all event data
"""
def get_events():
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events")
            events_data = cursor.fetchall()
            events_list = []
            for event in events_data:
                print(event)
                event_dict = {
                    "eventId": event[0],
                    "eventName": event[1],
                    "eventCreator": event[2],
                    "eventLocation": event[3],
                    "eventDate": event[4],
                    "eventTime":event[5],
                    "eventDescription": event[6],
                    "eventMaxPeople": event[7],
                    "eventPeopleJoined": event[8],
                    "isClosed": event[9],
                }
                events_list.append(event_dict)

            return json.dumps(events_list)
    except sqlite3.Error as e:
        return f"ERROR--Database error: {str(e)}"

"""
Create an event
params: data - JSON string containing event data
returns: JSON string containing success message and event ID if successful, error message otherwise
"""  
def create_event(data):
    try:
        event = json.loads(data)
        eventName = event["eventName"]
        eventCreator = event["eventCreator"]
        eventLocation = event["eventLocation"]
        eventDate = event["eventDate"]
        eventTime = event["eventTime"]
        eventDescription = event["eventDescription"]
        eventMaxPeople = event["eventMaxPeople"]
        eventPeopleJoined = event["eventPeopleJoined"]
    except (ValueError, KeyError) as e:
        return f"ERROR--Invalid data format: {str(e)}"
    
    try:
        with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO events (
                        eventName, eventCreator, eventLocation, eventDate, eventTime, eventDescription, eventMaxPeople, eventPeopleJoined
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (eventName, eventCreator, eventLocation, eventDate, eventTime, eventDescription, eventMaxPeople, eventPeopleJoined))

                # Commit the transaction and retrieve the new eventId
                conn.commit()
                new_event_id = cursor.lastrowid

        # Return success response with the new event ID
        return json.dumps({"status": "SUCCESS", "eventId": new_event_id})
    except sqlite3.Error as e:
        return json.dumps({"status": "ERROR", "message": "ERROR--Database error: {str(e)}"})

"""
Update an event in the database
params: data - JSON string containing event data
returns: JSON string containing success message if successful, error message otherwise
"""
def update_event(data):
    try:
        # Parse the incoming data
        event = json.loads(data)
        event_id = event.get("eventId")
        event_name = event.get("eventName", "").strip()
        event_location = event.get("eventLocation", "").strip()
        event_date = event.get("eventDate", "").strip()
        event_time = event.get("eventTime", "").strip()
        event_description = event.get("eventDescription", "").strip()
        event_max_people = event.get("eventMaxPeople")
        
        if not event_id:
            return "ERROR--Event ID no found"

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check if event exists
            cursor.execute("SELECT * FROM events WHERE eventId = ?", (event_id,))
            event_exists = cursor.fetchone()
            if not event_exists:
                return f"ERROR--Event with ID {event_id} does not exist"

            # Build the SET clause dynamically based on which fields need updating
            cursor.execute("""
                UPDATE events
                SET eventName = ?, eventLocation = ?, eventDate = ?, eventTime = ?, eventDescription = ?,
                           eventMaxPeople = ?
                WHERE eventId = ?
            """, (event_name, event_location, event_date, event_time, event_description, event_max_people, event_id))
            return "SUCCESS"

        return "ERROR--Event update failed"
    
    except Exception as e:
        return f"ERROR--{str(e)}"

"""
User joins an event
params: data - JSON string containing event ID
returns: JSON string containing success message if successful, error message otherwise
"""
def join_event(data):
    try:
        print("CURRENT LOGGED USER: ",current_user_handle)
        event = json.loads(data)
        event_id = event.get("eventId")
        print("TRYING TO JOIN EVENT:",event_id)

        if not event_id or not current_user_handle:  # Use the global user handle
            return "ERROR--Event ID or UserHandle missing"

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check if the event is not full before allowing the user to join
            cursor.execute("""
                SELECT eventPeopleJoined, eventMaxPeople
                FROM events 
                WHERE eventId = ?
            """, (event_id,))
            event_info = cursor.fetchone()

            if not event_info:
                return "ERROR--Event does not exist"

            event_people_joined, event_max_people = event_info
            if event_people_joined >= event_max_people:
                return "ERROR--Event is full"

            # Add the user to the event in the events_joined table
            cursor.execute("""
                INSERT INTO events_joined (userHandle, eventId)
                VALUES (?, ?)
            """, (current_user_handle, event_id))

            # Increment the number of participants in the event
            cursor.execute("""
                UPDATE events 
                SET eventPeopleJoined = eventPeopleJoined + 1
                WHERE eventId = ?
            """, (event_id,))

            conn.commit()
            return "SUCCESS"

    except Exception as e:
        return f"ERROR--{str(e)}"

"""
Get all events created by a user
params: user_id - user handle
returns: JSON string containing all events created by the user
"""
def get_created_events(user_id):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events WHERE eventCreator = ?", (user_id,))
            events_data = cursor.fetchall()
            events_list = []
            for event in events_data:
                events_list.append({
                    "eventId": event[0],
                    "eventName": event[1],
                    "eventCreator": event[2],
                    "eventLocation": event[3],
                    "eventDate": event[4],
                    "eventTime": event[5],
                    "eventDescription": event[6],
                    "eventMaxPeople": event[7],
                    "eventPeopleJoined": event[8],
                    "isClosed": event[9],
                })
            return json.dumps(events_list)
    except sqlite3.Error as e:
        return f"ERROR--Database error: {str(e)}"

"""
Get all events joined by a user
params: user_id - user handle
returns: JSON string containing all events joined by the user
"""
def get_joined_events(user_id):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT e.eventId, e.eventName, e.eventCreator, e.eventLocation, 
                       e.eventDate, e.eventTime, e.eventDescription, 
                       e.eventMaxPeople, e.eventPeopleJoined, e.isClosed
                FROM events e
                INNER JOIN events_joined ej ON e.eventId = ej.eventId
                WHERE ej.userHandle = ?
            """, (user_id,))
            events_data = cursor.fetchall()

            events_list = []
            for event in events_data:
                events_list.append({
                    "eventId": event[0],
                    "eventName": event[1],
                    "eventCreator": event[2],
                    "eventLocation": event[3],
                    "eventDate": event[4],
                    "eventTime": event[5],
                    "eventDescription": event[6],
                    "eventMaxPeople": event[7],
                    "eventPeopleJoined": event[8],
                    "isClosed": event[9],
                })
            return json.dumps(events_list)
    except sqlite3.Error as e:
        return f"ERROR--Database error: {str(e)}"

"""
Close an event
params: data - JSON string containing event ID
returns: JSON string containing success message if successful, error message otherwise
"""
def close_event(data):
    try:
        event = json.loads(data)
        event_id = event.get("eventId")

        if not event_id:  # Ensure event ID is provided
            return "ERROR--Event ID missing"

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check if the event exists
            cursor.execute("""
                SELECT IsClosed 
                FROM events 
                WHERE eventId = ?
            """, (event_id,))
            event_info = cursor.fetchone()

            if not event_info:
                return "ERROR--Event does not exist"

            is_closed = event_info[0]
            if is_closed == 1:  # Event is already closed
                return "ERROR--Event is already closed"

            # Update the event to mark it as closed
            cursor.execute("""
                UPDATE events 
                SET IsClosed = 1 
                WHERE eventId = ?
            """, (event_id,))
            conn.commit()

            return "SUCCESS"

    except Exception as e:
        return f"ERROR--{str(e)}"

"""
Leave an event joined by a user
params: data - string containing user ID and event ID separated by a comma
returns: string containing success message if successful, error message otherwise
"""
def leave_event_joined(data):
    try:
        print("Received data for leave_event_joined:", data)

        if ',' not in data:
            return "ERROR--Invalid data format"

        user_id, event_id = data.split(',')
        print(f"User: {user_id}, Event: {event_id}")

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM events WHERE eventId = ?
            """, (event_id,))
            event_exists = cursor.fetchone()
            if not event_exists:
                print(f"Event {event_id} does not exist")
                return "ERROR--Event does not exist"

            cursor.execute("""
                DELETE FROM events_joined 
                WHERE userHandle = ? AND eventId = ?
            """, (user_id, event_id))

            if cursor.rowcount == 0:
                print(f"User {user_id} was not associated with event {event_id}")
                return "ERROR--User is not part of this event"

            cursor.execute("""
                UPDATE events
                SET eventPeopleJoined = eventPeopleJoined - 1
                WHERE eventId = ? AND eventPeopleJoined > 0
            """, (event_id,))

            if cursor.rowcount == 0:
                print(f"Failed to decrement participant count for event {event_id}")
                return "ERROR--Failed to update participant count"

            conn.commit()
            print("Successfully removed user from event")
            return "SUCCESS"
    except Exception as e:
        print(f"Error in leave_event_joined: {str(e)}")
        return f"ERROR--{str(e)}"

"""
Cancel an event
params: data - string containing event ID
returns: string containing success message if successful, error message otherwise
"""
def cancel_event(data):
    try:
        event_id = data.strip() 

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM events WHERE eventId = ?
            """, (event_id,))
            event_exists = cursor.fetchone()
            if not event_exists:
                print(f"Event {event_id} does not exist")
                return "ERROR--Event does not exist"

            cursor.execute("""
                DELETE FROM events WHERE eventId = ?
            """, (event_id,))
            print(f"Deleted event {event_id} from events")

            cursor.execute("""
                DELETE FROM events_joined WHERE eventId = ?
            """, (event_id,))
            print(f"Deleted all participants for event {event_id} from events_joined")

            conn.commit()
            print("Event cancelled successfully")
            return "SUCCESS"
    except Exception as e:
        print(f"Error in cancel_event: {str(e)}")
        return f"ERROR--{str(e)}"

"""
Update user details
params: data - JSON string containing user data
returns: string containing success message if successful, error message otherwise
"""
def update_user(data):
    try:
        # Parse the JSON data
        user = json.loads(data)
        user_handle = user.get("userHandle")  # Primary key, cannot be changed
        user_name = user.get("userName", "").strip()
        user_location = user.get("userLocation", "").strip()
        user_description = user.get("userDescription", "").strip()
        food_preferences = user.get("userFoodPreferences", [])
        interests = user.get("userInterests", [])

        if not user_handle:
            return "ERROR--User handle is required"

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Update the main user details
            cursor.execute("""
                UPDATE users
                SET userName = ?, userLocation = ?, userDescription = ?
                WHERE userHandle = ?
            """, (user_name, user_location, user_description, user_handle))

            # Clear and update food preferences
            cursor.execute("DELETE FROM user_food_preferences WHERE userHandle = ?", (user_handle,))
            for food in food_preferences:
                cursor.execute("""
                    INSERT INTO user_food_preferences (userHandle, foodPreference)
                    VALUES (?, ?)
                """, (user_handle, food))

            # Clear and update interests
            cursor.execute("DELETE FROM user_interests WHERE userHandle = ?", (user_handle,))
            for interest in interests:
                cursor.execute("""
                    INSERT INTO user_interests (userHandle, interest)
                    VALUES (?, ?)
                """, (user_handle, interest))

            conn.commit()
            return "SUCCESS"

    except Exception as e:
        return f"ERROR--{str(e)}"

"""
Delete an user from the database
params: user_handle - user handle
returns: string containing success message if successful, error message otherwise
"""
def delete_user(user_handle):
    try:
        with sqlite3.connect(db_path) as conn:
            # Connect to the database
            cursor = conn.cursor()

            # Begin transaction
            conn.execute('BEGIN TRANSACTION;')

            # Step 1: Delete user's joined events
            cursor.execute("""
                DELETE FROM events_joined
                WHERE userHandle = ?;
            """, (user_handle,))

            # Step 2: Delete user's food preferences
            cursor.execute("""
                DELETE FROM user_food_preferences
                WHERE userHandle = ?;
            """, (user_handle,))

            # Step 3: Delete user's interests
            cursor.execute("""
                DELETE FROM user_interests
                WHERE userHandle = ?;
            """, (user_handle,))

            # Step 4: Delete events created by the user
            cursor.execute("""
                DELETE FROM events
                WHERE eventCreator = ?;
            """, (user_handle,))

            # Step 5: Delete the user from the users table
            cursor.execute("""
                DELETE FROM users
                WHERE userHandle = ?;
            """, (user_handle,))

            # Commit the transaction
            conn.commit()

            print(f"USER '{user_handle}' DELETED")
            return "SUCCESS"
    except sqlite3.Error as e:
        # Rollback transaction in case of an error
        conn.rollback()
        print(f"Error occurred: {e}")
        return str(e)
    finally:
        # Close the connection
        conn.close()

"""
Get all users joined to an event
params: event_id - event ID
returns: JSON string containing all users joined to the event
"""
def get_joined_users(event_id):
    try:
        with sqlite3.connect(db_path) as conn:
            # Connect to the database
            cursor = conn.cursor()
            # Execute the query
            cursor.execute("SELECT userHandle FROM events_joined WHERE eventId = ?", (event_id,))
            # Fetch all results
            users = cursor.fetchall()
            # Return a list of user handles
            return json.dumps([user[0] for user in users])
    except sqlite3.Error as e:
        print("Error accessing the database:", e)
        return "ERROR"
    finally:
        # Close the connection
        conn.close()

server = start_server()
while True:
    try:
        client_socket, addr = server.accept()
        print(f"Connection accepted from {addr}")
        handle_client(client_socket)
    except KeyboardInterrupt:
        print("\nShutting down server.")
        break
    except Exception as e:
        print(f"ERROR--Connection handling error: {e}")