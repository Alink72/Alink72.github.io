
from flask import Flask, request, render_template, send_file, redirect, url_for
import os
from function import ReadFile, ReadRunoff, CaluFlow, paipin, chazhi,tiaojieliuliang
import os
from flask import Flask, request, render_template, send_file, redirect, url_for
import pandas as pd


import os
from flask import Flask, request, render_template, send_file, redirect, url_for
import pandas as pd
  # 确保你的函数在同目录下


import os
from flask import Flask, request, render_template, send_file, redirect, url_for
import pandas as pd


app = Flask(__name__)
# 使用绝对路径指向与项目根目录平行的data文件夹
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
UPLOAD_FOLDER = os.path.join(PROJECT_DIR, 'data')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    tables = None
    download_link = False
    high_water_level = ''

    if request.method == 'POST':
        if 'files[]' in request.files:
            files = request.files.getlist('files[]')
            for file in files:
                file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            return redirect(url_for('index'))
        elif 'run_function' in request.form:
            high_water_level = request.form['high_water_level']
            files = os.listdir(UPLOAD_FOLDER)
            if not files:
                error_message = "No files found in the data folder. Please upload files first."
            else:
                try:
                    df = tiaojieliuliang(high_water_level)
                    df.to_excel(os.path.join(UPLOAD_FOLDER, 'output.xlsx'), index=False)
                    tables = df.to_html(classes='data', index=False)
                    download_link = True
                except Exception as e:
                    error_message = str(e)

    return render_template('index.html', tables=tables, download_link=download_link, error=error_message, high_water_level=high_water_level)

@app.route('/download')
def download_file():
    return send_file(os.path.join(UPLOAD_FOLDER, 'output.xlsx'), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

