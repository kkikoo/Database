# p2app/events/event_bus.py
#
# ICS 33 Fall 2022
# Project 2: Learning to Fly
#
# An intermediary that routes events to the parts of the application that are
# meant to handle them.
#
# * Most events are routed to the engine to be processed, with the engine's
#   results routed back to the user interface.
# * The user interface's internal events are routed back to the user interface
#   to be processed, with the engine never seeing them.
#
# YOU WILL NOT NEED TO MODIFY THIS FILE AT ALL



class EventBus:
    def __init__(self):
        self._view = None
        self._engine = None


    def register_view(self, view):
        self._view = view


    def register_engine(self, engine):
        self._engine = engine


    def initiate_event(self, event):
        if hasattr(event, '_INTERNAL'):
            self._view.handle_event(event)
        else:
            for result_event in self._engine.process_event(event):
                self._view.handle_event(result_event)
