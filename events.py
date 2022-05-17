class Event:
    def __init__(
        self, name, description, organizer, eventype, startDate, length, notation
    ):
        self.eventname = name
        self.description = description
        self.organizer = organizer
        self.type = eventype
        self.startDate = startDate
        self.length = length
        self.note = 0
        self.ratings = [0]
        self.subscribed = {}
