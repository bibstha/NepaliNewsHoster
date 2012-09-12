# Create your views here.
from osmusertracker import *
from django.http import HttpResponse

def api(request, username):
	userFile = UserFile(username)
	user = User(userFile)
	user.loadChangeset() # loads the main user changeset file
	# user.updateChangeset()
	# user.saveChangeset()
	user.loadValuesFromChangeset()
	changesetIdList = user.getChangesetIdList()
	for changesetId in changesetIdList:
		changesetFile = UserChangeFile(changesetId)
		changesetFile.download()
	userData = user.calculateUserData()

	for days in userData:
		for key in userData[days].keys():
			if key != 'createCount' and key != 'modifyCount':
				del userData[days][key]

	jsonOutput = json.dumps(userData, sort_keys=True, indent=4)
	return HttpResponse(jsonOutput)
	


	