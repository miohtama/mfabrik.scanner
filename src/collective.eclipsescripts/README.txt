.. contents ::

Introduction
-------------

collective.eclipsescripts is an Eclipse integration plug-in for Plone development.
It aims to provide effective way for novice developers to get started with Plone.

Features
--------

* Create an Eclipse workspace from a buildout installation - all Python projects inside the src/ folder structure are 
  converted to Eclipse projects. You can keep your buildout in sync with your Eclipse workspace with one
  command.

* Set Eclipse preferences suitable for Plone/Zope development 
	
	* Tab stops to 8 spaces
	
	* File associations: .pt, .dtml, .zcml, etc.
	
	* Version control ignores (do not commit egg-info folders)
	
	* Text encoding settings to UTF-8

* Different UI Run shortcuts are automatically created

        * IDE compatible Zope launching script (retains console output by not making Zope to fork on start-up)

        * Plone local instance 

        * Unit test runners for all projects

        * Run buildout
        
        * Open Zope debug shell
        
        * Edit buildout.cfg

Prerequirements
----------------

What you need to know before messing with this script

* Basic Plone development and Eclipse usage knowledge 

        * What is `buildout <http://www.buildout.org/>`_ and buildout folder structure
        
        * How to use `Eclipse IDE <http://www.eclipse.org/>`_
                

Installation
------------ 

**Note**: Currently we can't support installation as Python egg or Eclipse plug-in bundle. This is being worked out. 

* Install `Aptana Studio <http://www.aptana.org/>`_ with PyDev and Subclipse plug-ins. Standalone Aptana installation
  is recommended as it is the fastest way to get started - you do not need to manually gather and install plug-ins.
  
        * Standard Eclipse standalone installation seems to have some component version compatibility issues.
          Aptana is the recommended way to install Eclipse for Python development.       

* Install `Python Monkey <http://code.google.com/p/jrfonseca/wiki/PythonMonkey>`_ and restart Eclipse 

* Checkout this project using Subclipse/Subversive to the Eclipse workspace as a project

	* Repository URL: https://svn.plone.org/svn/collective
	
	* Project path: collective.eclipsescripts/trunk
	
	* Alternatively copy Python egg contents to script/ folders under some of your Eclipse projects 

* Immediately menu *Scripts* should appear in the top menu bar  

* Open scripts in Python editor to see comments what they do

* Execute scripts by picking then from *Scripts* menubar

* Open console to see possible script output

	* Choose menu *Window* -> *Show View* -> *Console*. Then choose Eclipse Monkey Console
	  from alternative console views. Note: console might not be available until you have 
	  run one of the scripts.
	
Usage
-----

* Create a Plone 3 buildout - use your favorite buildout integrated tool to manage source code checkout under src/.
  E.g. 'Mr. Developer <http://pypi.python.org/pypi/mr.developer>`_
   
* Launch Eclipse - Switch workspace and choose src/ folder in buildout as the workspace location

* Configure Python 2.4 (for Plone 3.x) in preferences

* Set workspace settings - Choose *Scripts* -> *Plone* -> *Set Plone Preferences*

* Choose *Scripts* -> *Plone* -> *Import src folder as workspace* to import all checked out projects  
  under src/ as Eclipse projects. If you add new projects you can run this command without losing
  manual changes made to the projects.
  
        * Plone instance and projects will have launchers created in *Run configurations...* menu
        
        * Optionally, if you are using `collective.recipe.omelette <http://pypi.python.org/pypi/collective.recipe.omelette>`_
          all Plone packages are added under PyDev builders and code autocompletion will work for the projects
  
* Choose *Scripts* -> *Plone* -> *Edit buildout.cfg* if you wish to edit buildout.cfg
	
How it works
-------------

`Python Monkey exposes <http://code.google.com/p/jrfonseca/wiki/PythonMonkey>`_ Eclipse process to Python scripting environment 
through `Jython run-time <http://www.jython.org/>`_.
Everything what can be done by Eclipse plug-ins and Java development can be now done with few lines of Python code.
This makes the development of integration options for Eclipse real quick and dirty. 

Also, you do not need to have a separate Eclipse project for your scripts. You can keep your scripts
within any Eclipse project in the *scripts* top level folder.

For more information
--------------------

* http://docs.aptana.com/docs/index.php/Adding_metadata_to_an_Eclipse_Monkey_script

* http://help.eclipse.org/galileo/index.jsp

Possible future features
------------------------

* Deploy as real Eclipse plug-in

* paster integration: add view, content types directly from IDE

* deployment integration 

Author
------

`mFabrik Research Oy <mailto:info@mfabrik.com>`_ - Python and Plone professionals for hire.

* `mFabrik web site <http://mfabrik.com>`_  (`In Finnish <http://mfabrik.fi>`_)

* `mFabrik mobile site <http://mfabrik.mobi>`_ 

* `Blog <http://blog.mfabrik.com>`_

* `More about Plone <http://mfabrik.com/technology/technologies/content-management-cms/plone>`_ 

       