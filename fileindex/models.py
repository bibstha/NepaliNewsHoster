from django.db import models
from django.conf import settings
import os

# Create your models here.
class FileIndex():
	# make sure to put a / at the end
	FOLDER_ROOT = settings.STATICFILES_DIRS[0]
	def getList(self, path):
		#TODO check path for security

		# Security Checks
		#if path[0:2] != "./":
		#	path = "./".join(path)
		folder = os.path.join(self.FOLDER_ROOT, path)
		dirList = []
		fileList = []
		for file in os.listdir(folder):
			fullPath = os.path.join(folder, file)
			if (os.path.isdir(fullPath)):
				dirList.append((file, 0))
			else:
				fileList.append((file, self.sizeof_fmt(os.path.getsize(fullPath))))
		dirList.sort()
		fileList.sort(reverse=True)
		return {'dirList':dirList, 'fileList':fileList}

	def getRelativePath(self, path):
		# Convert absolutely path to relative path
		if path[0:1] == "/":
			path = "".join( (".", path) )
		# Resolve complicated relative path to a simple one
		return os.path.relpath(os.path.join(self.FOLDER_ROOT, path), self.FOLDER_ROOT)

	def sizeof_fmt(self, num):
		for x in ['bytes','KB','MB','GB']:
			if num < 1024.0:
				return "%3.1f %s" % (num, x)
			num /= 1024.0
		return "%3.1f %s" % (num, 'TB')
