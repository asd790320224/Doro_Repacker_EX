# Overview:
nikke mod repack tool, supports many types of mods

==============================================================================================================================================================================

# New Features & Improvements

## 1.0:

### New Features:
	+ repack burst/lobby mod and event mod
### workflow change:
	+ No need to copy mods to "Modded Bundles_Rename Step" folder anymore.
	+ No need to create shortcut for NAU.exe anymore.
	+ change name format for lobby/burst mod to format when using NLBMM.
	+ Can repack multiple character mods, lobby/burst mods, event mods in one run.
### other changes:
	+ added feature to sort mods by name.
	+ Original mod files are categorized and moved to the correct folder:
		- aim/cover/standing: "Original Bundles".
		- lobby/burst: "Original lobby burst bundles".
		- event: "Original event bundles".
	+ Changed how original mod bundles are found and named ("Modded Bundles_Rename Step" and "Renamed Bundles for Match" are no longer needed).
	+ remove: "B___rename_moddedbundles_renamestep.py", "C___move_renamestepfiles_to_renamedbundlesformatch.py", "D___copy_raw_files_matches_to_originalbundles_showprogress.py" their work will be done by "X__GetRawFile.py".
	+ add "1.2_OPTIONAL_CLEAN_FOLDERS.bat" which will run run "OPTIONAL___clean_folders.py"
	+ rename some scripts

## 1.1:

### New Features:
	+ ability to repack most mod if they have assets of type: "AudioClip", "TextAsset", "Texture2D" and they are lookupable in "catalog_db.json" and "core_other.json" except "swap" mod
### other changes:
	+ remove some files that are no longer needed
### test status:
	+ Audio mod (does not exist yet): Using the same file as the original, extracted the audio file and imported it back successfully. file using is "18159e11839d82bba18deb7b138fa58d.bundle".
	+ spine physics mod (does not exist yet): Using the same file as the original, extracted the audio file and imported it back successfully. file using is "spinephysicssettings_assets_all.bundle".
	+ texture mod (all kinds of mods that change only texture): untested but it should work.
	+ other types of mods: not tested yet.


## 1.1:

### New Features:
	+ packed into one exe file, now you don't need to install anything for the tool to work
### other changes:
	+ add .exe build instructions

==============================================================================================================================================================================



# how to use:
## SETUP:

!!!!!!NOTE: If you just want to use the exe, skip this the setup.

Note 2: if your previous version of Doro_Repacker works, you can skip this step

Step 1: Get python
	+ dowload python: "https://www.python.org/downloads/" 
	+ Install like other programs just make sure to check "Add python.exe to PATH" otherwise you will have to add it manually.
Step 2: run SETUP_INSTALL_REQUIREMENTS.bat

## NAME FORMAT:

aim/cover/standing: 	[id]_[skin_code]_[type]_[Author]_[ModName]
lobby/burst: 		[id]-[skin_code]-[type]-[Author]-[ModName]
event:			[ID]-[type]-[Author]-[ModName]
other mod: 		use original file name or hash, can be looked up in "catalog_db.json" or "core_other.json", example:
				+ "0d23c5230bfd38b85478b293870cc1ef"
				+ "be5bf3a579d4ee9d7ee0dbd1a4e9e298.bundle"
				+ "assistcharacter_assets_as_robot_001_var.bundle"
				+ "spinephysicssettings_assets_all"

Don't confuse "-" and "_".
The naming structure is based on NMM for "aim/cover/standing" and NLBMM for "lobby/burst","event". If your mod loader doesn't use the above structure, you'll need to rename it yourself.
the naming for other mod 
The names of other mods are quite hard to find as a casual player, I want to make it simpler for some popular mods like "favorite item" but I'm not sure about their name format.

## USAGE:

# NOTE: 
tool designed to repack mods supported by NMM or NLBMM, it may not work with mods designed for other mod managers
!! this tools cant repack swap mod !!

### Use exe file

step 1: Put all repackable mods in the "Modded Bundles" folder
step 2: run "repacker.exe"

You will be asked if you want to delete temporary files (the "Repacked" folder will not be deleted), answer according to your needs, if you do not enter anything the program will skip the cleaning part. 
You can get your packed mod in the "Repacked" folder.

### Use python scripts

Make sure you have done all the setup steps.

step 1: Put all repackable mods in the "Modded Bundles" folder
step 2: run "1.0__GET_RAW_FILES.bat"
step 3: run "1.1__PY_RUN_REPACKER.bat"

After running "1.1__PY_RUN_REPACKER.bat", all repacked mods will be put into the "Repacked" folder.
If you want to delete all old data to prepare for the next repack, run: "1.2_OPTIONAL_CLEAN_FOLDERS.bat"


# build tutorial:

NOTE: You must first complete the setup steps including installing python and the required modules in requirements.txt before starting the build.

step 1: Open project folder: open project folder: if you use visual studio code then select file -> open folder open the folder containing mainScript.py

step 2: Install nuitka and its dependencies using the command: 

	pip install nuitka zstandard ordered-set

step 3: find your python installation directory, if you don't know where it is you can use the command:

	where python'

Copy the path to the folder containing the python.exe file (not including the .exe file)
warning: if you see multiple python paths it means you have multiple python versions, you must choose the correct version where you installed all modules before

step 3: replace "<your python installation directory>" with python path and run command:

nuitka --onefile --standalone --mingw64 --enable-plugin=tk-inter --assume-yes-for-downloads --include-package=UnityPy --include-package=UnityPy.resources --include-data-dir="<
your python installation directory>\Lib\site-packages\UnityPy\resources=UnityPy/resources" --include-data-dir="<
your python installation directory>\Lib\site-packages\archspec=archspec" --user-package-configuration-file=my.nuitka-package.config.yml mainScript.py

step 4: wait...around 30 minute.





