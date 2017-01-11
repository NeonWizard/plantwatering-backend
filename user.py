import jwt

class User:
	def __init__(self, username, password, email, UID):
		self.username = username
		self.password = password
		self.email = email
		self.UID = UID

		self.plants = [
			# Sample plant
			{
				"species": "rose",
				"custom_name": "Rose #1",
				"water_interval": 24 # in hours
			}
		]

	# -- Retrieve info --
	def getUsername(self):
		return self.username

	def getEmail(self):
		return self.email

	def getPassword(self):
		return self.password

	def getUID(self):
		return self.UID

	def getPlants(self):
		return self.plants

	# -- Set info --
	def setPassword(self, password):
		self.password = password

	def setEmail(self, email):
		self.email = email

	def __str__(self):
		return str(self.UID) + ": " + self.getUsername() + " " + self.getEmail()

	# -- Other --
	def createToken(self):
		return jwt.encode({"UID": self.UID}, "sooper-secret", algorithm='HS256')

	def verifyToken(self, token):
		try:
			decoded = jwt.decode(token, "sooper-secret", algorithms=['HS256'])
		except:
			return False

		return decoded["UID"] == self.UID


class UserManager:
	def __init__(self):
		self._list = []
		self._usedUIDS = []

	def __str__(self):
		return "\n".join([str(user) for user in self._list])

	def createUser(self, username, password, email):
		if self.exists(username=username): return None

		UID = 0
		while UID in self._usedUIDS:
			UID += 1
		self._usedUIDS.append(UID)

		u = User(username, password, email, UID)
		self.insert(u)

		return u

	# returns boolean of success
	def insert(self, user):
		self._list.append(user)

	# returns boolean of success
	def delete(self, UID=None, username="", email=""):
		ind = self.find(UID, username, email)
		if ind != -1: return False

		self._usedUIDS.remove(self._list[ind].UID)
		del self._list[ind]
		return True

	# returns found user's index else -1
	def find(self, UID=None, username="", email=""):
		for i, user in enumerate(self._list):
			if user.getUID() == UID or user.getUsername() == username or user.getEmail() == email:
				return i

		return -1

	# returns found user else None
	def retrieve(self, UID=None, username="", email=""):
		ind = self.find(UID, username, email)
		if ind == -1: return None

		return self._list[ind]

	# returns boolean
	def exists(self, UID=None, username="", email=""):
		return self.find(UID, username, email) != -1

	def traverse(self, cb):
		for user in self._list:
			cb(user)
