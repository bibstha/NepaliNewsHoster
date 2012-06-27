# Create your views here.
from django.shortcuts import render_to_response
from fileindex.models import FileIndex
from django.http import Http404

def index(request, baseName):
	fi = FileIndex()
	list = fi.getList('.')
	return render_to_response('fileindex/index.html', {'list': list, 'relPath': '.', 'baseName':baseName})

def list(request, baseName, urlRelativePath = "/"):
	fi = FileIndex()
	relativePath = fi.getRelativePath(urlRelativePath)
	
	# security risk if relativePath begins with ..
	if relativePath[0:2] == "..":
		raise Http404
	
	list = fi.getList(relativePath)
	return render_to_response('fileindex/index.html', {'list': list, 'relPath': relativePath, 'baseName':baseName})