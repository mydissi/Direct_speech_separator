
#from flask_material import Material


from flask import Flask, render_template, url_for, request, redirect, send_from_directory,abort
import os
import re
import codecs
from zipfile import ZipFile

app = Flask(__name__)

app.config["FILES"] = "..\direct\output"
app.config["FILES_UPLOAD"] = "..\direct\input"

def allowed(filename):
	if not "." in filename:
		return False
	ext = filename.rsplit(".", 1)[1]
	if ext == "txt":
		return True
	else:
		return False

@app.route('/',methods=["GET","POST"])
def index():
	rem = os.listdir(path="..\direct\output")
	for i in range(0, len(rem)):
		os.remove('..\direct\output\\' + rem[i])

	rem = os.listdir(path="..\direct\input")
	for i in range(0, len(rem)):
		os.remove('..\direct\input\\' + rem[i])

	if (request.method == "POST"):
		if request.files:
			if not allowed(request.files['file'].filename):
				print('forbidden extension')
				return redirect(request.url)

			file = request.files['file']
			file.save(os.path.join(app.config["FILES_UPLOAD"], file.filename))
			print('saved')
			path = '..\direct\input\\' + str(request.files['file'].filename)
			text = codecs.open(path, "r", encoding="utf-8", errors="ignore")
			text = text.read()
			file_name = str(request.files['file'].filename).rsplit(".", 1)[0]
			process(text,file_name)
			print('done')

			file_paths = []
			path1 = '..\direct\output\direct_'+file_name+'.txt'
			path2 = '..\direct\output\\non_direct_'+file_name+'.txt'
			path3 = '..\direct\output\outliers_' + file_name + '.txt'
			file_paths.append(path1)
			file_paths.append(path2)
			file_paths.append(path3)
			with ZipFile('..\direct\output\\result.zip', 'w') as zip:
				for file in file_paths:
					zip.write(file)
			return send_from_directory(app.config["FILES"],
								   filename = 'result.zip',
								   as_attachment=True)

	return render_template("index.html")

def process(text,file_name):
	d0, n0 = direct_non_direct_two_signs(text)

	text = cleaner(n0)

	# Прогоняет 5 раз по регексу
	res_direct = []
	res_non_direct = []

	d, n = direct_non_direct_two_signs(text)
	d1, n1 = direct_non_direct_two_signs(n)
	d2, n2 = direct_non_direct_two_signs(n1)
	d3, n3 = direct_non_direct_one_sign(n2)

	res_direct = d0 + d + d1 + d2 + d3
	res_non_direct = n3

	# Выдает 20 предположительных выбросов по длине
	text_outliers = get_outliers(res_direct)

	write_file_direct(res_direct, file_name)
	write_file_non_direct(res_non_direct, file_name)
	write_file_outlier(text_outliers, file_name)


def cleaner(text):
	text = '  ' + text
	text = text.replace(' . . . ', '...')
	text = text.replace(' . . .', '...')
	text = text.replace('\r', '')
	text = text.replace('"', "'")
	text = text.replace('--', '–')
	return text

# отделяем прямую от непрямой
def direct_non_direct_two_signs(text):
	direct = re.findall(r"(?:[^\w]{2})['\"«](.*?[.,;:!–?——])['\"»]", text)
	non_direct = re.sub(r"(?:[^\w]{2})['\"«](.*?[.,;:!–?——])['\"»]", '', text)
	return direct, non_direct

def direct_non_direct_one_sign(text):
	direct = re.findall(r"(?:[^\w]{1})['\"«](.*?[.,;:!–?——])['\"»]", text)
	non_direct = re.sub(r"(?:[^\w]{1})['\"«](.*?[.,;:!–?——])['\"»]", '', text)
	return direct, non_direct

def direct_non_direct_with_no_n(text):
	text = text.replace('\n', ' ')
	direct = re.findall(r"(?:[^\w]{1})['\"«](.*?[.,;:!–?——])['\"»]", text)
	non_direct = re.sub(r"(?:[^\w]{1})['\"«](.*?[.,;:!–?——])['\"»]", '', text)
	return direct, non_direct

def get_outliers(res_direct):
	lens = [len(res_direct[x]) for x in range(0, len(res_direct))]
	outliers = sorted(lens)[-20:]
	text_outliers = []
	for i in range(0, len(res_direct)):
		for j in range(0, len(outliers)):
			if (len(res_direct[i]) == outliers[j]):
				text_outliers.append(res_direct[i])
	return text_outliers

def write_file_direct(text, name):
	file_name = '..\direct\output\direct_{}.txt'.format(name)
	file = open(file_name, 'w+',errors="ignore")
	file.write(str(text[:]))
	file.close()

def write_file_non_direct(text, name):
	file_name = '..\direct\output\\non_direct_{}.txt'.format(name)
	file = open(file_name, 'w+',errors="ignore")
	file.write(text)
	file.close()

def write_file_outlier(text, name):
	file_name = '..\direct\output\outliers_{}.txt'.format(name)
	file = open(file_name, 'w+',errors="ignore")
	file.write(str(text[:]))
	file.close()

if __name__ == '__main__':
	app.run(debug=False)

