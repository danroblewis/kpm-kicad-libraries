import requests
import os
import zipfile
import io
import shutil
import json
#import py7zr

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

package_index_json = {}


# sevenzip_filters = [{"id": py7zr.FILTER_ARM}]
# sevenzip_filters = [{"id": py7zr.FILTER_COPY}]
# sevenzip_filters = [{"id": py7zr.FILTER_IA64}]
# sevenzip_filters = [{"id": py7zr.FILTER_PPMD}]
# sevenzip_filters = [{"id": py7zr.FILTER_ARMTHUMB}]
# sevenzip_filters = [{"id": py7zr.FILTER_CRYPTO_AES256_SHA256}]
# sevenzip_filters = [{"id": py7zr.FILTER_LZMA}]
# sevenzip_filters = [{"id": py7zr.FILTER_SPARC}]
# sevenzip_filters = [{"id": py7zr.FILTER_BROTLI}]
# sevenzip_filters = [{"id": py7zr.FILTER_DEFLATE}]
# sevenzip_filters = [{"id": py7zr.FILTER_LZMA2}]
# sevenzip_filters = [{"id": py7zr.FILTER_X86}]
# sevenzip_filters = [{"id": py7zr.FILTER_BZIP2}]
# sevenzip_filters = [{"id": py7zr.FILTER_DELTA}]
# sevenzip_filters = [{"id": py7zr.FILTER_POWERPC}]
# sevenzip_filters = [{"id": py7zr.FILTER_ZSTD}]


### Symbols

d = get_file_data(symbols_url)
z = zipfile.ZipFile(io.BytesIO(d))

for file in z.filelist:
	fname = file.filename
	if not fname.endswith(".kicad_sym"):
		continue
	name = fname.replace("kicad-symbols-master/", "").replace(".kicad_sym", "")

	print(name)
	with z.open(fname) as zf:
		build_zip_path = f"build/kicad_lib_symbols_{name}-v{version}.zip"
		with zipfile.ZipFile(build_zip_path, 'w', compression=zipfile.ZIP_LZMA) as out_zip:
			out_zip.writestr("symbols/" + name + ".kicad_sym", zf.read())

		# build_zip_path = f"build/kicad_lib_symbols_{name}-v{version}.7z"
		# with py7zr.SevenZipFile(build_zip_path, 'w', filters=sevenzip_filters) as out_zip:
		# 	out_zip.writestr(zf.read(), "symbols/" + name + ".kicad_sym")

		package_index_json[f"kicad_lib_symbols_{name}"] = {
			"owner": "kicad_contributors",
			"homepage": "https://gitlab.com/kicad/libraries/kicad-symbols",
			"releases": [
				{
					"version": version,
					"artifact_url": f"https://github.com/danroblewis/kpm-kicad-libraries/releases/download/v{version}/{build_zip_path.replace('build/','')}",
					"author": "kicad_contributors",
					"dependencies": {}
				}
			]
		}




### Footprints

d = get_file_data(footprints_url)
z = zipfile.ZipFile(io.BytesIO(d))

prettyfiles = {}

for file in z.filelist:
	fname = file.filename
	if '.pretty/' not in fname:
		continue
	if fname.endswith(".pretty/"):
		prettyfiles[fname] = []
		continue
	if not fname.endswith('.kicad_mod'):
		continue
	pfname = fname.split(".pretty/")[0] + '.pretty/'
	prettyfiles[pfname].append(fname)


for name, files in prettyfiles.items():
	name = name.replace("kicad-footprints-master/","").replace(".pretty/","")
	print(name)

	build_zip_path = f"build/kicad_lib_footprints_{name}-v{version}.zip"
	with zipfile.ZipFile(build_zip_path, 'w', compression=zipfile.ZIP_LZMA) as out_zip:
		for file in files:
			with z.open(file) as zf:
				parsed_file = file.replace("kicad-footprints-master/","")
				out_zip.writestr("footprints/" + parsed_file, zf.read())

	# build_zip_path = f"build/kicad_lib_footprints_{name}-v{version}.7z"
	# with py7zr.SevenZipFile(build_zip_path, 'w', filters=sevenzip_filters) as out_zip:
	# 	for file in files:
	# 		with z.open(file) as zf:
	# 			parsed_file = file.replace("kicad-footprints-master/","")
	# 			out_zip.writestr(zf.read(), "footprints/" + parsed_file)

		package_index_json[f"kicad_lib_footprints_{name}"] = {
			"owner": "kicad_contributors",
			"homepage": "https://gitlab.com/kicad/libraries/kicad-footprints",
			"releases": [
				{
					"version": version,
					"artifact_url": f"https://github.com/danroblewis/kpm-kicad-libraries/releases/download/v{version}/{build_zip_path.replace('build/','')}",
					"author": "kicad_contributors",
					"dependencies": {}
				}
			]
		}


### Write registry additions json

with open('registry_additions.json', 'w') as f:
	f.write(json.dumps(package_index_json, indent=4))
