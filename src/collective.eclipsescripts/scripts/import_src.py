#
# Menu: Plone > Import src folder as workspace
# Copyright: Twinapex Research 2009
# Author: Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>
# License: MIT
"""

    What you do:
    
    - Create a buildout
    
    - Create a new workspace - use buildout src folder as the workspace folder
    
    - Run this script from menu

    What the script does:
    
    1. Scan workspace folder for all subfolders 
    
    2. If subfolder looks like a Python project, add it to the workspace
    
    3. Add Python nature to the project: Automatically construct Python project source folders for the project
    
    4. If project is an SVN import, add SVN nature to the project (actually this is done automatically
       with the latest Subversion plug-in if .svn files exist and we do not have to do this ourselves)
        
    This script uses "standard" (sigh) Eclipse tab-is-four-spaces

"""

# ResourcePlugin.getWorkspace().getRoot().getProject("PROJECT_FOLDER_NAME").create(null)

# http://docs.aptana.com/docs/index.php/Adding_metadata_to_an_Eclipse_Monkey_script

# http://help.eclipse.org/galileo/index.jsp

__docformat__ = "epytext"

import urllib
import os
import sys

from org.eclipse.core.resources import ResourcesPlugin
from org.eclipse.core.runtime import Path
from org.eclipse.core.runtime import NullProgressMonitor
from org.eclipse.core.resources import IncrementalProjectBuilder
from org.eclipse.jface.dialogs import ProgressMonitorDialog
from org.eclipse.jface.dialogs import MessageDialog
from org.eclipse.jface.operation import IRunnableWithProgress
from org.eclipse.debug.core import DebugPlugin  
from org.eclipse.ui.console import ConsolePlugin 
from org.eclipse.ui.console import IConsoleConstants
from org.eclipse.swt.widgets import Display
from org.eclipse.ui.externaltools.internal.model import IExternalToolConstants 

from org.python.pydev.core import IPythonNature
from org.python.pydev.plugin.nature import PythonNature
from org.python.pydev.plugin.nature import PythonPathNature
from org.python.pydev.debug.core import Constants as DebugConstants

# Global progress monitor instance, used to report wtf is going on, no real steps implemented
progress_monitor = None
progress_monitor_dialog = None

# Hold this for the worker thread
display = None


def get_console_by_name(name):
    """
    @return: IConsole handle to Eclipse message console, looked up by name
    """
    plugin = ConsolePlugin.getDefault()
    # IConsoleManager 
    conMan = plugin.getConsoleManager()
    existing = conMan.getConsoles()
    for con in existing:
        if con.getName() == name:
            return con
        
    return None

def get_os_script_name(filename):
    """ Add OS specific shell script file extension.
    
    UNIX: None
    
    Windows: bat
    
    @param filename: base filename
        
    """
    
    if sys.platform == "win32":
        return filename + ".bat"
    else:
        return filename
     

def open_monkey_console():
    """ Open monkey output console.
    
    http://wiki.eclipse.org/FAQ_How_do_I_write_to_the_console_from_a_plug-in%3F
    """

    name = "Eclipse Monkey Python Console"
    console = get_console_by_name(name)
    if console:
        view = window.getActivePage().showView(IConsoleConstants.ID_CONSOLE_VIEW)
        view.display(console)
    else:
        print "Couldn't find console with name:" + name    
    
    
def create_progress_monitor():
    global progress_monitor
    global progress_monitor_dialog
    
    progress_monitor_dialog = ProgressMonitorDialog(window.getShell())
    progress_monitor_dialog.setCancelable(True)
    progress_monitor_dialog.setOpenOnRun(True)
    
def get_buildout_path():
    """    
    @return: Path to buildout folder - assuming Eclipse is set up according to instructions
    """         

    # workspace is org.eclipse.core.internal.resources.Workspace
    # http://help.eclipse.org/galileo/topic/org.eclipse.platform.doc.isv/reference/api/org/eclipse/core/resources/IWorkspace.html
    workspace = ResourcesPlugin.getWorkspace()    
    root = workspace.getRoot()
    location = root.getRawLocation()
    path = location.toOSString()
    path = os.path.join(path, "..")
    path = os.path.normpath(path)
    return path


