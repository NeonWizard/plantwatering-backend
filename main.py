import hug
import falcon
# from hug_middleware_cors import CORSMiddleware
from middleware_cors import CORSMiddleware

import random

from data import *

api = hug.API(__name__)
api.http.add_middleware(CORSMiddleware(api))


# Create new user
@hug.post("/users")
def register(body=None, response=None):
	# If a body isn't provided
	if not body:
		response.status = falcon.HTTP_400
		return({"error": "No fields were filled."})

	# If the body doesn't contain all required fields
	if "username" not in body or "email" not in body or "password" not in body:
		response.status = falcon.HTTP_400
		return({"error": "Not all required fields were filled."})

	username, email, password = body["username"], body["email"], body["password"]

	status, message = User.create(username, password, email)
	if not status:
		response.status = falcon.HTTP_400
		return({"error": message})

	token = User.retrieve(username=username).createToken()
	return({"id_token": token})

# Retrieve user by ID and create a JWT
@hug.post("/users/authenticate")
def loginUser(body=None, response=None):
	# If a body isn't provided
	if not body:
		response.status = falcon.HTTP_400
		return({"error": "No fields were filled."})

	# If the body doesn't contain a username or password field
	if "username" not in body or "password" not in body:
		response.status = falcon.HTTP_400
		return({"error": "Username or password not provided."})

	username, password = body["username"].lower(), body["password"]
	user = User.retrieve(username=username)

	# If no user exists under the supplied username
	if not user:
		response.status = falcon.HTTP_400
		return({"error": "No users exist under that username."})

	# If the provided password does not match the user's password
	if not user.verifyPassword(password):
		response.status = falcon.HTTP_400
		return({"error": "Password is incorrect."})

	print(username + " logged in successfully!")

	return({
		"id_token": user.createToken(),
		"UID": user.UID
	})

def verifyUser(user, request=None, response=None):
	if "AUTHORIZATION" not in request.headers:
		response.status = falcon.HTTP_400
		return({"error": "Authorization key not provided in header."})
	jwt = request.headers["AUTHORIZATION"].split()[1]

	if not user:
		response.status = falcon.HTTP_400
		return({"error": "User does not exist."})

	if not user.verifyToken(jwt):
		response.status = falcon.HTTP_403
		return({"error": "Not authorized."})

	return "" # woot


# Retrieve user's plants
@hug.get("/users/{UID}/plants")
def getUserPlants(UID, request=None, response=None):
	try:
		UID = int(UID)
	except ValueError:
		response.status = falcon.HTTP_400
		return({"error": "Invalid user ID."})

	user = User.retrieve(UID=UID)

	message = verifyUser(user, request, response)
	if message: return message

	plants = Plant.retrieveAllUser(UID)
	# for p in plants: p.pop("PID") # exclude PID key for security reasons

	return({"plants": plants})

@hug.delete("/users/{UID}/plants/{PID}")
def deletePlant(UID, PID, request=None, response=None):
	try:
		UID = int(UID)
		PID = int(PID)
	except ValueError:
		response.status = falcon.HTTP_400
		return({"error": "Invalid user or plant ID."})

	user = User.retrieve(UID=UID)

	message = verifyUser(user, request, response)
	if message: return message

	plant = Plant.retrieve(PID)
	if not plant:
		response.status = falcon.HTTP_404
		return {"error": "Plant couldn't be found under provided PID."}

	if plant.UID != UID:
		response.status = falcon.HTTP_403
		return {"error": "User doesn't own specified plant."}

	if not Plant.delete(PID=PID):
		# This should never run because it only returns False when the plant doesn't exist, which is already covered above
		return {"error": "Plant could not be deleted."}


@hug.put("/users/{UID}/plants/{PID}/water")
def waterPlant(UID, PID, request=None, response=None):
	try:
		UID = int(UID)
		PID = int(PID)
	except ValueError:
		response.status = falcon.HTTP_400
		return({"error": "Invalid user or plant ID."})

	user = User.retrieve(UID=UID)

	message = verifyUser(user, request, response)
	if message: return message

	plant = Plant.retrieve(PID)
	if not plant:
		response.status = falcon.HTTP_404
		return {"error": "Plant couldn't be found under provided PID."}

	if plant.UID != UID:
		response.status = falcon.HTTP_403
		return {"error": "User doesn't own specified plant."}

	if "TIMESTAMP" not in request.headers:
		response.status = falcon.HTTP_400
		return {"error": "No timestamp provided in headers."}
	
	plant.lastWatered = request.headers["TIMESTAMP"]


# # Retrieve a plant from a user, using a UID and PID
# @hug.get("/users/{UID}/plants/{PID}")
# def getUserPlant(UID, PID, jwt):
# 	UID = int(UID)
# 	user = UM.retrieve(UID=int(UID))

# 	message = verifyUser(user, request, response)
# 	if message: return(message)

# 	print(user.getUsername() + " has been given a specific one of their plants.")
# 	return("User verified!")
