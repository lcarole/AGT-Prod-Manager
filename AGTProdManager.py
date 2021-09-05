import os
import os.path
import time
import sys
import re
import shutil
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMaya as api
import maya.OpenMayaUI as apiUI
from functools import partial

filepath = ""

#Class which determines who the current user is and is preference.
class PrefUserWindow :
	namePref = ""
	firstnamePref = ""
	locationPref = ""
    
    #If the preference file doesn't exist, open a window and ask the user to write is Firstname and Nickname or at least his/her initials.
	def UserWindow(a,b):
		global filepath
		if str(b) != "firstOpening":
			cmds.deleteUI("mainColumn")

		uisBefore = cmds.lsUI (wnd = True)
		superFen = uisBefore[0]
		for wnd in uisBefore:
			if wnd == 'AGT_Prod_Manager':
				superFen = wnd

		cmds.columnLayout('WindowPreferences', h=600, w=600, p=superFen)
		cmds.rowLayout(numberOfColumns=2)
		cmds.text("Entrer votre nom : ")
		cmds.textField("nameUser",bgc = [1,1,1],w=200, tx=a.namePref)
		cmds.setParent('..')
		cmds.rowLayout(numberOfColumns=2)
		cmds.text("Entrer votre prenom : ")
		cmds.textField("firstnameUser",bgc = [1,1,1],w=200, tx=a.firstnamePref)
		cmds.setParent('..')
		cmds.rowLayout(numberOfColumns=2)
		cmds.text("Entrer le chemin correspondant : ")
		cmds.textField("MayaLocation",bgc = [1,1,1],w=200, tx=a.locationPref)
		cmds.setParent('..')
		
		#Save the preferences file and create it if it doesn't exist
		def SaveInFile(a):
			namePref = cmds.textField("nameUser",query=True,tx=True)
			firstnamePref = cmds.textField("firstnameUser",query=True,tx=True)
			locationPref = cmds.textField("MayaLocation",query=True,tx=True)
			if os.path.exists("C:/Maya_Preferences") == False:
			    os.makedirs("C:/Maya_Preferences")
			    print "Repertoire creer"
			    
			    
			filepref = os.open("C:/Maya_Preferences/Shamepipe_Preferences.txt",os.O_RDWR | os.O_TRUNC | os.O_CREAT)
			os.write(filepref,"nom = "+namePref+"\n")
			os.write(filepref,"prenom = "+firstnamePref+"\n")
			os.write(filepref,"Maya Location = "+locationPref)
			os.close(filepref)
			cmds.deleteUI('WindowPreferences')
			cmds.deleteUI('Barre')
			if cmds.columnLayout("mainColumn",query=True,exists=1):
			    cmds.deleteUI("mainColumn")
			ShamePipeWindow().createAndShowWindow('AGT_Prod_Manager')
			listFic = cmds.textScrollList("listFic",q=True)
			ShamePipeWindow().openProject(listFic, "listFic",True)
			
		def cancelPref(a):
		    cmds.deleteUI('WindowPreferences')
		    cmds.deleteUI('Barre')
		    if cmds.columnLayout("mainColumn",query=True,exists=1):
		    	cmds.deleteUI("mainColumn")
		    ShamePipeWindow().createAndShowWindow('AGT_Prod_Manager')
		    listFic = cmds.textScrollList("listFic", query=True)
		    ShamePipeWindow().openProject(listFic, "listFic", True)
		    
		cmds.rowLayout(numberOfColumns=2)
		cmds.button("SAVE",c=SaveInFile)
		cmds.button("Cancel",c=cancelPref)
		cmds.setParent('..')

	def __init__(self):
		self.namePref = ""
		self.firstnamePref = ""
		self.locationPref = ""
		if (os.path.exists("C:/Maya_Preferences/Shamepipe_Preferences.txt")):
			filepref = os.open("C:/Maya_Preferences/Shamepipe_Preferences.txt",os.O_RDWR)
			lastUserInfo = os.read(filepref,999)
			lastUserInfo = lastUserInfo.split("\n")			
			self.namePref = lastUserInfo[0].split('= ')
			self.namePref = self.namePref[1]
			self.firstnamePref = lastUserInfo[1].split('= ')
			self.firstnamePref = self.firstnamePref[1]
			self.locationPref = lastUserInfo[2].split('= ')
			self.locationPref = self.locationPref[1]
			#print(self.namePref+"\n"+self.firstnamePref+"\n"+self.locationPref)
			os.close(filepref)
		else:
			self.UserWindow("firstOpening")
		
