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


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        # This is a way to write a generator function that always yields zero values.
        # You'll want to remove this and replace it with your own code, once you start
        # writing your engine, but this at least allows the program to run.
        yield from ()
