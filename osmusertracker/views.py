# Create your views here.
from osmusertracker import *
from django.http import HttpResponse
from django.shortcuts import render_to_response

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

	for days in sorted(userData.keys()):
		for key in userData[days].keys():
			if key != 'createCount' and key != 'modifyCount':
				del userData[days][key]

	jsonOutput = json.dumps(userData, sort_keys=True, indent=4)
	print "Hello", request.GET.get('callback')
	if request.GET.get('callback'):
		callback = request.GET['callback']
		jsonOutput = callback + "({0})".format(jsonOutput)
	return HttpResponse(jsonOutput, mimetype="application/json")

def api_update(request, username):
	userFile = UserFile(username)
	user = User(userFile)
	user.loadChangeset()
	user.updateChangeset()
	user.saveChangeset()
	jsonOutput = '{"status":"Complete"}'
	if request.GET.get('callback'):
		callback = request.GET['callback']
		jsonOutput = callback + "({0})".format(jsonOutput)
	return HttpResponse(jsonOutput, mimetype="application/json")
	
def usertrackerHtml(request):

	return render_to_response('osmusertracker/usertracker.html')