from distutils.log import error
import os
import hashlib
import smtplib, ssl
import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    make_response,
    abort,
)
import bson
import statistics
from users import User
from events import Event
from database import Database

app = Flask(__name__)
db = Database()


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static"), "favicon.ico")


@app.route("/signup")
def signup():
    if db.is_UUID_valid(request.cookies.get("UUID")):
        return redirect(url_for("home"))
    return render_template("signup.html", error="")


@app.route("/signin")
def signin():
    if db.is_UUID_valid(request.cookies.get("UUID")):
        return redirect(url_for("home"))
    return render_template("signin.html", error="")


@app.route("/signup-form", methods=["POST"])
def signupform():
    newUser = User(
        request.form["username"],
        request.form["password"],
        request.form["email"],
        request.form["firstName"],
        request.form["lastName"],
        request.form["phoneNumber"],
        "user",
    )
    if db.find_user(newUser.username) == None:
        db.create_user(newUser.__dict__)
        return redirect(url_for("signin"))
    else:
        return render_template("signup.html", error="user already exist")


@app.route("/signin-form", methods=["POST"])
def signinform():
    connectUser = db.find_user(request.form["username"])
    h = hashlib.new("sha256")
    b = bytearray(request.form["password"], encoding="utf8")
    h.update(b)
    if connectUser == None:
        return render_template("signin.html", error="user does not exist")
    else:
        if connectUser["password"] != h.hexdigest():
            return render_template("signin.html", error="wrong password")
        else:
            resp = make_response(redirect(url_for("home")))
            resp.set_cookie("UUID", str(connectUser["_id"]))
            return resp


@app.route("/event/rating/<eventname>", methods=["POST"])
def rating(eventname):
    event = db.find_event(eventname)
    event["ratings"].append(int(request.form["rating"]))
    event["note"] = statistics.mean(event["ratings"])
    db.update_event(event["eventname"], event)
    return redirect(url_for("home"))


@app.route("/register-to-event/<eventname>", methods=["POST"])
def registerToEvent(eventname):
    event = db.find_event(eventname)
    user = db.find_user_by_UUID(request.cookies.get("UUID"))
    event["subscribed"][str(user["_id"])] = user["username"]
    user["events"][str(event["_id"])] = "member"
    db.update_event(event["eventname"], event)
    db.update_user(user["username"], user)
    return redirect(url_for("home"))


@app.route("/unregister-to-event/<eventname>", methods=["POST"])
def unregisterToEvent(eventname):
    event = db.find_event(eventname)
    user = db.find_user_by_UUID(request.cookies.get("UUID"))
    del event["subscribed"][str(user["_id"])]
    del user["events"][str(event["_id"])]
    db.update_event(event["eventname"], event)
    db.update_user(user["username"], user)
    return redirect(url_for("home"))


@app.route("/home")
def home():
    if not (db.is_UUID_valid(request.cookies.get("UUID"))):
        return redirect(url_for("signin"))
    else:
        return render_template("home.html", events=db.get_all_events())


@app.route("/profile")
def profile():
    if not (db.is_UUID_valid(request.cookies.get("UUID"))):
        return redirect(url_for("signin"))
    else:
        user = db.find_user_by_UUID(request.cookies.get("UUID"))
        return render_template(
            "profile.html",
            user=user,
            subscribed=[
                db.find_event_by_UUID(bson.objectid.ObjectId(UUID))
                for _, UUID in enumerate(user["events"])
            ],
        )


@app.route("/admin")
def admin():
    if not (db.is_UUID_valid(request.cookies.get("UUID"))):
        return redirect(url_for("signin"))
    user = db.find_user_by_UUID(request.cookies.get("UUID"))
    if user["type"] != "admin":
        return redirect(url_for("home"))
    return render_template("admin.html")


@app.route("/admin/dashboard")
def dashboard():
    if not (db.is_UUID_valid(request.cookies.get("UUID"))):
        return redirect(url_for("signin"))
    user = db.find_user_by_UUID(request.cookies.get("UUID"))
    if user["type"] != "admin":
        return redirect(url_for("home"))
    return render_template(
        "dashboard.html", allevents=db.get_all_events(), allusers=db.get_all_users()
    )


