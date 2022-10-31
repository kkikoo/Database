# p2app/engine/main.py
#
# ICS 33 Fall 2022
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.


import sqlite3
from collections import namedtuple
from turtle import update

from p2app.events.database import CloseDatabaseEvent, DatabaseClosedEvent, DatabaseOpenFailedEvent, DatabaseOpenedEvent, OpenDatabaseEvent
from p2app.events.app import EndApplicationEvent, ErrorEvent, QuitInitiatedEvent
from p2app.events.continents import ContinentLoadedEvent, ContinentSavedEvent, ContinentSearchResultEvent, LoadContinentEvent, SaveContinentEvent, SaveContinentFailedEvent, SaveNewContinentEvent, StartContinentSearchEvent
from p2app.events.countries import CountryLoadedEvent, CountrySavedEvent, CountrySearchResultEvent, LoadCountryEvent, SaveCountryEvent, SaveCountryFailedEvent, SaveNewCountryEvent, StartCountrySearchEvent
from p2app.events.regions import LoadRegionEvent, RegionLoadedEvent, RegionSavedEvent, RegionSearchResultEvent, SaveNewRegionEvent, SaveRegionEvent, SaveRegionFailedEvent, StartRegionSearchEvent



class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self._file_path = None
        pass

    def process_Application_level_events(self, event, return_event: list):
        # open database
        # close database
        # exit
        if isinstance(event, OpenDatabaseEvent):
            S = str(event.path())
            if len(S) < 3 or S[-3:] != '.db':  # db file
                return_event.append(
                    DatabaseOpenFailedEvent("Please open a db file !!!"))

            else:
                self._file_path = event.path()
                return_event.append(DatabaseOpenedEvent(event.path()))

        elif isinstance(event, QuitInitiatedEvent):
            return_event.append(EndApplicationEvent())

        elif isinstance(event, CloseDatabaseEvent):
            return_event.append(DatabaseClosedEvent)

    def process_Continent_related_events(self, event, return_event: list):

        Continent = namedtuple(
            'Continent', ['continent_id', 'continent_code', 'name'])

        conn = sqlite3.connect(self._file_path)
        c = conn.cursor()
        query = ""

        if isinstance(event, StartContinentSearchEvent):
            code, name = event._continent_code, event._name

            if code == None:
                query = "SELECT * FROM continent WHERE name = '{}';".format(
                    name)
            elif name == None:
                query = "SELECT * FROM continent WHERE continent_code = '{}';".format(
                    code)
            else:
                query = "SELECT * FROM continent WHERE continent_code = '{}' and name = '{}';".format(
                    code, name)
            for row in c.execute(query):
                _ = Continent(row[0], row[1], row[2])
                return_event.append(ContinentSearchResultEvent(_))

        elif isinstance(event, LoadContinentEvent):
            id = event._continent_id
            query = "SELECT * FROM continent WHERE continent_id = {};".format(
                id)

            for row in c.execute(query):
                _ = Continent(row[0], row[1], row[2])
                return_event.append(ContinentLoadedEvent(_))

        elif isinstance(event, SaveNewContinentEvent):
            _ = event._continent
            id, code, name = _[0], _[1], _[2]


            if (code == "") or (name == ""):
                return_event.append(SaveContinentFailedEvent(
                    "continent_code and continent_name can not be empty!!!"))


            elif code in (
                    [row[0] for row in c.execute("SELECT (continent_code) FROM continent ;")]):
                return_event.append(SaveContinentFailedEvent(
                    "Your input code is the same as the continent_code already in the database!!!"))

            else:
                query = "SELECT max(continent_id) FROM continent ;"
                max_id = max([int(row[0]) for row in c.execute(query)])
                query = "INSERT INTO continent (continent_id, continent_code, name) VALUES ({},'{}','{}');".format(
                    max_id + 1, code, name)
                c.execute(query)
                conn.commit()
                return_event.append(ContinentSavedEvent(
                    Continent(max_id + 1, code, name)))

        elif isinstance(event, SaveContinentEvent):
            _ = event._continent
            id, code, name = _[0], _[1], _[2]

            # Not Null check
            if (code == "") or (name == ""):
                return_event.append(SaveContinentFailedEvent(
                    "continent_code and continent_name can not be empty!!!"))

            # unique
            elif code in ([row[0] for row in
                           c.execute(
                               "SELECT (continent_code) FROM continent where continent_id != {};".format(
                                   id))]):
                return_event.append(SaveContinentFailedEvent(
                    "Your input continent_code is the same as the continent_code already in the database!!!"))

            #update

            else:
                query = "UPDATE continent  SET continent_code='{}', name='{}'  WHERE continent_id={};".format(
                    code, name, id)

                c.execute(query)
                conn.commit()
                return_event.append(ContinentSavedEvent(
                    Continent(id, code, name)))

        conn.close()


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        # This is a way to write a generator function that always yields zero values.
        # You'll want to remove this and replace it with your own code, once you start
        # writing your engine, but this at least allows the program to run.
        yield from ()
