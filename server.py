import datetime
import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html',clubs=clubs)

@app.route('/showSummary',methods=['POST'])
def showSummary():
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
        return render_template('welcome.html',club=club,competitions=competitions)
    except IndexError:
        erreur = 1
        return render_template('index.html',erreur=erreur)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    competitions_with_valid_date = []
    competitions_done = []

    for comp in competitions:
        date_str = str(comp['date'])
        date_object = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        if date_object > datetime.datetime.now():
            comp['date'] = date_object
            competitions_with_valid_date.append(comp)
        else:
            competitions_done.append(comp)

    places = request.form.get('places')

    if places:
        placesRequired = int(places)
        if (placesRequired <= int(competition['numberOfPlaces']) and placesRequired > 0) and (int(club['points'])>0 and (int(club['points']) >= placesRequired and placesRequired < 13)):
            competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
            club['points'] = int(club['points']) - placesRequired
            flash('Felicitation! vous venez de reserver {} places '.format(placesRequired))
        else:
            flash('echec lors de la reservation de {} places !'.format(placesRequired))
    else:
        flash('Aucune place n\'a été sélectionnée!')
    return render_template('welcome.html', club=club, competitions=competitions_with_valid_date, competition_done=competitions_done)

# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))