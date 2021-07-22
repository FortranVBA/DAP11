import pytest
from flask import Flask, render_template, request

import server

@pytest.fixture
def client(monkeypatch):
    def mock_loadClubs():
        return [
            {
                "name":"Simply Lift",
                "email":"john@simplylift.co",
                "points":"80"
            },
            {
                "name":"Iron Temple",
                "email": "admin@irontemple.com",
                "points":"4"
            },            
        ]
    monkeypatch.setattr("server.loadClubs", mock_loadClubs, raising=True)

    def mock_loadCompetitions():
        return [
            {
                "name": "Spring Festival",
                "date": "2000-03-27 10:00:00",
                "numberOfPlaces": "25"
            },
            {
                "name": "Fall Classic",
                "date": "2221-10-22 13:30:00",
                "numberOfPlaces": "13"
            }
        ]
    monkeypatch.setattr("server.loadCompetitions", mock_loadCompetitions, raising=True)

    app = server.create_app()

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_display_point_balance(client):

    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    assert b"Club balances:" in response.data
    assert b"Iron Temple" in response.data
    assert b"Points available: 4" in response.data

def test_booking_past_competition(client):

    response = client.get('/book/Spring%20Festival/Simply%20Lift')
    assert b"Error: Past competitions cannot be booked" in response.data

def test_good_booking_competition(client):

    response = client.get('/book/Fall%20Classic/Simply%20Lift')

    assert b"How many places?" in response.data

def test_max_purchase(client):

    response = client.get('/book/Fall%20Classic/Simply%20Lift')
    assert b'<input type="number" name="places" id="" min="0" max=12 />' in response.data
    
def test_max_points_available(client):

    response = client.get('/book/Fall%20Classic/Iron%20Temple')
    assert b'<input type="number" name="places" id="" min="0" max=1 />' in response.data
    
def test_booking_deduces_points(client):

    response = client.post('/purchasePlaces', 
        data={'club': "Simply Lift", 'competition': "Spring Festival", 'places': 5}, 
        follow_redirects=True)
    assert b'Great-booking complete!' in response.data
    assert b'Points available: 65' in response.data
    
def test_correct_email_log(client):

    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert b"Welcome, john@simplylift.co" in response.data

def test_incorrect_email_log(client):

    response = client.post('/showSummary', data={'email': 'fake@mail.com'})
    assert b"Email adress does not match any registered club." in response.data
    