def get_project(workspace, project_name):
    """
    
    @return: Named workspace project or None if not exists
    """

    root = workspace.getRoot()

    all_projects = root.getProjects()

    for p in all_projects:
        if p.getName() == project_name:
            return p
        
    return None
            
def get_any_python_project(workspace):
    """
    Helper function to get reference to any workspace project (dummy ref needed for Plone instance launcher)
    """            
    root = workspace.getRoot()
    all_projects = root.getProjects()
    
    for project in all_projects:
        if project.isOpen():    
            if project.hasNature(PythonNature.PYTHON_NATURE_ID):
                return project
            
    return None
    
def is_good_python_project(folder):
    """ Check whether a folder is a pythonic project or not.
    
    Assume all good Python projects have setup.py or __init__.py file at the root folder. 
    
    @param folder: String, absolute path to folder
    @return: True if good to go
    """
    setuppy = os.path.join(folder, "setup.py")
    initpy = os.path.join(folder, "__init__.py")
    return os.path.exists(setuppy) or os.path.exists(initpy)


def pythonify(project):
    """ Add python nature to the project and set-up source paths.
    
    http://github.com/buriy/Pydev/blob/ba05f8799d6f9dfc6967fd7ded918ae765a200ca/plugins/org.python.pydev/src/org/python/pydev/plugin/nature/PythonNature.java
    
    http://help.eclipse.org/help32/topic/org.eclipse.platform.doc.isv/guide/resAdv_natures.htm?resultof=%22%69%70%72%6f%6a%65%63%74%22%20
    
    @param refer_to_omelette: Make project reference to "omelette" so that Plone namespace autom completion works.
    """
        
    PythonNature.addNature(project, 
                           progress_monitor, 
                           None,
                           None,
                           None,
                           None,
                           None)
    
    
def make_refer_to_omelette(project):
    """
    
    http://help.eclipse.org/help32/topic/org.eclipse.platform.doc.isv/reference/api/org/eclipse/core/resources/package-summary.html#main
    """
    print "Making omelette reference for project:" + project.getName()
    desc = project.getDescription();
    refs = desc.getReferencedProjects()
    
    workspace = project.getWorkspace()
    
    omelette_project = get_project(workspace, "omelette")    
    
    if omelette_project != None:
        if omelette_project not in refs:
            refs.append(omelette_project)
            desc.setReferencedProjects(refs)
            project.setDescription(desc, progress_monitor)
    
def set_src_folders(project):
    """ Assume the project root folder is source if there is no src folder.
    
    
    """
    nature = PythonNature.getPythonPathNature(project)
    sources = nature.getProjectSourcePathSet(False)
    
    # Check if we have src/ in project
    path = Path("src")
    if project.exists(path):
        source_path = "/" + project.getName() + "/src"
    else:
        source_path = "/" + project.getName()
        
    print "Adding source path:" + source_path + " existing:" + str(sources)
    
    # sources is java.util.HashSet
    # but PyDev seems to internally store paths as | delimited string
    #python_nature = PythonNature.getPythonNature(project)
    #projectSourcePath = python_nature.getStore().getPathProperty(PythonPathNature.getProjectSourcePathQualifiedName());
    
    if not source_path in sources:        
        sources.add(source_path)
        # Convert to Python list
        sources = list([ i for i in sources ])
        sources = "|".join(sources)        
        nature.setProjectSourcePath(sources)

from java.lang import Runnable
from java.lang import Object as JavaObject

class QuiteSafeProjectOpener(Runnable):
    """ Subclipse compatible project opener.
    
    If project.open() is run in a worker thread and the project happens to be
    
        1) SVN project which associates itself with Subclipse 
        
        2) Does not know password of SVN report
        
    Subclipse will block the worker thread forever because it tries to launch
    "Enter SVN password" dialog unsuccesfully.
    
    This class is hack around the behavior by using SWT asyncExec and Java 
    threading primitives.     
    """
    def __init__(self, project):
        self.project = project
        
    def run(self):
        self.project.open(progress_monitor)
    

