import os
import sys

def fetch_python_location(options, buildout):
	""" Determine Python installation location and expose it as buildout variable python-location """

	python = buildout["buildout"]["executable"]
	bin = os.path.basename(python)
	python = os.path.join(bin, "..")
		
	#python = buildout["buildout"]["python-location"] = python
	# Inject location to configure options
	options["configure-options"] = "--with-python=" + python
	
def build_dnet_wrapper(options, buildout):
	""" FUCK FUCK FUCK I HATE FUCKING DOING THINGS LIKE THIS """

	vars = {
		"parts" : buildout["buildout"]["parts-directory"],
		"executable" : buildout["buildout"]["executable"]
	}
	
	cwd = os.getcwd()
	
	try:
		dir = "%(parts)s/libdnet__compile__/libdnet-1.12/python" % vars
		os.chdir(dir)
		cmd = "%(executable)s setup.py install --prefix=%(parts)s/python-dnet" % 	vars
		print "Running:" + cmd
		os.system(cmd)
	finally:
		os.chdir(cwd)	
	