import sqlite3

class Manager:
	def __init__(self):
		self.conn = sqlite3.connect("PlantWatering.db")
		self.curs = self.conn.cursor()

		self.createTables()

	def createTables(self):
		self.curs.execute("""
			CREATE TABLE IF NOT EXISTS users 
			(
				uid INTEGER PRIMARY KEY, 
				username VARCHAR(20), 
				password CHAR(60), 
				email VARCHAR(20), 
				emailNotifications BOOLEAN
			)
	""")
		self.curs.execute("""
			CREATE TABLE IF NOT EXISTS plants
			(
				id INTEGER PRIMARY KEY,
				uid REFERENCES users(uid),
				name VARCHAR(20)
			)
	""")

	def createUser(self, username, password, email, emailNotifications):
		if self.exists(username=username):
			return False

		self.curs.execute("INSERT INTO users (username, password, email, emailNotifications) VALUES (?, ?, ?, ?)", (username, password, email, emailNotifications))
		self.conn.commit()


	# ==================
	#  Update functions
	# ==================
	def updateUserFields(self, UID=None, password):
		if not (password or UID): return False

		self.curs.execute("UPDATE users SET password=? WHERE UID=?", (password, UID))
		self.conn.commit()

		return True

	def updateUserEmail(self, UID, email):
		if not (email or UID): return False

		self.curs.execute("UPDATE users SET password=? WHERE UID=?", (email, UID))
		self.conn.commit()

		return True

	def updateUserEmailNotifications(self, UID, emailNotifications):
		if not (emailNotifications or UID): return False

		self.curs.execute("UPDATE users SET password=? WHERE UID=?", (emailNotifications, UID))
		self.conn.commit()

		return True
	# ==================

	def delete(self, username):
		if not self.exists(username=username):
			return False

		self.curs.execute("DELETE FROM users WHERE username=?", (username, ))
		self.conn.commit()

		return True

	def retrieve(self, UID=None, username=None, email=None):
		for row in self.curs.execute("SELECT * FROM users WHERE uid=? OR username=? OR email=?", [UID, username, email]):
			data = {}
			data["UID"] = int(row[0])
			data["username"] = str(row[1])
			data["password"] = str(row[2])
			data["email"] = str(row[3])
			data["emailNotifications"] = bool(row[4])
			return(data)

		return None

	def exists(self, UID=None, username=None, email=None):
		return self.retrieve(UID, username, email) != None


def main():
	M = Manager()

	M.createUser("Semiz", "kittybiscuit1", "email@gmail.com", False)
	M.createUser("AverageWizard", "password123", "averagewizard13@gmail.com", True)
	M.createUser("delet_this", "password123", "woh@aol.com", True)
	M.createUser("mod_this", "p", "p", False)

	print("Delete: " + M.delete("delet_this"))
	print("Retrieve: " + M.retrieve(username="Semiz"))
	M.updateUserPassword()
	print("Modify: ")

if __name__ == "__main__":
	main()