@app.route("/signout")
def signout():
    resp = make_response(redirect(url_for("landing")))
    resp.set_cookie("UUID", "", expires=0)
    return resp


@app.route("/orga")
def orga():
    if not (db.is_UUID_valid(request.cookies.get("UUID"))):
        return redirect(url_for("signin"))
    user = db.find_user_by_UUID(request.cookies.get("UUID"))
    if user["type"] != "orga" and user["type"] != "admin":
        return redirect(url_for("home"))
    return render_template("orga.html")


@app.route("/orga/create-event")
def createEvent():
    if not (db.is_UUID_valid(request.cookies.get("UUID"))):
        return redirect(url_for("signin"))
    user = db.find_user_by_UUID(request.cookies.get("UUID"))
    if user["type"] != "orga" and user["type"] != "admin":
        return redirect(url_for("home"))
    return render_template("create-event.html", error="")


@app.route("/orga/delete-event")
def deleteEvent():
    if not (db.is_UUID_valid(request.cookies.get("UUID"))):
        return redirect(url_for("signin"))
    user = db.find_user_by_UUID(request.cookies.get("UUID"))
    if user["type"] != "orga" and user["type"] != "admin":
        return redirect(url_for("home"))
    return redirect(url_for("profile"))


@app.route("/orga/create-event-form", methods=["POST"])
def createEventForm():
    if not (db.is_UUID_valid(request.cookies.get("UUID"))):
        return redirect(url_for("signin"))
    user = db.find_user_by_UUID(request.cookies.get("UUID"))
    if user["type"] != "orga" and user["type"] != "admin":
        return redirect(url_for("home"))

    newEvent = Event(
        request.form["eventname"],
        request.form["description"],
        user["username"],
        request.form["eventtype"],
        request.form["startdate"],
        request.form["length"],
        "",
    )
    if db.find_event(newEvent.eventname) == None:
        db.create_event(newEvent.__dict__)
        event = db.find_event(newEvent.eventname)
        user["events"][str(event["_id"])] = "creator"
        db.update_user(user["username"], user)
        return redirect(url_for("createEvent"))
    else:
        return render_template("createEvent.html", error="event already exist")


@app.route("/admin/delete-user-form/<username>", methods=["POST"])
def deleteUserForm(username):
    user = db.find_user(username)
    db.delete_user(username)
    return redirect(url_for("dashboard"))


@app.route("/orga/delete-user-from-event-form/<username>/<eventname>", methods=["POST"])
def deleteUserFromEventForm(username, eventname):
    event = db.find_event(eventname)
    user = db.find_user(username)
    del user["events"][str(event["_id"])]
    del event["subscribed"][str(user["_id"])]
    db.update_event(event["eventname"], event)
    db.update_user(user["username"], user)
    return redirect(url_for("profile"))


@app.route("/orga/delete-event-form/<eventname>", methods=["POST"])
def deleteEventForm(eventname):
    users = db.get_all_users()
    event = db.find_event(eventname)
    for user in users:
        if str(event["_id"]) in user["events"]:
            del user["events"][str(event["_id"])]
        db.update_user(user["username"], user)
    db.delete_event(eventname)
    return redirect(url_for("profile"))


@app.route("/event/<eventName>")
def eventDetails(eventName):
    event = db.find_event(eventName)
    user = db.find_user_by_UUID(request.cookies.get("UUID"))
    if event == None:
        abort(404, description="Not found")
    return render_template(
        "event.html",
        event=event,
        strId=str(event["_id"]),
        subscribed=[
            db.find_user_by_UUID(bson.objectid.ObjectId(UUID))
            for _, UUID in enumerate(event["subscribed"])
        ],
        user=user,
    )


@app.route("/404")
def notFound():
    return render_template("404.html")


@app.route("/500")
def serverError():
    return render_template("500.html")


@app.errorhandler(404)
def Page_Not_Found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def Internal_Server_Error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.static_folder = "static"
    app.run()