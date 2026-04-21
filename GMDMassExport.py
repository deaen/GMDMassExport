from pathlib import Path
from time import gmtime, strftime
from os.path import getmtime
from base64 import urlsafe_b64decode
from gzip import decompress
from platform import system
from Crypto.Cipher import AES
import xml.etree.ElementTree as ET

def xor(string: str, key: int) -> str:
	return ("").join(chr(ord(char) ^ key) for char in string)

def decrypt_data(data: str) -> str:
	base64_decoded = urlsafe_b64decode(xor(data, key=11).encode())
	decompressed = decompress(base64_decoded)
	return decompressed.decode()

KEY = (
    b"\x69\x70\x75\x39\x54\x55\x76\x35\x34\x79\x76\x5d\x69\x73\x46\x4d"
    b"\x68\x35\x40\x3b\x74\x2e\x35\x77\x33\x34\x45\x32\x52\x79\x40\x7b"
)

def remove_pad(data: bytes) -> bytes:
    last = data[-1]
    if last < 16:
        data = bytes(data[--last])
    return data

def mac_decrypt(data: bytes) -> str:
    cipher = AES.new(KEY, AES.MODE_ECB)
    return remove_pad(cipher.decrypt(data)).decode()

def getUniquePath(path_str) -> Path:
	path = Path(path_str)
	counter = 2
	while path.exists():
		path = Path("{} ({}){}".format(path.with_suffix(""), counter, path.suffix))
		counter += 1

	return path

files: list[Path]
createSubs: bool
total_level_count = 0

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
		folder_path = output_path / strftime("%Y-%m-%d %H-%M-%S", gmtime(getmtime(file))) if createSubs else output_path
		Path.mkdir(folder_path, parents=True, exist_ok=True)

		root = ET.fromstring(decrypt_data(file.read_text()) if system() != "Darwin" else mac_decrypt(file.read_bytes()))
		file_dict = root.find("dict")

		if file_dict is not None and file_dict.findtext("k") == "LLM_01":
			llm_01 = file_dict.find("d")

			if llm_01 is not None:

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
					gmd_file = getUniquePath(folder_path / name)
					gmd_file.write_bytes(b'<?xml version="1.0"?>' + ET.tostring(root, encoding="utf-8"))
					print("Successfully exported {}!".format(gmd_file.name))
					total_level_count += 1

print("-"*100)
print("exported {} levels!! have fun good bye".format(total_level_count))
print("-"*100)
input("Press any key to exit...")