def import_folder_as_python_project(root, project_name, folder, is_absolute=False, refer_to_omelette=False, create_test_launcher=True):
    """ Create a workspace Python project based on absolute folder path.
    
    http://stackoverflow.com/questions/251807/programmatically-generate-an-eclipse-project 
    
    @param root:  org.eclipse.core.internal.resources.WorkspaceRoot instance
    
    @param folder: String, absolute path to folder
    
    @oaram is_absolute: True if folder path is absolute FS path, otherwise in workspace root 
    
    @return: True if project was succesfully created
    """
    
    path_head, project_name = os.path.split(folder)
    

    old_project = get_project(root.getWorkspace(), project_name)
    
    exists = old_project != None
        
    project = root.getProject(project_name);
    
    if not exists:                    
        
        if is_absolute:
            # http://help.eclipse.org/help32/topic/org.eclipse.platform.doc.isv/reference/api/org/eclipse/core/resources/IProjectDescription.html#setLocation(org.eclipse.core.runtime.IPath)
            # 
            
            # http://cvalcarcel.wordpress.com/2009/07/26/writing-an-eclipse-plug-in-part-4-create-a-custom-project-in-eclipse-new-project-wizard-the-behavior/
            desc = project.getWorkspace().newProjectDescription(project.getName())    
            path = Path(folder)                        
            desc.setLocation(path)
            project.create(desc, progress_monitor);
        else:         
            project.create(progress_monitor);
    
    if not project.isOpen():
        # FFFFFFFFffffff....
        opener = QuiteSafeProjectOpener(project)
        display.syncExec(opener)        
        
    if not project.hasNature(PythonNature.PYTHON_NATURE_ID):
        pythonify(project)
        
    if refer_to_omelette:
        make_refer_to_omelette(project)
        
    set_src_folders(project)
    
    if create_test_launcher:
        create_launcher(project, unit_tests=True)
    
    
def import_omelette(root, path):
    """ Import omelette as a generic project if there is one.
    
    Also, make references to omelette from your other projects, so that
    name auto-completion works for Python.
    
    Assume this one is in buildout:
    
        - http://pypi.python.org/pypi/collective.recipe.omelette
        
    ...and make all Python classes browsable in workspace by creating a special project "omelette"

    @param root:  org.eclipse.core.internal.resources.WorkspaceRoot instance
    
    @param path: Workspace folder absolute path
            
    @return: True if omelette is in workspace
    """
        
    # Assume workspace location is src/
    # Assume omelette is in parts/omelette
    omelette_path = os.path.join(path, "..", "parts", "omelette")
    omelette_path = os.path.normpath(omelette_path)
    import_folder_as_python_project(root, "omelette", omelette_path, is_absolute=True, create_test_launcher=False)            
    return omelette_path
    
    
def check_omelette():
    """
    @return: True if omelette is available and user would like to import it
    """

    # workspace is org.eclipse.core.internal.resources.Workspace
    # http://help.eclipse.org/galileo/topic/org.eclipse.platform.doc.isv/reference/api/org/eclipse/core/resources/IWorkspace.html
    workspace = ResourcesPlugin.getWorkspace()    
    root = workspace.getRoot()
    
    # location will be IPath object, we need string presentation of the path
    # 
    location = root.getRawLocation()
    path = location.toOSString()
    omelette_path = os.path.join(path, "..", "parts", "omelette")
    omelette_path = os.path.normpath(omelette_path)

    if os.path.exists(omelette_path):                
        query = MessageDialog.openQuestion(window.getShell(), "Omelette detected", "Omelette buildout part contains all Python files used by Plone in symlinked structure. Importing omelette folder to workspace makes Python name completion to work. However, it is a very heavy task - loooong 'Building workspace' operation must be done when the workspace is refreshed. Unless you have a very powerful computer your computer will probably melt down to smoldering ashes. Alternatively toggle on 'Analyze open editors only' setting in PyDev preferences. Import omelette?") 
        return query
    else:
        return False

def check_we_are_src():
    """ Check whether workspace is set up according to instructions
    
    @return: False if this is not going to work
    """
    workspace = ResourcesPlugin.getWorkspace()    
    root = workspace.getRoot()
    location = root.getRawLocation()
    path = location.toOSString()
    
    if path.endswith("src") or path.endswith("products"): # products is a special case made for my Danish friend
    

        return True
    
    else:        
        query = MessageDialog.openQuestion(window.getShell(), 
                                           "Workspace is not correctly set up", 
                                           "Workspace folder should be src/ folder of buildout.  The current workspace folder '" + path + "' does not look like one. Scan checked out projects from this folder?") 
        return query
    
    
