Introduction
============

mfabrik.scanner is a Python application for easy network scanning.

The application itself is simple, but the dependency and download process is complex.
The application is distirbuted as `buildout <http://buildout.org>`_ file which will
download, configure, compile and install necessary dependencies

* libpcap

* libdnet

* Python libpcap wrapper

* Python libdnet wrapper

* `scapy <http://www.secdev.org/projects/scapy/>`_

* mfabrik.scanner

Buildout will take care of it that you can actually use pcap and dnet Python modules - 
they are not distributed or packaged in modern manner and made easily available on PyPi.
This is were `hexagonit.recipe.cmmi - compile, make. make install buildout recipe <http://pypi.python.org/pypi/hexagonit.recipe.cmmi>`_
will save you. We do pretty nasty things like running Python code in pre-configure-hooks
to set-up buildout properly.

Because the procedure heavily depends on freely available development tools,
like C compiler, Windows users may or may not find this useful. 

Installation
============

Checkout the source from Github using Git.

Example::
	
	git 
	python bootstrap.by
	bin/buildout
	
Usage
=====

Example::

	bin/scanner
	
Kudos
-----

* 
	
Author
------

`mFabrik Research Oy <mailto:info@mfabrik.com>`_ - Python and Plone professionals for hire.

* `mFabrik web site <http://mfabrik.com>`_ 

* `mFabrik mobile site <http://mfabrik.mobi>`_ 

* `Blog <http://blog.mfabrik.com>`_


