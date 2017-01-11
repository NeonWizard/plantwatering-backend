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
				username VARCHAR(20), 
				password BLOB, 
				email VARCHAR(20), 
				emailNotifications BOOLEAN
			)
	""")
		conn.commit()

	@staticmethod
	def retrieve(UID=None, username=None, email=None):
		if username: username = username.lower()
		for row in curs.execute("SELECT * FROM users WHERE UID=? OR username=? OR email=?", [UID, username, email]):
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
	def delete(username):
		username = username.lower()

		u = User.retrieve(username=username)
		if not u: return False

		curs.execute("DELETE FROM users WHERE username=?", (username, ))
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
	@staticmethod
	def createTable():
		curs.execute("""
			CREATE TABLE IF NOT EXISTS plants
			(
				ID INTEGER PRIMARY KEY,
				UID REFERENCES users(UID),
				name VARCHAR(20)
			)
	""")
		conn.commit()


User.createTable()
Plant.createTable()

def main():
	User.create("Semiz", "kittybiscuit1", "email@gmail.com", False)
	User.create("AverageWizard", "password123", "averagewizard13@gmail.com", True)
	User.create("zErF", "aojdbasd", "alshdausdv@email.com")
	User.create("xanu", "password123", "anthony.george@dixiesuccess.org", True)

	semiz = User.retrieve(username="Semiz")
	averagewizard = User.retrieve(username="AverageWizard")
	zerf = User.retrieve(username="ZeRf")

	print(semiz.username)
	print(semiz.email)
	semiz.email = "garfield@gmail.com"
	print(semiz.email)

	print()

	print(zerf.username)
	print(zerf.email)

	User.delete("ZeRf")

	print(semiz.verifyPassword("kittybiscuit1"))
	print(semiz.verifyPassword("notkittybiscuit1"))


if __name__ == "__main__":
	main()