def download_ide_launcher(workspace_path):
    """ Download and install IDE compatible Zope run script if not exist.
    
    """
    
    print "Checking whether we need to download idelauncher.py"
    
    bin_path = os.path.join(workspace_path, "..", "bin")
    launcher = os.path.join(bin_path, "idelauncher.py")
    
    if not os.path.exists(launcher):
        
        url = "http://plone.org/documentation/tutorial/developing-plone-with-eclipse/idelauncher.py"
        print "Downloading " + url
        
        # TODO: if plone.org is slow hangs here
        progress_monitor.beginTask("Downloading idelauncher.py from plone.org", 1);
        urllib.urlretrieve(url, launcher)
        progress_monitor.done()
        
def create_launcher(project, unit_tests=False, name=None, args=None):
    """ Create a Eclipse launcher shortcut for a Python project
    
    References:
    
    * http://github.com/aptana/Pydev/blob/9bf905ef7bce7598a4819b9797cb073cc3305f0f/plugins/org.python.pydev.debug/src/org/python/pydev/debug/core/Constants.java
    
    * http://stackoverflow.com/questions/222093/how-to-run-eclipse-launch-configurations-programmatically
    
    * http://help.eclipse.org/help32/topic/org.eclipse.jdt.doc.isv/guide/jdt_api_run.htm?resultof=%22%67%65%74%4c%61%75%6e%63%68%4d%61%6e%61%67%65%72%22%20%22%67%65%74%6c%61%75%6e%63%68%6d%61%6e%61%67%22%20
    
    * http://help.eclipse.org/help32/topic/org.eclipse.platform.doc.isv/reference/api/org/eclipse/debug/core/package-summary.html?resultof=%22%44%65%62%75%67%50%6c%75%67%69%6e%22%20%22%64%65%62%75%67%70%6c%75%67%69%6e%22%20    
    
    @param unit_tests: True to create unit test launcher - otherwise launch Plone foreground
    """
    
    
    # Resolve IDE launcher location
    path = get_buildout_path() 

    # ILaunchManager 
    manager = DebugPlugin.getDefault().getLaunchManager()
    # ILaunchConfigurationType 
    type = manager.getLaunchConfigurationType(DebugConstants.ID_PYTHON_REGULAR_LAUNCH_CONFIGURATION_TYPE)
    # ILaunchConfigurationWorkingCopy
    
    if not name: 
        name = project.getName() + " tests"
        
    print "Updating launch configuration:" + name
        
    launches = manager.getLaunchConfigurations()
    launch = None
    for l in launches:
        if l.getName() == name:
            launch = l
            break
                
    if launch == None:
        # Lauch configuration for this project does not exist yet
        wc = type.newInstance(None, name)
    else:
        wc = launch.getWorkingCopy()
        
    wc.setAttribute(DebugConstants.ATTR_PROJECT, project.getName())
        
    if not args:
        if unit_tests:
            args = "test -s " + project.getName()
        else:
            args = "fg"
        
    launcher_path = os.path.join(get_buildout_path(), "bin", "idelauncher.py")
        
    wc.setAttribute(DebugConstants.ATTR_PROGRAM_ARGUMENTS, args)
    wc.setAttribute(DebugConstants.ATTR_LOCATION, launcher_path)
     
    config = wc.doSave()
    
    
def create_external_launcher(name, path, arguments, workdir=None):
    """ Create a launcher for external application.
    
    This will appear under External tools configuration... menu
    
    http://mobius.inria.fr/eclipse-doc/org/eclipse/ui/externaltools/internal/model/IExternalToolConstants.html
    """

    # ILaunchManager 
    manager = DebugPlugin.getDefault().getLaunchManager()
    # ILaunchConfigurationType 
    type = manager.getLaunchConfigurationType(IExternalToolConstants.ID_PROGRAM_LAUNCH_CONFIGURATION_TYPE)
    # ILaunchConfigurationWorkingCopy
            
    print "Updating external launch configuration:" + name

    if sys.platform == "win32":
        print "Adding .exe extension to:" + path
        path += ".exe"
        
    launches = manager.getLaunchConfigurations()
    launch = None
    for l in launches:
        if l.getName() == name:
            launch = l
            break
                
    if launch == None:
        # Lauch configuration for this project does not exist yet
        wc = type.newInstance(None, name)
    else:
        wc = launch.getWorkingCopy()

    wc.setAttribute(IExternalToolConstants.ATTR_TOOL_ARGUMENTS, arguments)
    wc.setAttribute(IExternalToolConstants.ATTR_LOCATION, path)
    
    if workdir:
        wc.setAttribute(IExternalToolConstants.ATTR_WORKING_DIRECTORY, workdir)
        
    config = wc.doSave()
    return config
        
        
         
