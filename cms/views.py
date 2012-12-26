from django.template import RequestContext, loader, Context
from django.shortcuts import render_to_response
from fileindex.models import FileIndex, PatrikaService
from django.http import Http404, HttpResponseServerError
import sys

def index(request):
	fi = FileIndex()
	latestFileList = PatrikaService().getLatest()
	dateFileMap = {}
	for dirName, latestFile in latestFileList.items():
		fileDate = latestFile[0].replace(".pdf", "");
		if not dateFileMap.has_key(fileDate):
			dateFileMap[fileDate] = { dirName: latestFile }
		else:
			dateFileMap[fileDate][dirName] = latestFile
		# dateFileMap[fileDate][dirName][2] = dateFileMap[fileDate][dirName][1].replace("pdf", "png")
	
	return render_to_response('cms/index.html', {'relPath': '.', 
		'dateFileMap':dateFileMap}, context_instance = RequestContext(request))

	# return render_to_response('cms/index.html', context_instance = RequestContext(request))

