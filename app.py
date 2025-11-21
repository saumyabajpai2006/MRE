import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from helpers import movie_data_from_tmdb
from mre import *

app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretmre')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/recommender', methods=['GET','POST'])
def forminput():
    return render_template('form.html')

@app.route('/results', methods=['GET','POST'])
def result():
    if request.method == 'POST':
        name = request.form['name']
        by = request.form['by']
        count = request.form['count']
        print(f'name: {name}, by: {by}, count: {count}')
        count = int(count)
        match by:
            case 'name':
                movies = get_recommendation(name, count=count)
            case 'word':
                movies = get_recommendation(name, by=by, count=count)
        if not movies:
            flash('No movies available', 'danger')
            return redirect(url_for('forminput'))
        
        if movies == 'Movie not found':
            flash('Movie not found', 'danger')
            return redirect(url_for('forminput'))
        else:
            results = movie_data_from_tmdb(name, count=count)
            if results is None:
                flash('Error fetching movie data', 'danger')
                return redirect(url_for('forminput'))
            return render_template('results.html', name=name, by=by, count=count, results=results)
    return redirect(url_for('forminput'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_env = os.environ.get('FLASK_DEBUG', 'False').lower()
    debug = debug_env in ('1', 'true', 'yes')
    app.run(host="0.0.0.0", port=port, debug=debug)