#! /usr/bin/env python
# requres libraries requests lxml

import requests, os, time, argparse, json
from lxml import etree
from django.conf import settings

def log(logString, debug=False):
	if (not debug) or Config.DEBUG:
		print(logString)

def parseArgs():
	parser = argparse.ArgumentParser(description='Tool to download and parse OSM user statistics')
	parser.add_argument('username', help='the username as in http://www.openstreetmap.org/user/xxxxx. Pass the xxxxx here.')
	parser.add_argument('--update', action='store_true', help='Fetches updates for the user if previously cached.')

	return parser.parse_args()


class Config:
	ROOTPATH = "osmusertracker"
	DEBUG = False

class FileDownloader:
	_isLoaded = False
	_dataFolder = settings.APP_ROOT + "/" + Config.ROOTPATH + "/userdata"
	_fileName = None
	_url = None
	_data = None

	def __init__(self, fileName, url, dataFolder = None):
		if (dataFolder):
			self._dataFolder = dataFolder
		self._fileName = fileName
		self._url = url

	def fetchURL(self):
		r = requests.get(self._url)
		return r

	def writeFile(self, str):
		dataPath = self._dataFolder + "/" + self._fileName
		f = open(dataPath, "w")
		f.write(str)
		f.close()

	def readFileData(self):
		dataPath = self._dataFolder + "/" + self._fileName
		if os.path.exists(dataPath):
			f = open(dataPath, "r")
			self._data = f.read()
			self._isLoaded = True

	def download(self):
		dataPath = self._dataFolder + "/" + self._fileName
		if not os.path.exists(dataPath):
			log(dataPath + " does not exist, downloading it.")
			r = self.fetchURL()
			if r.status_code == 200:
				self.writeFile(r.text.encode('utf-8'))
				self._data = r.text.encode('utf-8')
				self._isLoaded = True
		else:
			log(dataPath + " already exists, skipping download.", debug=True)
			self.readFileData()

	def isLoaded(self):
		return self._isLoaded

	def getData(self):
		return self._data


class UserChangeFile(FileDownloader):
	_fileName = None
	_dataFolder = Config.ROOTPATH + "/userdata/changesets"
	_urlTemplate = "http://api.openstreetmap.org/api/0.6/changeset/{0}/download"
	_url = None

	def __init__(self, changesetId):
		self._fileName = changesetId + ".xml"
		self._url = self._urlTemplate.format(changesetId)


class UserFile(FileDownloader):
	_name = None
	_user = None
	_urlTemplate = "http://api.openstreetmap.org/api/0.6/changesets?display_name={0}"

	def __init__(self, name, update=False):
		self._name = name
		self._url = self._urlTemplate.format(name)
		self._fileName = name + ".xml"

