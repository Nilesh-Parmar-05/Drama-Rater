import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# API Configuration
OMDB_API_URL = "http://www.omdbapi.com/"
OMDB_API_KEY = "77b58788"

# In-memory data for demonstration
watched_dramas = []
to_watch_dramas = []
reviews = {}  # Dictionary to store reviews by drama IMDb ID

class SearchForm(FlaskForm):
    search = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("Search")

class ReviewForm(FlaskForm):
    rating = IntegerField('Rating (out of 10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    cinematography = IntegerField('Cinematography (out of 10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    casting = IntegerField('Casting (out of 10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    story = IntegerField('Story (out of 10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    music = IntegerField('Music (out of 10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    review_text = StringField('Write your review', validators=[DataRequired()])
    submit = SubmitField('Submit Review')

@app.route("/", methods=["GET", "POST"])
def home():
    form = SearchForm(request.form)
    if request.method == "POST":
        if form.validate():
            search_query = form.search.data.strip()
            search_query = search_query.replace(" ", "+")
            response = requests.get(OMDB_API_URL, params={"apikey": OMDB_API_KEY, "s": search_query})
            if response.status_code != 200:
                flash("Error connecting to the OMDb API.")
                return redirect(url_for("home"))
            results = response.json().get("Search", [])
            if not results:
                flash("No results found. Please try a different search term.")
                return redirect(url_for("home"))
            return render_template("search_results.html", dramas=results, search_term=form.search.data)
    return render_template("home.html", form=form, watched_dramas=watched_dramas)

@app.route("/drama/<imdb_id>", methods=["GET", "POST"])
def drama_details(imdb_id):
    # Get the drama details from OMDB API
    response = requests.get(OMDB_API_URL, params={"apikey": OMDB_API_KEY, "i": imdb_id})
    drama = response.json()

    # Fetch user reviews
    user_review = reviews.get(imdb_id)

    # Handle review submission
    review_form = ReviewForm(request.form)
    if review_form.validate_on_submit():
        review_data = {
            "rating": review_form.rating.data,
            "cinematography": review_form.cinematography.data,
            "casting": review_form.casting.data,
            "story": review_form.story.data,
            "music": review_form.music.data,
            "review_text": review_form.review_text.data
        }
        reviews[imdb_id] = review_data  # Store the review temporarily in-memory
        flash("Your review has been submitted successfully!")
        return redirect(url_for("drama_details", imdb_id=imdb_id))

    # Display details including rating from the site
    return render_template("drama_details.html", drama=drama, review_form=review_form, user_review=user_review)

@app.route("/search/genre/<genre_name>/<country>")
def search_genre(genre_name, country):
    response = requests.get(OMDB_API_URL, params={"apikey": OMDB_API_KEY, "s": genre_name})
    if response.status_code != 200:
        flash("Error connecting to the OMDb API.")
        return redirect(url_for("home"))
    dramas = response.json().get("Search", [])
    filtered_dramas = [drama for drama in dramas if drama.get("Country", "").lower() == country.lower()]
    return render_template("search_results.html", dramas=filtered_dramas, search_term=genre_name, country=country)

@app.route("/to-watch", methods=["GET", "POST"])
def to_watch():
    if request.method == "POST":
        name = request.form.get("name").strip()
        if name:
            to_watch_dramas.append({"name": name})
            flash(f"'{name}' added to your To-Watch list.")
        else:
            flash("Drama name cannot be empty.")
    return render_template("to_watch.html", to_watch_dramas=to_watch_dramas)

if __name__ == "__main__":
    app.run(debug=True)
