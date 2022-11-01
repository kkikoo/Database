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
            if len(S) < 3 or S[-3:] != '.db':  # must be db file
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
        # look for "continent" in database
        # add "continent" in database
        # update original continent
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
            elif name == None: #Neither
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

            # cannot be none
            if (code == "") or (name == ""):
                return_event.append(SaveContinentFailedEvent(
                    "continent_code and continent_name can not be empty!!!"))

            #code has to be unique
            elif code in (
                    [row[0] for row in c.execute("SELECT (continent_code) FROM continent ;")]):
                return_event.append(SaveContinentFailedEvent(
                    "Your input code is the same as the continent_code already in the database!!!"))
            #start searching
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

            # unique, no "(where ... != ...)"
            elif code in ([row[0] for row in
                           c.execute(
                               "SELECT (continent_code) FROM continent where continent_id != {};".format(
                                   id))]):
                return_event.append(SaveContinentFailedEvent(
                    "Your input continent_code is the same as the continent_code already in the database!!!"))

            #update
            #name & code cannot be none
            else:
                query = "UPDATE continent  SET continent_code='{}', name='{}'  WHERE continent_id={};".format(
                    code, name, id)

                c.execute(query)
                conn.commit()
                return_event.append(ContinentSavedEvent(
                    Continent(id, code, name)))

        conn.close() #close database

    def process_Country_related_events(self, event, return_event: list):
        #look for "country" in database
        #add "country" in database
        #update original country
        Country = namedtuple(
            'Country',
            ['country_id', 'country_code', 'name', 'continent_id', 'wikipedia_link', 'keywords'])
        conn = sqlite3.connect(self._file_path)
        c = conn.cursor()
        query = ""

        if isinstance(event, StartCountrySearchEvent):
            code, name = event._country_code, event._name

            if code == None:
                query = "SELECT * FROM country WHERE name = '{}';".format(
                    name)
            elif name == None:
                query = "SELECT * FROM country WHERE country_code = '{}';".format(
                    code)
            else:
                query = "SELECT * FROM country WHERE country_code = '{}' and name = '{}';".format(
                    code, name)
            for row in c.execute(query):
                _ = Country(row[0], row[1], row[2], row[3], row[4], row[5])
                return_event.append(CountrySearchResultEvent(_))

        elif isinstance(event, LoadCountryEvent):
            id = event._country_id
            query = "SELECT * FROM country WHERE country_id = {};".format(id)

            for row in c.execute(query):
                _ = Country(row[0], row[1], row[2], row[3], row[4], row[5])
                return_event.append(CountryLoadedEvent(_))

        elif isinstance(event, SaveNewCountryEvent):
            _ = event._country
            country_id, country_code, name, continent_id, wikipedia_link, keywords = _[
                                                                                         0], _[1], \
                                                                                     _[2], _[3], _[
                                                                                         4], _[5]
            #below cannot be non, only keywords can
            if country_code == "" or name == "" or continent_id == "" or wikipedia_link == "":
                return_event.append(SaveCountryFailedEvent(
                    "country_code and country_name and continent_id and wikipedia_link can not be empty!!!"))
            # unique test
            elif country_code in ([row[0] for row in
                                   c.execute("SELECT (country_code) FROM country ;")]):
                return_event.append(SaveCountryFailedEvent(
                    "Your input code is the same as the country_code already in the database!!!"))

            elif continent_id not in [int(row[0]) for row in
                                      c.execute("SELECT (continent_id) FROM continent;")]:
                return_event.append(SaveCountryFailedEvent(
                    "Your input continent_id is not record in database!!!"))

            # pass test, start
            else:
                query = "SELECT max(country_id) FROM country ;"
                max_id = max([int(row[0]) for row in c.execute(query)])

                if keywords == "":
                    query = "INSERT INTO country (country_id, country_code, name, continent_id, wikipedia_link, keywords) VALUES ({},'{}','{}',{},'{}',NULL);".format(
                        max_id + 1, country_code, name, continent_id, wikipedia_link)
                else:
                    query = "INSERT INTO country (country_id, country_code, name, continent_id, wikipedia_link, keywords) VALUES ({},'{}','{}',{},'{}','{}');".format(
                        max_id + 1, country_code, name, continent_id, wikipedia_link, keywords)

                c.execute("PRAGMA foreign_keys = ON;")
                c.execute(query)
                conn.commit()
                return_event.append(CountrySavedEvent(
                    Country(max_id + 1, country_code, name, continent_id, wikipedia_link,
                            keywords)))

        elif isinstance(event, SaveCountryEvent):
            _ = event._country
            country_id, country_code, name, continent_id, wikipedia_link, keywords = _[
                                                                                         0], _[1], \
                                                                                     _[2], _[3], _[
                                                                                         4], _[5]
            # Not NULL test
            if country_code == "" or name == "" or continent_id == "" or wikipedia_link == "":
                return_event.append(SaveCountryFailedEvent(
                    "country_code and country_name and continent_id and wikipedia_link can not be empty!!!"))
            # unique
            elif country_code in ([row[0] for row in c.execute(
                    "SELECT (country_code) FROM country where country_id != {};".format(
                        country_id))]):
                return_event.append(SaveCountryFailedEvent(
                    "Your input country_code is the same as the country_code already in the database!!!"))

            elif continent_id not in [int(row[0]) for row in
                                      c.execute("SELECT (continent_id) FROM continent ;")]:
                return_event.append(SaveCountryFailedEvent(
                    "Your input continent_id is not record in database!!!"))
            # pass test, update
            else:
                if keywords == None or keywords == "":
                    keywords = ""
                    c.execute(
                        "update country set keywords=NULL where country_id={};".format(country_id))

                query = "UPDATE country SET country_code='{}', name='{}', continent_id={}, \
                        wikipedia_link='{}'  WHERE country_id={};".format(
                    country_code, name, continent_id, wikipedia_link, country_id)

                c.execute("PRAGMA foreign_keys = ON;")
                c.execute(query)
                conn.commit()
                return_event.append(CountrySavedEvent(Country(
                    country_id, country_code, name, continent_id, wikipedia_link, keywords)))

        conn.close()  # close database

    def process_Region_related_events(self, event, return_event: list):
        #look for "region" in database
        #add "region" in database
        #update original region
        Region = namedtuple(
            'Region',
            ['region_id', 'region_code', 'local_code', 'name',
             'continent_id', 'country_id', 'wikipedia_link', 'keywords'])
        conn = sqlite3.connect(self._file_path)
        c = conn.cursor()
        query = ""

        if isinstance(event, StartRegionSearchEvent):
            local_code = event._local_code
            name = event._name
            region_code = event._region_code

            limit_of_local_code = ""
            limit_of_name = ""
            limit_of_region_code = ""

            if local_code != None:
                limit_of_local_code = "local_code = '{}'".format(local_code)
            else:
                limit_of_local_code = "local_code is not NULL"

            if name != None:
                limit_of_name = "name = '{}'".format(name)
            else:
                limit_of_name = "name is not NULL"

            if region_code != None:
                limit_of_region_code = "region_code = '{}'".format(region_code)
            else:
                limit_of_region_code = "region_code is not NULL"

            query = "select * from region where " + limit_of_local_code + \
                    " and " + limit_of_name + " and " + limit_of_region_code + ";"

            for row in c.execute(query):
                _ = Region(row[0], row[1], row[2], row[3],
                           row[4], row[5], row[6], row[7])
                return_event.append(
                    RegionSearchResultEvent(_)
                )

        elif isinstance(event, LoadRegionEvent):
            id = event._region_id
            query = "SELECT * FROM region WHERE region_id = {};".format(id)
            for row in c.execute(query):
                _ = Region(row[0], row[1], row[2], row[3],
                           row[4], row[5], row[6], row[7])
                return_event.append(
                    RegionLoadedEvent(_)
                )
        elif isinstance(event, SaveNewRegionEvent):
            _ = event._region

            continent_id_list = [int(row[0]) for row in c.execute(
                "SELECT (continent_id) FROM continent ;")]
            country_id_list = [int(row[0]) for row in c.execute(
                "SELECT (country_id) FROM country ;")]

            region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords = \
                _[0], _[1], _[2], _[3], _[4], _[5], _[6], _[7]

            #Null test，Wikipedia & keywords can be none
            if region_code == "" or local_code == "" or name == "" or continent_id == "" or country_id == "":
                return_event.append(SaveRegionFailedEvent(
                    "region_code, local_code, name, continent_id, country_id can not be empty!"))

            elif region_code in (
                    [row[0] for row in c.execute("SELECT (region_code) FROM region ;")]):
                return_event.append(
                    SaveRegionFailedEvent(
                        "Your input region_code is the same as the region_code already in the database!!!")
                )

            elif country_id not in country_id_list:
                return_event.append(
                    SaveRegionFailedEvent(
                        "Your input country_id is not record in database!!!")
                )
            elif continent_id not in continent_id_list:
                return_event.append(
                    SaveRegionFailedEvent(
                        "Your input continent_id is not record in database!!!")
                )
            else:
                query = "SELECT max(region_id) FROM region ;"
                max_id = max([int(row[0]) for row in c.execute(query)])

                # print(continent_id,country_id)
                # print(type(continent_id),type(country_id))

                # continent_id, country_id = int(continent_id), int (country_id)
                if keywords == "" and wikipedia_link == "":
                    query = "INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link,keywords) VALUES ({},'{}','{}','{}',{},{},NULL,NULL);".format(
                        max_id + 1, region_code, local_code, name, continent_id, country_id)
                elif keywords == "" and wikipedia_link != "":
                    query = "INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link,keywords) VALUES ({},'{}','{}','{}',{},{},'{}',NULL);".format(
                        max_id + 1, region_code, local_code, name, continent_id, country_id,
                        wikipedia_link)

                elif keywords != "" and wikipedia_link == "":
                    query = "INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link,keywords) VALUES ({},'{}','{}','{}',{},{}, NULL,'{}');".format(
                        max_id + 1, region_code, local_code, name, continent_id, country_id,
                        keywords)
                else:
                    query = "INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link,keywords) VALUES ({},'{}','{}','{}',{},{},'{}','{}');".format(
                        max_id + 1, region_code, local_code, name, continent_id, country_id,
                        wikipedia_link, keywords)

                c.execute("PRAGMA foreign_keys = ON;")
                c.execute(query)
                conn.commit()

                return_event.append(
                    RegionSavedEvent(Region(max_id + 1, region_code, local_code,
                                            name, continent_id, country_id, wikipedia_link,
                                            keywords))
                )

        elif isinstance(event, SaveRegionEvent):
            _ = event._region

            continent_id_list = [int(row[0]) for row in c.execute(
                "SELECT (continent_id) FROM continent ;")]
            country_id_list = [int(row[0]) for row in c.execute(
                "SELECT (country_id) FROM country ;")]

            region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords = \
                _[0], _[1], _[2], _[3], _[4], _[5], _[6], _[7]

            if region_code == "" or local_code == "" or name == "" or continent_id == "" or country_id == "":
                return_event.append(SaveRegionFailedEvent(
                    "region_code, local_code, name, continent_id, country_id, wikipedia_link can not be empty!"))

            elif region_code in ([row[0] for row in c.execute(
                    "SELECT (region_code) FROM region where region_id != {};".format(region_id))]):
                return_event.append(
                    SaveRegionFailedEvent(
                        "Your input region_code is the same as the region_code already in the database!!!")
                )
            elif country_id not in country_id_list:
                return_event.append(
                    SaveRegionFailedEvent(
                        "Your input country_id is not record in database!!!")
                )
            elif continent_id not in continent_id_list:
                return_event.append(
                    SaveRegionFailedEvent(
                        "Your input continent_id is not record in database!!!")
                )
            else:
                if keywords == None or keywords == "":
                    c.execute(
                        "UPDATE region SET keywords=NULL where region_id={}".format(region_id))
                    keywords = ""
                if wikipedia_link == None or wikipedia_link == "":
                    wikipedia_link = ""
                    c.execute("UPDATE region SET wikipedia_link=NULL where region_id={}".format(
                        region_id))

                query = "UPDATE region SET region_code='{}', local_code='{}',name = '{}', continent_id={}, \
                       country_id = {}  WHERE region_id={};".format(
                    region_code, local_code, name, continent_id, country_id, region_id)

                c.execute("PRAGMA foreign_keys = ON;")
                c.execute(query)
                conn.commit()
                return_event.append(RegionSavedEvent(Region(
                    region_id, region_code, local_code, name, continent_id, country_id,
                    wikipedia_link, keywords)))

        conn.close()

    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        # This is a way to write a generator function that always yields zero values.
        # You'll want to remove this and replace it with your own code, once you start
        # writing your engine, but this at least allows the program to run.
        print("receive: ", event)
        return_event = []
        # 3 + 4 + 4 + 4 = 15 events
        # Case 1: Application-level events
        if isinstance(event, OpenDatabaseEvent) or \
                isinstance(event, QuitInitiatedEvent) or \
                isinstance(event, CloseDatabaseEvent):
            self.process_Application_level_events(event, return_event)

        # Case2: Continent-related events
        elif isinstance(event, StartContinentSearchEvent) or \
                isinstance(event, LoadContinentEvent) or \
                isinstance(event, SaveNewContinentEvent) or \
                isinstance(event, SaveContinentEvent):
            self.process_Continent_related_events(event, return_event)

        # Case3: Country-related events
        elif isinstance(event, StartCountrySearchEvent) or \
                isinstance(event, LoadCountryEvent) or \
                isinstance(event, SaveNewCountryEvent) or \
                isinstance(event, SaveCountryEvent):
            self.process_Country_related_events(event, return_event)

        # Case4: Region-related events
        elif isinstance(event, StartRegionSearchEvent) or \
                isinstance(event, LoadRegionEvent) or \
                isinstance(event, SaveNewRegionEvent) or \
                isinstance(event, SaveRegionEvent):
            self.process_Region_related_events(event, return_event)

        else:
            return_event.append(ErrorEvent(
                "Unexpected error! Please quit and try again!"))

        print("output: ", return_event)
        yield from ()
