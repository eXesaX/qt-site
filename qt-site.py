from flask import Flask, Response, redirect, url_for, request, session, abort, jsonify
from flask.ext.login import LoginManager, UserMixin, \
    login_required, login_user, logout_user, current_user

app = Flask(__name__)

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


class Record:
    def __init__(self, id, type, value):
        self.id = id
        self.type = type
        self.value = value

    def as_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "value": self.value,
        }


class Favourite:
    def __init__(self, rec_id, user_id):
        self.rec = rec_id
        self.user = user_id





# create some users with ids 1 to 20
users = [User(id) for id in range(1, 21)]

records = []
records.append(Record(1, "text", "some text"))
records.append(Record(2, "image", "image link"))
records.append(Record(3, "audio", "audio link"))
records.append(Record(4, "video", "video link"))
records.append(Record(5, "web", "url"))


favourites = []
favourites.append(Favourite(1, 1))
favourites.append(Favourite(2, 1))
favourites.append(Favourite(3, 1))
favourites.append(Favourite(2, 2))
favourites.append(Favourite(3, 2))
favourites.append(Favourite(2, 3))
favourites.append(Favourite(3, 3))


# some protected url
@app.route('/')
@login_required
def home():
    return Response("Hello World!")


@app.route('/list')
@login_required
def list():
    return jsonify([rec.as_dict() for rec in records])


@app.route('/favourite')
@login_required
def favourite():
    user = current_user
    favourite_records = [rec for rec in favourites if int(rec.user) == int(user.id)]
    recs = [rec for rec in records for fav_rec in favourite_records if rec.id == fav_rec.rec]
    return jsonify([rec.as_dict() for rec in recs])


@app.route('/add_favourite/<rec_id>')
@login_required
def add_favourite(rec_id):
    user = current_user
    favourites.append(Favourite(rec_id, user.id))
    return "OK"


# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == username + "_secret":
            id = username.split('user')[1]
            user = User(id)
            login_user(user)
            return redirect(request.args.get("next"))
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)


if __name__ == "__main__":
    app.run()