import requests
import os
import zipfile
import io
import shutil
import json


symbols_url = "https://gitlab.com/kicad/libraries/kicad-symbols/-/archive/master/kicad-symbols-master.zip"
footprints_url = "https://gitlab.com/kicad/libraries/kicad-footprints/-/archive/master/kicad-footprints-master.zip"
shapes_url = "https://gitlab.com/kicad/libraries/kicad-packages3D/-/archive/master/kicad-packages3D-master.zip"


def get_file_data(url):
	f = os.path.basename(url)
	if os.path.exists(f):
		with open(f, 'rb') as f:
			return f.read()
	r = requests.get(url)
	with open(f, 'wb') as f:
		f.write(r.content)
	return r.content


version = open('VERSION').read().strip()

shutil.rmtree('build', ignore_errors=True)
os.mkdir('build')

d = get_file_data(symbols_url)
z = zipfile.ZipFile(io.BytesIO(d))

package_index_json = {}

for file in z.filelist:
	fname = file.filename
	if not fname.endswith(".kicad_sym"):
		continue
	name = fname.replace("kicad-symbols-master/", "").replace(".kicad_sym", "")

	print("name", name)
	with z.open(fname) as zf:
		build_zip_path = f"build/kicad_lib_symbols_{name}-v{version}.zip"
		print(build_zip_path)
		with zipfile.ZipFile(build_zip_path, 'w') as out_zip:
			out_zip.writestr("symbols/" + name + ".kicad_sym", zf.read())

		package_index_json[f"kicad_lib_symbols_{name}"] = {
			"owner": "kicad_contributors",
			"homepage": "https://github.com/danroblewis/kicad-eurorack-tools",
			"releases": [
				{
					"version": version,
					"artifact_url": f"https://github.com/danroblewis/kpm-kicad-libraries/releases/download/v{version}/{build_zip_path.replace('build/','')}",
					"author": "kicad_contributors",
					"dependencies": {}
				}
			]
		}

with open('registry_additions.json', 'w') as f:
	f.write(json.dumps(package_index_json, indent=4))
