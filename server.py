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
        list_clubs = [club for club in clubs if club['email'] == request.form['email']]
        if list_clubs:
            club = [club for club in clubs if club['email'] == request.form['email']][0]
            return render_template('welcome.html',current_club=club,competitions=competitions, clubs=clubs)
        else:
            error = 'Email adress does not match any registered club.'
            return render_template('index.html', error=error)

    @app.route('/book/<competition>/<club>')
    def book(competition,club):
        matching_clubs = [c for c in clubs if c['name'] == club]
        if not matching_clubs:
            flash("Something went wrong with your club. Please log out and try again")
            return render_template('welcome.html', current_club=club, competitions=competitions, clubs=clubs)
        foundClub = matching_clubs[0]

        matching_competitions = [c for c in competitions if c['name'] == competition]
        if not matching_competitions:
            flash("Something went wrong with the competition. Please try again")
            return render_template('welcome.html', current_club=foundClub, competitions=competitions, clubs=clubs)
        foundCompetition = matching_competitions[0]

        competition_date = datetime.strptime(foundCompetition["date"], "%Y-%m-%d %H:%M:%S")
        if competition_date < datetime.now():
            flash("Error: Past competitions cannot be booked")
            return render_template('welcome.html', current_club=foundClub, competitions=competitions, clubs=clubs)        
        maxSeat = min(int(foundClub["points"])//3, 12)
        return render_template('booking.html',
            club=foundClub,competition=foundCompetition, 
            maxSeat=maxSeat)

    @app.route('/purchasePlaces',methods=['POST'])
    def purchasePlaces():
        competition = [c for c in competitions if c['name'] == request.form['competition']][0]
        club = [c for c in clubs if c['name'] == request.form['club']][0]

        competition_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")
        if competition_date < datetime.now():
            flash("Error: Past competitions cannot be booked")
            return render_template('welcome.html', current_club=club, competitions=competitions, clubs=clubs)        

        placesRequired = int(request.form['places'])
        club["points"] = int(club["points"])

        if club["points"] < 3 * placesRequired:
            flash('The club does not have enough points !')
        elif placesRequired > 12:
            flash('Cannot book more than 12 places !')
        else:
            competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
            club["points"] -= placesRequired * 3
            flash('Great-booking complete!')
        return render_template('welcome.html', current_club=club, competitions=competitions, clubs=clubs)

    # TODO: Add route for points display


    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))

    return app