class User:
	_changesetDataString = None
	_changesetXmlRoot = None
	_uid = None
	_user = None
	_userFile = None
	
	def __init__(self, userFile):
		self._userFile = userFile

	def loadChangeset(self):
		self._userFile.download()
		self.loadChangesetFromString(self._userFile.getData())

	def loadChangesetFromString(self, dataString):
		self._changesetXmlRoot = etree.fromstring(dataString)

	def loadValuesFromChangeset(self):
		changesetCount = len(self._changesetXmlRoot)
		if changesetCount > 0: # not what happens if there are no edits at all
			log("User XML contains {0} changeset Elements".format(changesetCount), debug=True)
			firstChangesetElement = self._changesetXmlRoot[0]
			self._uid = firstChangesetElement.get('uid')
			self._user = firstChangesetElement.get('user')
		else:
			log("User XML contains no changeset Element", debug=True)

	def getLastElement(self):
		lastElement = False
		if len(self._changesetXmlRoot) > 0:
			lastElement = self._changesetXmlRoot[0]
		return lastElement

	def getChangesetIdList(self):
		changesetIdList = []
		for changesetElement in self._changesetXmlRoot:
			changesetIdList.append(changesetElement.get('id'))
		return changesetIdList

	def calculateUserData(self):
		userData = {}

		# organize by date
		for changesetElement in self._changesetXmlRoot: # considering the data is generated date wize
			createdAtDate = time.strptime(changesetElement.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
			createdAtDateStr = time.strftime('%Y-%m-%d', createdAtDate)
			
			# consider dates are sorted, same dates are together, so the reset to 0 means new date
			if not userData.has_key(createdAtDateStr):
				userData[createdAtDateStr] = {}
				createCount = {'node':0, 'relation':0, 'way':0}
				modifyCount = {'node':0, 'relation':0, 'way':0}
			
			changeFile = UserChangeFile(changesetElement.get("id"))
			changeFile.readFileData()
			changeFileXmlRoot = etree.fromstring(changeFile.getData())
			
			g = lambda x:x.get('id')
			create = {}
			create['node'] = map(g, changeFileXmlRoot.xpath('/osmChange/create/node'))
			create['way'] = map(g, changeFileXmlRoot.xpath('/osmChange/create/way'))
			create['relation'] = map(g, changeFileXmlRoot.xpath('/osmChange/create/relation'))

			modify = {}
			modify['node'] = map(g, changeFileXmlRoot.xpath('/osmChange/modify/node'))
			modify['way'] = map(g, changeFileXmlRoot.xpath('/osmChange/modify/way'))
			modify['relation'] = map(g, changeFileXmlRoot.xpath('/osmChange/modify/relation'))

			userData[createdAtDateStr][changesetElement.get("id")] = {'create':create, 'modify':modify}

			createCount['node'] = createCount['node'] + len(create['node'])
			createCount['way'] += len(create['way'])
			createCount['relation'] += len(create['relation'])

			modifyCount['node'] += len(modify['node'])
			modifyCount['way'] += len(modify['way'])
			modifyCount['relation'] += len(modify['relation'])

			userData[createdAtDateStr]['createCount'] = createCount
			userData[createdAtDateStr]['modifyCount'] = modifyCount

		return userData

	def printData(self):
		userData = self.calculateUserData()

		for day in sorted(userData.keys()):
			print day
			print "CreateCount ::", userData[day]['createCount']
			print "ModifyCount ::", userData[day]['modifyCount']

	def updateChangesetFromString(self, updatedXmlStr):
		needsUpdate = False
		updatedXmlRoot = etree.fromstring(updatedXmlStr)
		oldChangesetId = 0 if len(self._changesetXmlRoot) == 0 else int(self._changesetXmlRoot[0].get('id'))

		# may be the comparison needs to be done by date?
		# we assume the topmost item is always the latest one
		if ( len(updatedXmlRoot) > 0 and int(updatedXmlRoot[0].get('id')) > oldChangesetId ):
			needsUpdate = True

			# combine each element from the beginning of our main XmlRoot
			pos = 0
			for changesetXmlElement in updatedXmlRoot:
				if int(changesetXmlElement.get('id')) > oldChangesetId:
					self._changesetXmlRoot.insert(pos, changesetXmlElement)
					pos = pos + 1

		return needsUpdate

	def updateChangeset(self):
		#print self.getChangesetIdList(), len(self.getChangesetIdList())
		r = self._userFile.fetchURL()
		self.updateChangesetFromString(r.text.encode('utf-8'))	
		# print self.getChangesetIdList(), len(self.getChangesetIdList())

	def saveChangeset(self):
		self._userFile.writeFile(etree.tostring(self._changesetXmlRoot, pretty_print=True, xml_declaration=True, encoding='utf-8'))

def main():
	args = parseArgs()
	username = args.username
	updateUserFile = args.update

	log("Downloading data for {0}".format(username))

	userFile = UserFile(username)
	user = User(userFile)
	user.loadChangeset() # loads the main user changeset file
	
	# uncomment the following lines if you want to update the userfile
	if updateUserFile:
		user.updateChangeset()
		user.saveChangeset()
	
	user.loadValuesFromChangeset() # loads individual changeset xmls from changeset list

	print "UserId :", user._uid
	print "UserName :", user._user

	changesetIdList = user.getChangesetIdList()
	for changesetId in changesetIdList:
		changesetFile = UserChangeFile(changesetId)
		changesetFile.download()

	user.printData()
	userData = user.calculateUserData()
	print json.dumps(userData, sort_keys=True, indent=4)


if __name__ == '__main__':
	main()
