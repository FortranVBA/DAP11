
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

def test_display_point_balance(client):

    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    assert b"Club balances:" in response.data
    assert b"Simply Lift" in response.data
    assert b"Points available: 13" in response.data

