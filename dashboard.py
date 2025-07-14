from flask import Flask, render_template_string, request, send_file, redirect, url_for
import threading
import os
import main as scraper_main

app = Flask(__name__)

job_status = {'running': False, 'done': False, 'message': '', 'output_csv': '', 'output_json': ''}

def run_scraper(urls, dynamic, paginate, delay, proxies, config):
    job_status['running'] = True
    job_status['done'] = False
    job_status['message'] = 'Scraping in progress...'
    try:
        args = ["--urls"] + urls
        if dynamic:
            args.append("--dynamic")
        if paginate:
            args.append("--paginate")
        if delay:
            args += ["--delay", str(delay[0]), str(delay[1])]
        if proxies:
            args += ["--proxies", proxies]
        if config:
            args += ["--config", config]
        import sys
        sys.argv = ["main.py"] + args
        scraper_main.main()
        job_status['message'] = 'Scraping complete.'
        job_status['output_csv'] = 'output.csv'
        job_status['output_json'] = 'output.json'
    except Exception as e:
        job_status['message'] = f'Error: {e}'
    finally:
        job_status['running'] = False
        job_status['done'] = True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        urls = request.form['urls'].split()
        dynamic = 'dynamic' in request.form
        paginate = 'paginate' in request.form
        delay_min = float(request.form.get('delay_min', 1))
        delay_max = float(request.form.get('delay_max', 3))
        proxies = request.form.get('proxies_file') or None
        config = request.form.get('config_file') or None
        t = threading.Thread(target=run_scraper, args=(urls, dynamic, paginate, [delay_min, delay_max], proxies, config))
        t.start()
        return redirect(url_for('status'))
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Web Scraper Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f8f9fa; }
            .container { max-width: 600px; margin-top: 40px; }
            .form-label { font-weight: 500; }
            .btn-primary { width: 100%; }
            .card { box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        </style>
    </head>
    <body>
    <div class="container">
        <div class="card p-4">
            <h2 class="mb-4 text-center">Web Scraper Dashboard</h2>
            <form method="post">
                <div class="mb-3">
                    <label class="form-label">URLs (space-separated)</label>
                    <input name="urls" class="form-control" placeholder="https://example.com https://another.com" required>
                </div>
                <div class="mb-3 form-check form-switch">
                    <input class="form-check-input" type="checkbox" name="dynamic" id="dynamic">
                    <label class="form-check-label" for="dynamic">Dynamic Content (Selenium)</label>
                </div>
                <div class="mb-3 form-check form-switch">
                    <input class="form-check-input" type="checkbox" name="paginate" id="paginate">
                    <label class="form-check-label" for="paginate">Pagination</label>
                </div>
                <div class="row mb-3">
                    <div class="col">
                        <label class="form-label">Delay Min (s)</label>
                        <input name="delay_min" type="number" class="form-control" value="1" step="0.1">
                    </div>
                    <div class="col">
                        <label class="form-label">Delay Max (s)</label>
                        <input name="delay_max" type="number" class="form-control" value="3" step="0.1">
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">Proxies File (optional)</label>
                    <input name="proxies_file" type="text" class="form-control" placeholder="proxies.txt">
                </div>
                <div class="mb-3">
                    <label class="form-label">Config File (optional)</label>
                    <input name="config_file" type="text" class="form-control" placeholder="myconfig.yaml">
                </div>
                <button type="submit" class="btn btn-primary">Start Scraping</button>
            </form>
            <div class="mt-3 text-center">
                <a href="/status" class="btn btn-link">Check Job Status</a>
            </div>
        </div>
    </div>
    </body>
    </html>
    ''')

@app.route('/status')
def status():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Job Status</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
    <div class="container" style="max-width:600px; margin-top:40px;">
        <div class="card p-4">
            <h2 class="mb-3 text-center">Job Status</h2>
            <div class="alert {{'alert-success' if done and 'complete' in msg else 'alert-info'}}" role="alert">
                {{msg}}
            </div>
            {% if done %}
                <div class="d-flex justify-content-center gap-3">
                    <a href="/download/csv" class="btn btn-success">Download CSV</a>
                    <a href="/download/json" class="btn btn-secondary">Download JSON</a>
                    <a href="/" class="btn btn-link">Back</a>
                </div>
            {% else %}
                <div class="text-center mt-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Scraping in progress... Please wait.</p>
                </div>
                <meta http-equiv="refresh" content="2">
            {% endif %}
        </div>
    </div>
    </body>
    </html>
    ''', msg=job_status['message'], done=job_status['done'])

@app.route('/download/csv')
def download_csv():
    if os.path.exists('output.csv'):
        return send_file('output.csv', as_attachment=True)
    return 'No CSV output found.'

@app.route('/download/json')
def download_json():
    if os.path.exists('output.json'):
        return send_file('output.json', as_attachment=True)
    return 'No JSON output found.'

if __name__ == '__main__':
    app.run(debug=True) 