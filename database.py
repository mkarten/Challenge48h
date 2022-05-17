from pymongo import *
import bson


class Database:
    def __init__(self) -> None:
        self.client = MongoClient("YOUR MONGODB URI HERE", 27017)
        self.db = self.client.Challenge48h

    def is_UUID_valid(self, UUID):
        if bson.objectid.ObjectId.is_valid(UUID):
            return self.db.User.find_one({"_id": bson.objectid.ObjectId(UUID)}) != None
        else:
            return False

    def create_user(self, user):
        self.db.User.insert_one(user)

    def find_user(self, username):
        return self.db.User.find_one({"username": username})

    def find_user_by_UUID(self, UUID):
        return self.db.User.find_one({"_id": bson.objectid.ObjectId(UUID)})

    def update_user(self, username, newdata):
        self.db.User.update_one({"username": username}, {"$set": newdata})

    def delete_user(self, username):
        self.db.User.delete_one({"username": username})

    def create_event(self, event):
        self.db.Event.insert_one(event)

    def find_event(self, eventname):
        return self.db.Event.find_one({"eventname": eventname})

    def find_event_by_UUID(self, UUID):
        return self.db.Event.find_one({"_id": bson.objectid.ObjectId(UUID)})

    def update_event(self, eventname, newdata):
        self.db.Event.update_one({"eventname": eventname}, {"$set": newdata})

    def delete_event(self, eventname):
        self.db.Event.delete_one({"eventname": eventname})

    def get_all_events(self):
        events = []
        for elem in self.db.Event.find({}):
            events.append(elem)
        return events

    def get_all_users(self):
        users = []
        for elem in self.db.User.find({}):
            users.append(elem)
        return users