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
        return []
    monkeypatch.setattr("server.loadCompetitions", mock_loadCompetitions, raising=True)

    app = server.create_app()

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_correct_email_log(client):

    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert b"Welcome, john@simplylift.co" in response.data

def test_incorrect_email_log(client):

    response = client.post('/showSummary', data={'email': 'fake@mail.com'})
    assert b"Email adress does not match any registered club." in response.data
    