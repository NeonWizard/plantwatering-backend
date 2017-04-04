import config

import sqlite3
import jwt
import bcrypt

conn = sqlite3.connect("PlantWatering.db")
curs = conn.cursor()

class SQLProperty():
	def __init__(self, name, tableName):
		self._name = name
		self._tableName = tableName

	def __get__(self, instance, type):
		if instance is None:
			return self
		else:
			return instance._cached[self._name]

	def __set__(self, instance, value):
		if not value: return

		curs.execute("UPDATE {} SET {}=? WHERE {}=?".format(self._tableName, self._name, instance.primaryKey), (value, instance._cached[instance.primaryKey]))
		conn.commit()

		instance._cached[self._name] = value

class User:
	primaryKey = "UID"
	UID = SQLProperty("UID", "users")
	username = SQLProperty("username", "users")
	password = SQLProperty("password", "users")
	email = SQLProperty("email", "users")
	emailNotifications = SQLProperty("emailNotifications", "users")

	def __init__(self, data):
		self._cached = data

	@staticmethod
	def createTable():
		curs.execute("""
			CREATE TABLE IF NOT EXISTS users 
			(
				UID INTEGER PRIMARY KEY, 
				username VARCHAR(20) NOT NULL UNIQUE, 
				password BLOB NOT NULL, 
				email VARCHAR(20) NOT NULL, 
				emailNotifications BOOLEAN NOT NULL
			)
	""")
		conn.commit()

	@staticmethod
	def _packData(row):
		data = {
			"UID": int(row[0]),
			"username": str(row[1]),
			"password": bytes(row[2]),
			"email": str(row[3]),
			"emailNotifications": bool(row[4])
		}
		return(data)

	@staticmethod
	def retrieve(UID=None, username=None, email=None):
		if username: username = username.lower()
		for row in curs.execute("SELECT * FROM users WHERE UID=? OR username=? OR email=?", (UID, username, email)):
			data = User._packData(row)

			return(User(data))
		return(None)

	@staticmethod
	def retrieveAll():
		items = []
		for row in curs.execute("SELECT * FROM users"):
			data = User._packData(row)

			items.append(data)
		return(items)

	@staticmethod
	def create(username, password, email, emailNotifications=True):
		username = username.lower()
		if User.retrieve(username=username):
			return False, "User already exists."

		if len(password) < config.MIN_PASSWORDLENGTH:
			return False, "Password is too short."

		password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

		curs.execute("INSERT INTO users (username, password, email, emailNotifications) VALUES (?, ?, ?, ?)", (username, password, email, emailNotifications))
		conn.commit()

		return True, "Success."

	@staticmethod
	def delete(UID=None, username=None):
		username = username.lower()

		u = User.retrieve(UID=UID, username=username)
		if not u: return False

		curs.execute("DELETE FROM users WHERE username=? or UID=?", (username, UID))
		conn.commit()

		return True

	def verifyPassword(self, otherPassword):
		# return self._cached["password"] == otherPassword
		return bcrypt.checkpw(otherPassword.encode("utf-8"), self._cached["password"])

	def createToken(self):
		return jwt.encode({"UID": self._cached["UID"]}, "sooper-secret", algorithm='HS256')

	def verifyToken(self, token):
		try:
			decoded = jwt.decode(token, "sooper-secret", algorithms=['HS256'])
		except:
			return False

		return decoded["UID"] == self._cached["UID"]

class Plant:
	primaryKey = "PID"
	PID = SQLProperty("PID", "plants")
	UID = SQLProperty("UID", "plants")
	name = SQLProperty("name", "plants")
	species = SQLProperty("species", "plants")
	waterInterval = SQLProperty("waterInterval", "plants")
	lastWatered = SQLProperty("lastWatered", "plants")

	def __init__(self, data):
		self._cached = data

	@staticmethod
	def createTable():
		curs.execute("""
			CREATE TABLE IF NOT EXISTS plants
			(
				PID INTEGER PRIMARY KEY,
				UID INTEGER,
				name VARCHAR(20) NOT NULL,
				species VARCHAR(30) NOT NULL,
				waterInterval DECIMAL(5, 2) NOT NULL,
				lastWatered TIMESTAMP NOT NULL,
				FOREIGN KEY (UID) REFERENCES users(UID)
			)
	""")
		conn.commit()

	@staticmethod
	def _packData(row):
		data = {
			"PID": int(row[0]),
			"UID": int(row[1]),
			"name": str(row[2]),
			"species": str(row[3]),
			"waterInterval": float(row[4]),
			"lastWatered": str(row[5])
		}
		return(data)
	
	@staticmethod
	def retrieve(PID):
		for row in curs.execute("SELECT * FROM plants WHERE PID=?", (PID, )):
			data = Plant._packData(row)

			return(Plant(data))
		return(None)

	@staticmethod
	def retrieveAllUser(UID):
		items = []
		for row in curs.execute("SELECT * FROM plants WHERE UID=?", (UID, )):
			data = Plant._packData(row)

			items.append(data)
		return(items)

	@staticmethod
	def retrieveAll():
		items = []
		for row in curs.execute("SELECT * FROM plants"):
			data = Plant._packData(row)

			items.append(data)
		return(items)

	@staticmethod
	def create(UID, name, species, waterInterval):
		waterInterval = round(waterInterval, 2) # Limit to 2 decimal points, plus ensure waterInterval is a float

		if not User.retrieve(UID=UID):
			return False, "No users with that UID exist."

		curs.execute("INSERT INTO plants (UID, name, species, waterInterval, lastWatered) VALUES (?, ?, ?, ?, ?)", (UID, name, species, waterInterval, 0))
		conn.commit()

		return True, "Success."

	@staticmethod
	def delete(PID):
		p = Plant.retrieve(PID)
		if not p: return False

		curs.execute("DELETE FROM plants WHERE PID=?", (PID, ))
		conn.commit()

		return True


User.createTable()
Plant.createTable()

def main():
	# --- User testing ---
	print("User testing:")
	User.create("AverageWizard", "password123", "averagewizard13@gmail.com", True)
	User.create("zErF", "aojdbasd", "alshdausdv@email.com")
	User.create("xanu", "password123", "anthony.george@dixiesuccess.org", True)

	averagewizard = User.retrieve(username="AverageWizard")
	zerf = User.retrieve(username="ZeRf")

	print()

	print(zerf.username)
	print(zerf.email)

	User.delete(username="ZeRf")

	print()

	print("AverageWizard password checking correct: " + str(averagewizard.verifyPassword("password123")))
	print("AverageWizard password checking incorrect: " + str(averagewizard.verifyPassword("notpassword123")))

	print(User.retrieveAll())

	# --- Plant testing --
	print("\nPlant testing:")
	
	Plant.delete(4) # Delete the plant from last execution of this
	Plant.delete(5)

	Plant.create(2, "Rose #1", "Rose", 24)
	Plant.create(2, "Rose #2", "Rose", 24)

	rose1 = Plant.retrieve(4)
	print(rose1.name)

if __name__ == "__main__":
	main()
