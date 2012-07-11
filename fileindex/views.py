from django.template import RequestContext, loader, Context
from django.shortcuts import render_to_response
from fileindex.models import FileIndex, PatrikaService
from django.http import Http404, HttpResponseServerError
import sys

def index(request, baseName):
	fi = FileIndex()
	list = fi.getList('.')
	latestFileList = PatrikaService().getLatest()
	return render_to_response('fileindex/index.html', {'list': list, 'relPath': '.', 'baseName':baseName,
		'latestFileList':latestFileList}, context_instance = RequestContext(request))

def list(request, baseName, urlRelativePath = "/"):
	fi = FileIndex()
	latestFileList = PatrikaService().getLatest()

	relativePath = fi.getRelativePath(urlRelativePath)
	
	# security risk if relativePath begins with ..
	if relativePath[0:2] == "..":
		raise Http404
	
	list = fi.getList(relativePath)
	return render_to_response('fileindex/index.html', {'list': list, 'relPath': relativePath, 'baseName':baseName, 
		'latestFileList':latestFileList}, context_instance = RequestContext(request))

def custom_500(request):
    t = loader.get_template('500.html')
    type, value, tb = sys.exc_info()
    return HttpResponseServerError(t.render(Context(
		{'exception_value': value, }
	)))