from PySide2 import QtCore, QtGui, QtWidgets
import shotgun_api3
import hou
import json

hda = hou.pwd().parent().parent()

# read image path and resolution from render settings
image_path = hou.node(hou.pwd().parm("path").eval()).parm("picture").evalAsString()
res = hou.node(hou.pwd().parm("path").eval()).parmTuple("resolution").eval()

def sg_header():
    """ Connect to Shotgrid's API """
    
    # read credentials from .json file
    path = hda.parm("creds").evalAsString()
    open_file = open(path)
    creds = json.load(open_file)  
    
    # connect to Shotgun API using credentials
    sg = shotgun_api3.Shotgun(creds["shotgun"]["website"], 
                              script_name= creds["shotgun"]["script_name"],
                              api_key= creds["shotgun"]["api_key"])
    return sg
    
def show_dialog():
    """Dialog window to visualize and publish the render in Shotgrid."""

    # create a Qt dialog window 
    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("Render Output")
        
    # create a QLabel to display the rendered image
    img_label = QtWidgets.QLabel(dialog)
    img = QtGui.QPixmap(image_path)
    img = img.scaled(res[0]*0.75,res[1]*0.75, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
    img_label.setPixmap(img)
    img_label.setAlignment(QtCore.Qt.AlignCenter)
    
    # create a QPushButton for publishing to Shotgrid
    button1 = QtWidgets.QPushButton("Publish to Shotgrid", dialog)
    button1.setMinimumSize(80, 50)
    # set font for size
    font = QtGui.QFont()
    font.setPointSize(16)
    button1.setFont(font)
    # connect button click to publish function
    button1.clicked.connect(lambda: publish(dialog))
    
    # create a QLabel for displaying notes
    notes_label = QtWidgets.QLabel()
    notes = hda.parm("gpt_notes").evalAsString()
    notes_label.setText(notes)
    notes_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    # set font for size
    font = QtGui.QFont()
    font.setPointSize(20)
    notes_label.setFont(font)
    
    # create main layout
    layout = QtWidgets.QVBoxLayout(dialog)    
    
    # TABS
    tabs = QtWidgets.QTabWidget()
    layout.addWidget(tabs)
    
    # create tab1
    tab1 = QtWidgets.QWidget()
    tab1_lyt = QtWidgets.QVBoxLayout()
    tab1.setLayout(tab1_lyt)     
    tabs.addTab(tab1, "Render View")
    
    # create tab2
    tab2 = QtWidgets.QWidget()
    tab2_lyt = QtWidgets.QVBoxLayout()
    tab2_lyt.setContentsMargins(40,20,20,20)
    tab2.setLayout(tab2_lyt)        
    tabs.addTab(tab2, "GPT4 Vision Feedback")   
    
    # add widgets to layouts
    tab1_lyt.addWidget(img_label)   
    tab2_lyt.addWidget(notes_label)
    layout.addWidget(button1)
    
    # Execute the dialog window
    dialog.exec_()
    
def publish(dialog):
    """Publish render to Shotgrid as a new Version of the selected Shot."""

    # connect to shotgrid API
    sg = sg_header()
     
    # read selected project id
    projects_menu = hda.parm("projects_menu")
    project_index = projects_menu.eval()
    project_id = projects_menu.menuItems()[project_index]
    project_id = int(project_id)
    
    # read selected shot id
    shots_menu = hda.parm("shots_menu")
    index = shots_menu.eval()
    shot_id = shots_menu.menuItems()[index]
    shot_id = int(shot_id)

    # read description and notes from parameters
    description = hda.parm("gpt_description").evalAsString()
    notes = hda.parm("gpt_notes").evalAsString()

    # create new version
    version_data = {
        "project": {"type": "Project", "id": project_id},
        "entity": {'type': 'Shot', 'id': shot_id},
    }
    version = sg.create("Version", version_data)
    
    # update version info: render image and desciption
    data = {
        "description": description,
        "image": image_path,
    }     
    sg.update("Version", version["id"], data)
    
    # create notes with GPT4 content
    note_data = { 
        "project": {"type": "Project", "id": project_id},
        "subject": "GPT4 feedback notes",
        "note_links": [{'type': 'Version', 'id': version["id"]}],
        "content": notes,
    }    
    sg.create("Note", note_data)
    
    # print message when the render is published
    print("Published to Shotgrid")
    
    # close window after publishing
    dialog.accept()  

# run dialog window on the main thread
work_item.node.scheduler.runOnMainThread(True, show_dialog)