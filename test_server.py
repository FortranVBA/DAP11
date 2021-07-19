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
                "points":"13"
            },
        ]
    monkeypatch.setattr("server.loadClubs", mock_loadClubs, raising=True)

    def mock_loadCompetitions():
        return [
            {
                "name": "Spring Festival",
                "date": "2100-03-27 10:00:00",
                "numberOfPlaces": "25"
            }            
        ]
    monkeypatch.setattr("server.loadCompetitions", mock_loadCompetitions, raising=True)

    app = server.create_app()

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_booking_deduces_points(client):

    response = client.post('/purchasePlaces', 
        data={'club': "Simply Lift", 'competition': "Spring Festival", 'places': 5}, 
        follow_redirects=True)
    assert b'Great-booking complete!' in response.data
    assert b'Points available: 8' in response.data
