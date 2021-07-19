import json
from flask import Flask,render_template,request,redirect,flash,url_for
from datetime import datetime

def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions

def create_app():
    app = Flask(__name__)
    app.secret_key = 'something_special'

    competitions = loadCompetitions()
    clubs = loadClubs()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/showSummary',methods=['POST'])
    def showSummary():
        club = [club for club in clubs if club['email'] == request.form['email']][0]
        return render_template('welcome.html',current_club=club,competitions=competitions, clubs=clubs)


    @app.route('/book/<competition>/<club>')
    def book(competition,club):
        foundClub = [c for c in clubs if c['name'] == club][0]
        foundCompetition = [c for c in competitions if c['name'] == competition][0]
        if foundClub and foundCompetition:
            competition_date = datetime.strptime(foundCompetition["date"], "%Y-%m-%d %H:%M:%S")
            if competition_date < datetime.now():
                flash("Error: Past competitions cannot be booked")
                return render_template('welcome.html', current_club=foundClub, competitions=competitions, clubs=clubs)        
            maxPoint = 12
            return render_template('booking.html',
                club=foundClub,competition=foundCompetition, 
                maxPoint=maxPoint)
        else:
            flash("Something went wrong-please try again")
            return render_template('welcome.html', current_club=club, competitions=competitions, clubs=clubs)

    @app.route('/purchasePlaces',methods=['POST'])
    def purchasePlaces():
        competition = [c for c in competitions if c['name'] == request.form['competition']][0]
        club = [c for c in clubs if c['name'] == request.form['club']][0]
        placesRequired = int(request.form['places'])
        club["points"] = int(club["points"])
        competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
        club["points"] -= placesRequired
        flash('Great-booking complete!')
        return render_template('welcome.html', current_club=club, competitions=competitions, clubs=clubs)

    # TODO: Add route for points display


    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))

    return app
