from pathlib import Path
import time
import os
import base64
import gzip
import xml.etree.ElementTree as ET

def xor(string: str, key: int) -> str:
	return ("").join(chr(ord(char) ^ key) for char in string)

def decrypt_data(data: str) -> str:
	base64_decoded = base64.urlsafe_b64decode(xor(data, key=11).encode())
	decompressed = gzip.decompress(base64_decoded)
	return decompressed.decode()

def getUnqiuePath(path) -> Path:
    filename, extension = os.path.splitext(path)
    counter = 2
    while os.path.exists(path):
        path = "{} ({}){}".format(filename, counter, extension)
        counter += 1

    return Path(path)

files: list[Path]
createSubs: bool
print("-"*100)
print("Welcome to GMDMassExport!\nthis script lets you export all your editor levels to gmd files!! pretty awesome")
print("-"*100)
print("Please enter the path to the folder that contains the CCLocalLevels.dat files\n(hint: it's ok if those files are in multiple folders inside this parent folder!)")

while True:
	folder_path = Path(input("Folder Path: "))
	if folder_path.exists() and folder_path.is_dir():
		files = list(folder_path.rglob("CCLocalLevels.dat"))
		if len(files) < 1:
			print("This folder and it's subfolders do not contain any CCLocalLevels.dat files, please try again...")	
		else:
			break
	elif not folder_path.is_dir():
		print("This path is not a folder! make sure you are entering a folder directory and NOT the path to a .dat file, then try again...")
	else:
		print("This path does not exist, make sure you entered it correctly and try again...")

while True:
	ok = input("Found {} CCLocalLevels.dat(s)!\nDo you want to sort the exported .gmd files to folders based on date (instead of 1 big folder)? (Y/n): ".format(len(files)))
	if ok.upper() == "Y" or ok.upper() == "YES" or ok == "":
		createSubs = True
		break
	elif ok.upper() == "N" or ok.upper() == "NO":
		createSubs = False
		break
	else:
		print('Invalid input. Please enter either "Y" or "N".')

while True:
	ok = input("Start exporting? (Y/n):")
	if ok.upper() == "Y" or ok.upper() == "YES" or ok == "":
		break
	elif ok.upper() == "N" or ok.upper() == "NO":
		input("Press any key to exit...")
		exit()
	else:
		print('Invalid input. Please enter either "Y" or "N".')

print("-"*100)
print("Starting exports...")
print("-"*100)

output_path = Path.cwd() / "GMD Exports"
Path.mkdir(output_path, parents=True, exist_ok=True)

for file in files:
	if file.is_file():
		folder_path = output_path / time.strftime("%Y-%m-%d %H-%M-%S", time.gmtime(os.path.getmtime(file))) if createSubs else output_path
		Path.mkdir(folder_path, parents=True, exist_ok=True)

		root = ET.fromstring(decrypt_data(file.read_text()))
		file_dict = root.find("dict")

		if file_dict is not None and file_dict.findtext("k") == "LLM_01":
			llm_01 = file_dict.find("d")

			if llm_01 is not None:
				level_count = 1

				for level in llm_01.findall("d"):
					root = ET.Element("plist", {"version": "1.0", "gjver": "2.0"})
					gmd = ET.SubElement(root, "dict")
					next_is_name = False
					name = ""
					for elem in level.iter():
						if next_is_name == True:
							txt = elem.text
							if txt is not None:
								name = txt + ".gmd"
							next_is_name = False
						elif elem.text == "k2":
							next_is_name = True
						
						gmd.append(elem)
					if name == "":
						name = "level_" + str(level_count) + ".gmd"

					gmd_file = getUnqiuePath(folder_path / name)
					gmd_file.write_bytes(b'<?xml version="1.0"?>' + ET.tostring(root, encoding="utf-8"))
					print("Successfully exported {}!".format(gmd_file.name))

print("-"*100)
print("Finished Exporting!! Good bye")
print("-"*100)
input("Press any key to exit...")