from django.template import RequestContext, loader, Context
from django.shortcuts import render_to_response
from fileindex.models import FileIndex
from django.http import Http404, HttpResponseServerError
import sys

def index(request):
	return render_to_response('cms/index.html', context_instance = RequestContext(request))