class ShamePipeWindow :
	#Load the image of the corresponding version when the version selected changes
	def versionSelectedChange(a, item):
		image = om.MImage()
		puw = PrefUserWindow()
		sourceName = item.split(".")
		sourceListFic = cmds.textScrollList("listFic", query=True, si=1 )
		imgName = ""
		if os.path.exists(filepath + str(sourceListFic[0]) + "/Versioning/"):
			imgName = filepath + str(sourceListFic[0]) + "/Versioning/" + str(sourceName[0])
			
		elif os.path.exists(filepath + str(sourceListFic[0]) + "/Versions/"):
			imgName = filepath + str(sourceListFic[0]) + "/Versions/" + str(sourceName[0])
		image.readFromFile(imgName+".png")
		image.resize( 246,126 )
		tamponName = "C:/Maya_Preferences/tampon.png"
		if os.path.exists(tamponName) == False:
			if os.path.exists("C:/Maya_Preferences") == False:
				os.makedirs("C:/Maya_Preferences")
		image.writeToFile( tamponName, 'png')
		cmds.image("tampon", edit=True, vis=True, image=tamponName, w=246, h=126)
		
		cmds.textScrollList("infos",e=True,ra=True)
		selectedItem = cmds.textScrollList("listFic",q=True,si=True)
		selectedItem = selectedItem[0]
		cmds.textScrollList("infos",e=True,append="Item : "+selectedItem[1:])
		filepathInfo = re.split("(\d{2}_\w*)",filepath)
		filepathInfo = re.split("(\d{2}_)",filepathInfo[1])
		filepathInfo = "Step : "+filepathInfo[2]
		cmds.textScrollList("infos",e=True,append=filepathInfo)
		fileSelected = cmds.optionMenu("listVersion",q=True,v=True)
		version = re.split("([vV]\d+)",fileSelected)
		version = re.split("[vV]",version[1])
		version = str(version[1])
		cmds.textScrollList("infos",e=True,append="Version : "+version)
		status = os.stat(imgName + ".ma")
		fromdate = time.ctime(os.stat(imgName+".ma").st_mtime)
		fromdate = str(fromdate).split(" ")
		fromdate = fromdate[0] +" "+ fromdate[2] +" "+ fromdate[1] +" "+ fromdate[4] + " " + fromdate[3]
		cmds.textScrollList("infos",e=True,append="Last Version : "+fromdate)
		artist = imgName[-2]+imgName[-1]
		print "artist = "+artist
		cmds.textScrollList("infos",e=True,append="Artist : "+artist)
		cmds.text("versionInfo",e=True,label = "Date = "+fromdate+"\nArtist = "+artist)
		
	#Save all versions of the selected items into the optionMenu
	def clickOnListFic(self):
		# RESIZE IMAGE PREVIEW
		global filepath
		source = cmds.textScrollList( "listFic", query=True, si=1 )
		versioningPath = ""
		if os.path.exists(filepath + str(source[0]) + "/Versioning/"):
			versioningPath = filepath + str(source[0]) + "/Versioning/"
		elif os.path.exists(filepath + str(source[0]) + "/Versions/"):
			versioningPath = filepath + str(source[0]) + "/Versions/"
		if os.path.exists(versioningPath) == True:
			menuItems = cmds.optionMenu('listVersion',q=True,ils = True)
			if menuItems:
				cmds.deleteUI(menuItems)			        
			for i in os.listdir(versioningPath):
				if i.split(".")[1] == "ma":
					cmds.menuItem(label=i,parent="listVersion")
			menuItemSelected = cmds.optionMenu('listVersion',q=True,v=True)
			self.versionSelectedChange(menuItemSelected)

    #Refresh lists when a new project is open
	def refreshScrollListAfterOpenProject(self,listFic):
		c = -1
		global dirs
		global filepath
		dirs = []
		for i in os.listdir(filepath):
			c=c+1
			dirs.append(i)
		scrollList = cmds.textScrollList("listRep",edit=True,removeAll=True, visible = True)
		scrollListFic = cmds.textScrollList("listFic",edit=True,removeAll=True, visible = True)
		for i in dirs:
		    if os.path.exists(filepath+"/"+i+"/"):
		        cmds.textScrollList("listRep",edit=True,append=i)
		    else:
		        cmds.textScrollList("listFic",edit=True,append=i)
		        
		#If you have some issues with the tampon, add def resize here
		cmds.textScrollList("listFic", e=True, sc=partial(self.clickOnListFic))

	# Open an existing project with the good architecture
	def openProject(self, listFic, a, needRefresh):
		global filepath
		if needRefresh == False:
			dirPath = cmds.fileDialog2(fileMode = 3, dialogStyle=1)		
			filepath = dirPath[0]		
		self.refreshScrollListAfterOpenProject(listFic)

    #Create and open the main window
	def createAndShowWindow(self,fenetre):
		largeur = 540
		hauteur = 720
		
		# Create a new project with the correct architecture
		def createNewProject(listFic, a):
		    
			# Refresh both list after creating the new project
			def refreshScrollListAfterNewProject(listFic):
				c = -1
				global dirs
				global filepath
				dirs = []
				
				for i in os.listdir(filepath):
					c=c+1
					dirs.append(i)
				scrollList = cmds.textScrollList("listRep",edit=True,removeAll=True, visible = True)
				scrollList = cmds.textScrollList(listFic,edit=True,removeAll=True, visible = True)
				scrollList = cmds.textScrollList("listRep",edit=True,append=dirs)
				
			#Create a new project and refresh lists
			result = cmds.promptDialog(title='Name scene',message='Enter un nom pour votre scene :',button=['OK', 'Cancel'],defaultButton='OK',cancelButton = 'Cancel')
			if result == 'OK':
				Projet = cmds.promptDialog(query=True, text=True)
				dirPath = cmds.fileDialog2(fileMode = 3, dialogStyle=1)
				path = dirPath[0] +"\\" + Projet
				global filepath
				filepath = path
				os.mkdir(path)	
				path2 = path +"/1_PREPROD/11_SANDBOX"
				os.makedirs(path2)
				path2 = path +"/1_PREPROD/12_STORYBOARD"
				os.makedirs(path2)
				path2 = path +"/1_PREPROD/13_PREVIS/131_2D"
				os.makedirs(path2)
				path2 = path +"/1_PREPROD/13_PREVIS/132_3D"
				os.makedirs(path2)
				path2 = path +"/1_PREPROD/14_REFERENCES"
				os.makedirs(path2)
				path2 = path +"/1_PREPROD/15_MASTERS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/21_SANDBOX"
				os.makedirs(path2)
				path2 = path +"/2_PROD/22_MODELING/221_CHARACTERS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/22_MODELING/222_PROPS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/22_MODELING/223_SETS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/23_RIGG/231_CHARACTERS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/23_RIGG/232_PROPS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/23_RIGG/233_SETS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/24_LAYOUT/241_SHOTS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/25_ANIMATION/251_SHOTS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/26_FX/261_FLUIDS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/26_FX/262_FPARTICLES"
				os.makedirs(path2)
				path2 = path +"/2_PROD/26_FX/263_HAIR_FUR"
				os.makedirs(path2)
				path2 = path +"/2_PROD/26_FX/264_DYNAMICS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/26_FX/265_OTHERS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/27_EXPORT/271_MESH"
				os.makedirs(path2)
				path2 = path +"/2_PROD/27_EXPORT/272_SHADERS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/27_EXPORT/273_MISC"
				os.makedirs(path2)
				path2 = path +"/2_PROD/28_RENDER/281_SHOTS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/28_RENDER/282_CHARA"
				os.makedirs(path2)
				path2 = path +"/2_PROD/28_RENDER/283_PROPS"
				os.makedirs(path2)
				path2 = path +"/2_PROD/28_RENDER/284_SETS"
				os.makedirs(path2)
				path2 = path +"/3_POSTPROD/31_COMP"
				os.makedirs(path2)
				path2 = path +"/3_POSTPROD/32_EDIT"
				os.makedirs(path2)
				path2 = path +"/3_POSTPROD/33_SOUND"
				os.makedirs(path2)
				path2 = path +"/4_INPUT/41_TEXTURES"
				os.makedirs(path2)
				path2 = path +"/4_INPUT/41_TEXTURES/411_CHARACTERS"
				os.makedirs(path2)
				path2 = path +"/4_INPUT/41_TEXTURES/412_PROPS"
				os.makedirs(path2)
				path2 = path +"/4_INPUT/41_TEXTURES/413_SETS"
				os.makedirs(path2)
				path2 = path +"/4_INPUT/42_STOCKSHOTS"
				os.makedirs(path2)
				path2 = path +"/4_INPUT/43_OTHERS"
				os.makedirs(path2)
				path2 = path +"/5_DATA/501_CACHES/5011_CLOTH"
				os.makedirs(path2)
				path2 = path +"/5_DATA/501_CACHES/5012_LIGHT"
				os.makedirs(path2)
				path2 = path +"/5_DATA/501_CACHES/5013_GEO/SHOTS"
				os.makedirs(path2)
				path2 = path +"/5_DATA/501_CACHES/5014_FLUID"
				os.makedirs(path2)
				path2 = path +"/5_DATA/501_CACHES/5015_DISK"
				os.makedirs(path2)
				path2 = path +"/5_DATA/501_CACHES/5016_N"
				os.makedirs(path2)
				path2 = path +"/5_DATA/501_CACHES/5017_ABC"
				os.makedirs(path2)
				path2 = path +"/5_DATA/502_AUTOSAVES"
				os.makedirs(path2)
				path2 = path +"/5_DATA/503_3DPAINT"
				os.makedirs(path2)
				path2 = path +"/5_DATA/504_THRASH"
				os.makedirs(path2)
				path2 = path +"/5_DATA/505_FUR/5051_ATTRIBUTES"
				os.makedirs(path2)
				path2 = path +"/5_DATA/505_FUR/5052_SHADOW"
				os.makedirs(path2)
				path2 = path +"/5_DATA/505_FUR/5053_EQ"
				os.makedirs(path2)
				path2 = path +"/5_DATA/505_FUR/5054_IMAGES"
				os.makedirs(path2)
				path2 = path +"/5_DATA/505_FUR/5055_FILES"
				os.makedirs(path2)
				path2 = path +"/5_DATA/506_MR"
				os.makedirs(path2)
				path2 = path +"/5_DATA/507_SHADERS"
				os.makedirs(path2)
				path2 = path +"/5_DATA/508_IPR"
				os.makedirs(path2)
				path2 = path +"/5_DATA/509_DEPTH"
				os.makedirs(path2)
				path2 = path +"/5_DATA/510_PARTICLES"
				os.makedirs(path2)
				path2 = path +"/5_DATA/511_SCRIPTS"
				os.makedirs(path2)
				path2 = path +"/5_DATA/512_REFEDITS/SHOTS"
				os.makedirs(path2)
				path2 = path +"/5_DATA/513_XGEN"
				os.makedirs(path2)
				path2 = path +"/6_OUTPUT/61_MAYA"
				os.makedirs(path2)
				path2 = path +"/6_OUTPUT/62_PLAYBLAST"
				os.makedirs(path2)
				path2 = path +"/6_OUTPUT/63_COMP/631_SHOTS"
				os.makedirs(path2)
				path2 = path +"/6_OUTPUT/64_SEQUENCES"
				os.makedirs(path2)
				path2 = path +"/6_OUTPUT/65_PREVIS"
				os.makedirs(path2)
				path2 = path +"/6_OUTPUT/66_MASTER"
				os.makedirs(path2)
				refreshScrollListAfterNewProject(listFic)

			
		if cmds.menuBarLayout('Barre', query = True, exists= 1) == False:
		    #Create the menuBarLayout if it doesn't exist
			cmds.menuBarLayout('Barre',bgc = [1,1,1])
			cmds.menu('Shamepipe',tearOff=True)
			cmds.menuItem( label = "Close Window", command = 'cmds.deleteUI(fenetre)')
			cmds.menu('STEP by STEP')
			cmds.menu('Tools')
			cmds.menu('Preferences')
			cmds.menu('Help',helpMenu=True)
			cmds.setParent('..')
			cmds.columnLayout("mainColumn", columnAttach=('both', 5), columnWidth = 300, h=600, adjustableColumn=True, preventOverride = False)
			cmds.menuItem('User preferences',command=PrefUserWindow().UserWindow, parent="Preferences")
			cmds.rowLayout(numberOfColumns=2,columnAlign1 = "center")
			cmds.image(image='C:\Maya_Preferences\logo.png')
			cmds.setParent('..')
			repCourant = cmds.text("repCourant",label = self.filepath,backgroundColor = [0.75,0.75,0.75],h=20)
			cmds.rowLayout(numberOfColumns=3, height = 200)
		
		    #Open the path to the selected Item and refresh lists
			def AccessDir(listFic):# Permet d acceder aux sous-repertoire du repertoire selectionner.
				global filepath
				global dirs
				global fics
				someList = cmds.textScrollList("listRep", q=1, si=1)
				scrollList = cmds.textScrollList(listFic,edit=True,removeAll=True)
				while filepath[-1]=="/":
					split = filepath.rsplit("/",1)
					filepath = split[0]
				
				listDir = cmds.textScrollList("listRep",q=True,allItems=True)
				for i in listDir:
					if i == os.path.basename(filepath):
						filepath = filepath.rsplit(i,1)[0]
				c=0
				for i in os.listdir(filepath):
					if os.path.exists(filepath+'/'+i+"/"):
						c=1
						break
				if c==0:
					split = filepath.rsplit("/",1)
					filepath = split[0]
					
				filepath = filepath+ "/" + someList[0]+ "/"
				dirs = []
				fics = []
				c=-1
				ndir = 0
				for i in os.listdir(filepath):
					if os.path.exists(filepath+'/'+i+"/"):
						ndir = 1
						break
						
				if ndir == 1:
					scrollList = cmds.textScrollList("listRep",edit=True,removeAll=True)
					done = False
					for i in os.listdir(filepath):
						c=c+1
						if os.path.exists(filepath+'/'+i+"/"):
							if (os.path.exists(filepath+'/'+i+"/Versioning") or os.path.exists(filepath+'/'+i+"/versioning") or os.path.exists(filepath+'/'+i+"/Versions")) :
								fics.append(i)
								if done == False:
									for i in os.listdir(filepath + "/../"):
										dirs.append(i)
									done = True
							else:
								dirs.append(i)
						else:
							fics.append(i)
				else:
					for i in os.listdir(filepath):
						fics.append(i)
					split = filepath.rsplit(someList[0],1)
					filepath = split[0] + someList[0] + "/"
				
				scrollList = cmds.textScrollList("listRep",edit=True,append=dirs)
				scrollList = cmds.textScrollList(listFic,edit=True,append=fics)
				cmds.text("repCourant",edit=True,label = filepath)
				
			self.listRep = cmds.textScrollList('listRep',allItems=True,backgroundColor = (1,1,1),append=self.dirs,width=240,sc=partial(AccessDir, 'listFic'))	
			self.listFic = cmds.textScrollList('listFic',allItems=True,backgroundColor = (1,1,1), append=self.fics,width=240)	

			self.listFic = cmds.textScrollList(self.listFic, e=True, sc=partial(self.clickOnListFic))
			
			cmds.menuItem( label = "New Project", p = "Shamepipe", command = partial(createNewProject, self.listFic))
			cmds.menuItem( label = "Open Project", p = "Shamepipe", command = partial(self.openProject, self.listFic, False))
			
			cmds.columnLayout(adjustableColumn=True, preventOverride = False)
			cmds.rowLayout(numberOfColumns=1)
			cmds.image("tampon",image='',width=246,h=126)
			cmds.setParent('..')
			cmds.rowLayout(numberOfColumns=1, h = 25)

			cmds.optionMenu("listVersion",w=246, cc = self.versionSelectedChange)
			cmds.setParent('..')
			cmds.rowLayout(numberOfColumns=1)
			cmds.text("versionInfo",label = "",h=30,backgroundColor=[0.75,0.75,0.75],width = 240)
			cmds.setParent("..")
			cmds.setParent('..')
			cmds.setParent('..')
			cmds.rowLayout(numberOfColumns=3)
			cmds.columnLayout(columnAttach=('left',5), adjustableColumn=False, preventOverride = False, width = 240)
			cmds.rowLayout(numberOfColumns=3)
			
			#Open the parent directory of the current directory (it can't go back before the entry point)
			def modif(a): # Vide la textScrollList et ajoute les nouveaux elements
				global filepath
				global dirs
				global fics
				cmds.textScrollList("listRep",edit=True,removeAll=True)
				cmds.textScrollList("listFic",edit=True,removeAll=True)
				cmds.image("tampon", edit=True, vis = False, image='', width=246, h=126)
				nbMenuItemOptionMenu = cmds.optionMenu('listVersion', q=True, ni=True)
				if nbMenuItemOptionMenu > 0:
					menuItems = cmds.optionMenu('listVersion', q=True, itemListLong=True) # itemListLong returns the children
					if menuItems:
						cmds.deleteUI(menuItems)
				while filepath[-1] == '/':
					split = filepath.rsplit('/',1)
					filepath = split[0]
				split = filepath.rsplit('/',1)
				filepath=split[0]+'/'
				dirs = []
				fics = []
				c=-1
				for i in os.listdir(filepath):
					c=c+1
					if os.path.exists(filepath+os.listdir(filepath)[c]+"/"):
						dirs.append(i)
					else:
						fics.append(i)
				cmds.textScrollList("listRep",edit=True,append=dirs)
				cmds.textScrollList("listFic",edit=True,append=fics)
				cmds.text("repCourant",edit=True,label = filepath)
			
			#Open the version selected in the OptionMenu
			def OpenVersion(a):
				global filepath
				try:
					fileSelected = cmds.optionMenu("listVersion",q=True,v=True)
					fileSelected = str(fileSelected)
					projectSelected = cmds.textScrollList("listFic", query=True, si=1 )[0]
					position = fileSelected.index(".ma")
					if os.path.exists(filepath + str(projectSelected) + "/Versioning/"):
						fileSelected = filepath + str(projectSelected) + "/Versioning/" + fileSelected
					elif os.path.exists(filepath + str(projectSelected) + "/Versions/"):
						fileSelected = filepath + str(projectSelected) + "/Versions/" + fileSelected
					print "fileSelected = "+fileSelected
					cmds.file(fileSelected,force=True, o=True,type="mayaAscii")
					cmds.confirmDialog(title="Confirm",message="File open successfully !")
				except:
					cmds.confirmDialog( title='Warning !', message='Please, select a ".ma" file')
			
			#Create a directory inside the current directory and add it to the left textScrollList
			def createDir(a):
				global filepath
				listDir = []
				for i in os.listdir(filepath):
					if re.search("^\d+_",str(i)) != None:
						listDir.append(i)
				listDir.sort()
				splitName = re.split("(^\d+_)",listDir[-1])
				print splitName
				splitName = re.split("(_)",splitName[1])
				print splitName			
				numberFile = int(splitName[0])
				numberFile=numberFile+1
				splitName[0] = str(numberFile)
					
				
				def createAndDelete(splitName,a):
					global filepath
					dirName = cmds.textField("dirName",q=1,tx=1)
					dirName = splitName[0] + "_" + str(dirName)
					print filepath+"/"+dirName
					os.mkdir(filepath+"/"+dirName)
					cmds.textScrollList("listRep",e=True,append=dirName)
					cmds.deleteUI("CreateDirectory")
					
				cmds.window("CreateDirectory",title="Create Directory",s=False, rtf = False)
				cmds.columnLayout()
				cmds.text("Entrer le nom du repertoire a creer : ")
				dirName = splitName[0]
				cmds.textField("dirName",w=240)
				cmds.rowLayout(numberOfColumns=1)
				cmds.button("OK",command=partial(createAndDelete,splitName))
				cmds.showWindow("CreateDirectory")
				
			#Delete the directory selected in the left textScrollList and remove it of the list
			def removeDir(a):
				global filepath
				selectedItem = cmds.textScrollList("listRep",q=True,si=True)
				selectedItem = selectedItem[0]
				cmds.window("Confirm",rtf=True,s=False)
				cmds.columnLayout(h=30)
				cmds.rowLayout(numberOfColumns=1,h=30)
				cmds.text(label="Voulez-vous vraiment supprimer ce repertoire ?")
				cmds.setParent("..")
				cmds.rowLayout(numberOfColumns=2)
				
				def deleteConfirm(selectedItem,a):
					global filepath
					print("filepath = "+filepath)
					shutil.rmtree(filepath)
					while filepath[-1] == "/":
						split = filepath.rsplit('/',1)
						filepath = split[0]
					split = filepath.rsplit('/',1)
					filepath = split[0]
					cmds.textScrollList("listRep",e=True,removeItem = selectedItem)
					cmds.textScrollList("listFic",e=True,removeAll = True)
					cmds.deleteUI("Confirm")
					
				cmds.button("YES",command=partial(deleteConfirm,selectedItem))
				cmds.button("NO",command='cmds.deleteUI("Confirm")')
				cmds.showWindow("Confirm")
				
			#Create a scene and add it to the right textScrollList
			def createScene(a):
				global filepath
				name = ""
				cmds.window("CreateScene",title="Create a scene",rtf=True,s=False)
				cmds.columnLayout()
				cmds.rowLayout(numberOfColumns=2)
				cmds.text(label=filepath+"_")
				cmds.textField("sceneName")
				cmds.setParent("..")
				
				def creationConfirm(a):
					global filepath
					name = cmds.textField("sceneName",q=True,tx=True)
					name = "_"+str(name)
					os.makedirs(filepath+name+"/Versioning/")
					cmds.textScrollList("listFic",e=True,append=name)
					cmds.deleteUI("CreateScene")

				cmds.button(label="OK",c=creationConfirm)
				cmds.showWindow("CreateScene")
			
			#Delete a scene and all its versions and remove it from the right textScrollList
			def removeScene(a):
				selectedItem = cmds.textScrollList('listFic',q=True,si=True)
				selectedItem=selectedItem[0]
				cmds.window("ConfirmRemove",title="Confirm Remove",s=False,rtf=True)
				cmds.columnLayout()
				cmds.text(label="Confirmez-vous la suppression de cette scene ?")
				def removeConfirm(selectedItem,a):
					print filepath+selectedItem
					if(os.path.isfile(filepath+selectedItem) == True):
						os.remove(filepath+selectedItem)
					else:
						shutil.rmtree(filepath+selectedItem)
					cmds.textScrollList("listFic",e=True,removeItem = selectedItem)
					cmds.text("versionInfo",e=True,label="")
					cmds.deleteUI("listVerison")
					cmds.deleteUI("ConfirmRemove")
				cmds.button("YES",command=partial(removeConfirm,selectedItem))
				cmds.button("NO",command='cmds.deleteUI("ConfirmRemove")')
				cmds.showWindow("ConfirmRemove")
				
			cmds.button('  <  ',command=modif)
			cmds.button(label='  +  ',command=createDir)
			cmds.button(label=' - ',command=removeDir)
			cmds.setParent('..')
			cmds.setParent('..')
			cmds.columnLayout(columnAttach=('left',5),adjustableColumn=False, preventOverride = False, width = 240)
			cmds.rowLayout(numberOfColumns=2)
			cmds.button(label='  +  ',command=createScene)
			cmds.button(label=' - ',command=removeScene)
			cmds.setParent('..')
			cmds.setParent('..')
			cmds.rowLayout(numberOfColumns=1)
			cmds.button('Open Version',width=246,backgroundColor=[0,1,0],command=OpenVersion)
			cmds.setParent('..')
			cmds.setParent('..')
			cmds.rowLayout(numberOfColumns=1)
			cmds.text("Toggle Current File Infos/Versions :",backgroundColor = (0.95,0.95,0.95),width = 720,h=20,font = "plainLabelFont")
			cmds.setParent('..')
			cmds.rowLayout(numberOfColumns=2)
			cmds.textScrollList("infos",enable = False,backgroundColor=(1,1,1),width=481,append="Informations are displayed here")
			cmds.image(image="",width = largeur-515)
			cmds.setParent('..')
			cmds.rowLayout(numberOfColumns=3)

			def screenshotViewport(filepathToSave, fileName):
				#Grab the last active 3d viewport
				view = apiUI.M3dView.active3dView()

				#read the color buffer from the view, and save the MImage to disk
				image = api.MImage()
				
				#view.readColorBuffer(image, True)     #Doesn't work because of viewport2 
				if view.getRendererName() == view.kViewport2Renderer:      
					image.create(view.portWidth(), view.portHeight(), 4, api.MImage.kFloat)
					view.readColorBuffer(image)
					image.convertPixelFormat(api.MImage.kByte)
					print "viewPort2"
				else:
					view.readColorBuffer(image)
					print "old viewport !"
				image.writeToFile(filepathToSave + fileName +".png", 'png')
			
			#Save the current scene and gives it a version number
			def versioning(a):
				global filepath
				sourceListFic = cmds.textScrollList("listFic", query=True, si=1 )
				filepathTmp = filepath + str(sourceListFic[0])
				try:
					filepathCurrent = cmds.file(q=True, sn=True)
					print "filepathCurrent = "+filepathCurrent
					print "sourceListFic = "+sourceListFic[0]
					filename = ""
					if len(filename) == 0:
						filename = str(sourceListFic[0])[1:]

					dirs = os.listdir(filepathTmp)
				except:
					cmds.confirmDialog( title='Warning !', message='Please, create or select a ShamePipe project.')   
					return
				
				puw = PrefUserWindow()
				name = puw.namePref.upper()
				firstname = puw.firstnamePref.upper()
				print "filename = "+filename
				
				if(re.search("/Versioning/$",filepathTmp) != None):
					print("Nous sommes bien dans Versioning")
				elif(re.search("/Versions/$",filepathTmp) != None):
					print("Nous sommes bien dans Versioning")
				else:
					z=0
					for document in dirs:
						if document == "Versioning":
							z=1
							break
						if document == "Versions":
							z=2
							break
					if z == 0:
						os.mkdir(filepathTmp+"/Versioning/")
					if z == 1:
						filepathTmp = filepathTmp + "/Versioning/"
					elif z == 2:
						filepathTmp = filepathTmp + "/Versions/"
						
				filenamebis = filename.split(".")
				nv = ""
				
				
				print "filenamebis[0] : " + filenamebis[0]
				
				if(re.search("_[Vv]\d+",filenamebis[0]) != None):
					filenamebis = re.split("(_[Vv]\d+)",filenamebis[0])
					print filenamebis
					nv = re.split("(\d+)",filenamebis[1])
					intNv = int(nv[1])
					intNv = intNv+1
					nv = nv[0]+str(intNv)
					c=0
					while c==0:
						c=1
						for i in os.listdir(filepathTmp):
							if re.search("^"+filenamebis[0]+ nv,i):
								intNv = intNv+1
								nv = "_v"+str(intNv)
								print "new filenamebis = "+str(filenamebis[0])
								c=0
								break

				else:
					c=1
					d=0
					dirs = os.listdir(filepathTmp)
					intNv= 1

					for i in range(len(dirs)):
						strFileToCompare = str(dirs[i])
						fileToCompare = strFileToCompare[:strFileToCompare.index(".") - 3]
						if fileToCompare == (filename + "_v" + str(intNv)):
							c=c+1
							intNv = intNv + 1
					filenamebis[0] = filename
					nv = "_v" + str(intNv)
				
				screenshotViewport(filepathTmp, filenamebis[0]+ nv + "_" + firstname[0] + name[0])
				filenamebis[0] = filenamebis[0]+ nv + "_" + firstname[0] + name[0] + ".ma"
				#Check if "Versioning" folder exist !
				filepathTmp = filepathTmp + filenamebis[0]
				cmds.file(rename=filepathTmp)
				cmds.file(save=True, type="mayaAscii")
				# Update optionMenu listVersion
				ShamePipeWindow().clickOnListFic()
				cmds.confirmDialog( title='Confirm', message='New version saved : ' + str(filenamebis[0]), button=['Ok'], defaultButton='Ok', dismissString='Ok' )
				
			#Save the current file
			def saveM(a):
				fileOpen = cmds.file(q=True,sn=True)
				print"filename = "+fileOpen
				cmds.file(save=True, type="mayaAscii",force=True)
				

			sversion = cmds.button('Save Version', command = versioning,backgroundColor=[0,1,0],width = 240)
			smaster = cmds.button('Save Master', command = saveM,backgroundColor=[1,0,0],width = 240)
			screenshot = cmds.button('Say cheeeeeese :]',command = '',width = 246)
			existence = cmds.window(fenetre,query=True,exists=1)
			if(existence == True):
				cmds.showWindow(fenetre)

	def __init__(self):
		self.dirs = []
		self.fics = []
		self.listRep = None
		self.listFic = None
		global filepath
		self.filepath = filepath
		self.createAndShowWindow("AGT_Prod_Manager")

if __name__== "__main__":
	
	global windowCreated
	windowCreated = False
	fenetre = None
	if cmds.window('AGT_Prod_Manager', exists=True):
		cmds.deleteUI('AGT_Prod_Manager', window=True)
		fenetre = cmds.window('AGT_Prod_Manager', backgroundColor = [0.25,0.25,0.25],maximizeButton = False,resizeToFitChildren = True,menuBar = True, sizeable = False)
	elif cmds.windowPref('AGT_Prod_Manager', exists=True):
		cmds.windowPref('AGT_Prod_Manager', remove=True)
		fenetre = cmds.window('AGT_Prod_Manager', backgroundColor = [0.25,0.25,0.25],maximizeButton = False,resizeToFitChildren = True,menuBar = True, sizeable = False)

	if (os.path.exists("C:/Maya_Preferences/Shamepipe_Preferences.txt")):
		spw = ShamePipeWindow()
	else:
		puw = PrefUserWindow()
	existence = cmds.window(fenetre,query=True,exists=1)
	if(existence == True):
		cmds.showWindow(fenetre)
		windowCreated = True