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
            },
            {
                "name": "New Year",
                "date": "2222-01-01 13:30:00",
                "numberOfPlaces": "8"
            }
        ]
    monkeypatch.setattr("server.loadCompetitions", mock_loadCompetitions, raising=True)

    app = server.create_app()

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_logout(client):

    response = client.post('/showSummary', data={'email': 'john@simplylift.co'}, 
        follow_redirects=True)
    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome to the GUDLFT Registration Portal!" in response.data

def test_booking_process(client):

    response = client.get('/')
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    response = client.get('/book/Fall%20Classic/Simply%20Lift')
    response = client.post('/purchasePlaces', 
        data={'club': "Simply Lift", 'competition': "Fall Classic", 'places': 5}, 
        follow_redirects=True)

    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data
    assert b'Points available: 65' in response.data
    assert b'Number of Places: 8' in response.data
    
def test_access_multiple_comptetitions(client):

    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    response = client.get('/book/Spring%20Festival/Simply%20Lift')
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    response = client.get('/book/Fall%20Classic/Simply%20Lift')
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    response = client.get('/book/New%20Year/Simply%20Lift')
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    assert response.status_code == 200
    assert not b"Great-booking complete!" in response.data
    assert b'Points available: 80' in response.data
    assert b'Number of Places: 25' in response.data
    assert b'Number of Places: 13' in response.data
    assert b'Number of Places: 8' in response.data

def test_book_multiple_comptetitions(client):

    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    response = client.get('/book/Fall%20Classic/Simply%20Lift')
    response = client.post('/purchasePlaces', 
        data={'club': "Simply Lift", 'competition': "Fall Classic", 'places': 2}, 
        follow_redirects=True)

    response = client.get('/book/New%20Year/Simply%20Lift')
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    response = client.post('/purchasePlaces', 
        data={'club': "Simply Lift", 'competition': "New Year", 'places': 2}, 
        follow_redirects=True)

    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data
    assert b'Points available: 68' in response.data
    assert b'Number of Places: 25' in response.data
    assert b'Number of Places: 11' in response.data
    assert b'Number of Places: 6' in response.data

def test_log_multiple_account(client):
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    response = client.get('/logout', follow_redirects=True)
    response = client.post('/showSummary', data={'email': 'admin@irontemple.com'})

    assert response.status_code == 200
    assert b'Welcome, admin@irontemple.com' in response.data

def test_update_display_point_balance_other_account(client):
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    response = client.get('/book/Fall%20Classic/Simply%20Lift')
    response = client.post('/purchasePlaces', 
        data={'club': "Simply Lift", 'competition': "Fall Classic", 'places': 2}, 
        follow_redirects=True)
 
    response = client.get('/logout', follow_redirects=True)
    response = client.post('/showSummary', data={'email': 'admin@irontemple.com'})

    assert response.status_code == 200
    assert b'Number of Places: 25' in response.data
    assert b'Number of Places: 11' in response.data
    assert b'Number of Places: 8' in response.data
    assert b'Points available: 74' in response.data
    assert b'Points available: 4' in response.data

