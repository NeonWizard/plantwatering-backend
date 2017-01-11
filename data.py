import config

import sqlite3
import jwt
import bcrypt

conn = sqlite3.connect("PlantWatering.db")
curs = conn.cursor()

class SQLProperty():
	def __init__(self, name):
		self._name = name

	def __get__(self, instance, type):
		if instance is None:
			return self
		else:
			return instance._cached[self._name]

	def __set__(self, instance, value):
		if not value: return

		curs.execute("UPDATE users SET %s=? WHERE UID=?" % self._name, (value, instance._cached["UID"]))
		conn.commit()

		instance._cached[self._name] = value

class User:
	UID = SQLProperty("UID")
	username = SQLProperty("username")
	password = SQLProperty("password")
	email = SQLProperty("email")
	emailNotifications = SQLProperty("emailNotifications")

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
	def retrieve(UID=None, username=None, email=None):
		if username: username = username.lower()
		for row in curs.execute("SELECT * FROM users WHERE UID=? OR username=? OR email=?", (UID, username, email)):
			data = {}
			data["UID"] = int(row[0])
			data["username"] = str(row[1])
			data["password"] = bytes(row[2])
			data["email"] = str(row[3])
			data["emailNotifications"] = bool(row[4])

			return(User(data))
		return None

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
	PID = SQLProperty("PID")
	UID = SQLProperty("UID")
	name = SQLProperty("name")
	species = SQLProperty("species")
	waterInterval = SQLProperty("waterInterval")

	def __init__(self, data):
		self._cached = data

	@staticmethod
	def createTable():
		curs.execute("""
			CREATE TABLE IF NOT EXISTS plants
			(
				PID INTEGER PRIMARY KEY,
				UID REFERENCES users(UID),
				name VARCHAR(20) NOT NULL,
				species VARCHAR(30) NOT NULL,
				waterInterval DECIMAL(5, 2) NOT NULL
			)
	""")
		conn.commit()
	
	@staticmethod
	def retrieve(PID):
		for row in curs.execute("SELECT * FROM plants WHERE PID=?", (PID, )):
			data = {}
			data["PID"] = int(row[0])
			data["UID"] = int(row[1])
			data["name"] = str(row[2])
			data["species"] = str(row[3])
			data["waterInterval"] = float(row[4])

			return(Plant(data))
		return None

	@staticmethod
	def create(UID, name, species, waterInterval):
		waterInterval = round(waterInterval, 2) # Limit to 2 decimal points, plus ensure waterInterval is a float

		if not User.retrieve(UID=UID):
			return False, "No users with that UID exist."

		curs.execute("INSERT INTO plants (UID, name, species, waterInterval) VALUES (?, ?, ?, ?)", (UID, name, species, waterInterval))
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

	User.create("Semiz", "kittybiscuit1", "email@gmail.com", False)
	User.create("AverageWizard", "password123", "averagewizard13@gmail.com", True)
	User.create("zErF", "aojdbasd", "alshdausdv@email.com")
	User.create("xanu", "password123", "anthony.george@dixiesuccess.org", True)

	semiz = User.retrieve(username="Semiz")
	averagewizard = User.retrieve(username="AverageWizard")
	zerf = User.retrieve(username="ZeRf")

	print(semiz.username)
	print("Semiz email before change: " + semiz.email)
	semiz.email = "garfield@gmail.com"
	print("Semiz email after change: " + semiz.email)

	print()

	print(zerf.username)
	print(zerf.email)

	User.delete(username="ZeRf")

	print()

	print("Semiz password checking correct: " + str(semiz.verifyPassword("kittybiscuit1")))
	print("Semiz password checking incorrect: " + str(semiz.verifyPassword("notkittybiscuit1")))


	# --- Plant testing --
	print("\n")
	print(Plant.create(1, "Rose #1", "Rose", 24))

	Plant.retrieve(1)
	print(rose1.name)

if __name__ == "__main__":
	main()