def create_instance_launcher(project):
    """
    Create launcher which launches Plone as foreground.
    """
    create_launcher(project, name="Plone local server")

def create_zope_debug_launcher(project):
    """
    """
    path = get_buildout_path()
    workdir = path
        
    create_launcher(project, name="Zope debug shell", args="debug")        
    # path = os.path.join(path, "bin", get_os_script_name("instance"))
    # return create_external_launcher("Zope debug shell", path, "debug")
    
def create_buildout_launcher():
    """
    """
    path = get_buildout_path()
    workdir = path
        
    path = os.path.join(path, "bin", get_os_script_name("buildout"))
    create_external_launcher("Run buildout", path, "", workdir=workdir)    
    create_external_launcher("Run buildout (verbose)", path, "-vvv", workdir=workdir)
        

class MyRunnable(IRunnableWithProgress):
    """ 
    Wrap what we do to Eclipse async task.
    
    http://blogs.infosupport.com/blogs/peterhe/archive/2008/03/17/Monkeying-with-Eclipse.aspx
    
    http://www.prasannatech.net/2008/09/implementing-java-interfaces-in-jython.html
    """
    
    def __init__(self):
        self.import_omelette = False
    
    def prepare(self):
        """ Run all UI tasks before starting worker.
        
        Run in UI thread.
        
        @return: True if we are good to go
        """

        if check_we_are_src() == False:
            return False
        
        self.import_omelette = check_omelette()
                
        return True
    
    def run(self, monitor):
        
        global progress_monitor
        progress_monitor = monitor

        # workspace is org.eclipse.core.internal.resources.Workspace
        # http://help.eclipse.org/galileo/topic/org.eclipse.platform.doc.isv/reference/api/org/eclipse/core/resources/IWorkspace.html
        workspace = ResourcesPlugin.getWorkspace()
        print workspace
        
        # root is org.eclipse.core.internal.resources.WorkspaceRoot
        root = workspace.getRoot()
        print root.__class__
        
        # location will be IPath object, we need string presentation of the path
        # 
        location = root.getRawLocation()
        path = location.toOSString()
        
        
        print "Importing egg omelette if there is one:" + path
        if self.import_omelette:
            omelette_path = import_omelette(root, path)
        
        print "Converting source folder to workspace projects:" + path
            
        # Convert Eclipse resource wrapper to readable file-system path
        #rootpath = Path(".")
        #file = root.getFileForLocation(rootpath)
        #print file
        
        for potential_folder in os.listdir(path):
            name = potential_folder
            potential_folder = os.path.join(path, potential_folder) # Make absolute
            if is_good_python_project(potential_folder):
                print "Importing:" + potential_folder
                project = import_folder_as_python_project(root, name, potential_folder, refer_to_omelette=self.import_omelette)
            else:
                print "Not a Python project:" + potential_folder
                
        # Check whether we can create instance laucher
        project = get_any_python_project(workspace)
        if project != None:
            create_instance_launcher(project)
            create_zope_debug_launcher(project)
        
            
        create_buildout_launcher()
            
            
        # Run Pain here    
        workspace.build(IncrementalProjectBuilder.INCREMENTAL_BUILD, progress_monitor)
        
        # This is a possible failing operation, run as the last
        download_ide_launcher(path)
        
        print "All done"

def fix_ui():
    """
    """
    getViewSite().getActionBars().updateActionBars(); 
        
    
def go():
    global display
    
    # global variable window is org.eclipse.ui.internal.WorkbenchWindow
    open_monkey_console()

    display = Display.getCurrent()
    
    runnable = MyRunnable()
    if not runnable.prepare():
        return
    
    create_progress_monitor()
        
    progress_monitor_dialog = ProgressMonitorDialog(window.getShell())
    progress_monitor_dialog.run(True, True, runnable);
    
    window.updateActionBars()
    
            
go()    

