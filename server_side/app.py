from instagram_private_api import Client, ClientCompatPatch
import pickle, os
from flask import Flask
import pandas as pd
from flask import request
import time
import codecs
import json
import pickle

#Defining constants.
app = Flask(__name__)
Session_folder = 'Session/'
users_management = 'user_management.csv'

#UDF
class User(dict):

    def __init__(self, ID, username, profile_pic_url, following=False, follower=False):
        self.ID = ID
        self.username = username
        self.profile_pic_url = profile_pic_url
        self.following = following
        self.follower = follower
        dict.__init__(self, self.__dict__)
    
    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        if self.username != other.username:
            return False
        return True

    def __hash__(self):
        return self.username

def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')

def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object

def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('SAVED: {0!s}'.format(new_settings_file))

def get_all_following(api):
    resp_following = api.user_following(api.authenticated_user_id, Client.generate_uuid())
    user_following = []
    next_max_id = True
    while next_max_id:
        for following in resp_following["users"]:
            user_following.append(User(following["pk"], following["username"], following["profile_pic_url"], following=True))

        if resp_following['next_max_id']:
            resp_following = api.user_following(api.authenticated_user_id, Client.generate_uuid(), max_id=resp_following['next_max_id'])
        else:
            next_max_id = False
    return user_following

def get_all_follower(api):
    resp_followers = api.user_followers(api.authenticated_user_id, Client.generate_uuid())
    user_followers = []
    next_max_id = True
    while next_max_id:    
        for follower in resp_followers["users"]:
            user_followers.append(User(follower["pk"], follower["username"], follower["profile_pic_url"], follower=True))
    
        if resp_followers['next_max_id']:
            resp_followers = api.user_followers(api.authenticated_user_id, Client.generate_uuid(), max_id=resp_followers['next_max_id'])
        else:
            next_max_id = False
    return user_followers

#application routes
@app.route('/login', methods=['POST'])
def login():
    try:
        uname = request.form['username'].strip()
        pwd = request.form['password'].strip()
        print(uname, pwd)
        account = Client(uname, pwd)
        user_id = account.authenticated_user_id
        filename = Session_folder + uname
        onlogin_callback(account, filename)

        users_df = pd.read_csv(users_management)
        row = {}
        row["ID"] = user_id
        row["uname"] = uname
        row["filename"] = filename
        users_df = users_df.append(row, ignore_index=True)
        users_df.to_csv(users_management, index=False)

        response = {}
        response["Code"] = 200
        response["Status"] = "Sucessful"
        response["ID"] = user_id
        return response
    except Exception as e:
        print(e)
        response = {}
        response["Code"] = 400
        response["Status"] = "Unsucessful"
        response["ID"] = None
        return response

@app.route("/unfollowers", methods=["POST"])
def unfollowers():
    ID = int(request.form['ID'].strip())
    max_keys = int(request.form['max_keys'].strip())
    users_df = pd.read_csv(users_management)
    filepath = users_df.loc[users_df["ID"] == ID]['filename'].values[0]
    #print(filepath, ID)
    with open(filepath, 'r') as readfile:
        account = json.load(readfile, object_hook=from_json)
    api = Client('abc', 'abc', settings=account)
    followers = get_all_follower(api)
    following = get_all_following(api)

    unfollowers = []
    for f in following:
        if f not in followers:
            f.follower = False
            unfollowers.append(f)
    print(unfollowers[0])
    #print(followers)
    print('Followers: ', len(followers))
    print('Following: ', len(following))
    print('Not Following you: ', len(unfollowers))

    return json.dumps({"total_keys": len(unfollowers), "data": unfollowers[max_keys:max_keys + 50]})

@app.route("/follow", methods=["POST"])
def follow():
    ID = int(request.form['ID'].strip())
    UID = int(request.form['UID'].strip())
    users_df = pd.read_csv(users_management)
    filepath = users_df.loc[users_df["ID"] == ID]['filename'].values[0]
    #print(filepath, ID)
    with open(filepath, 'r') as readfile:
        account = json.load(readfile, object_hook=from_json)
    api = Client('abc', 'abc', settings=account)
    
    res = api.friendships_create(UID)
    print(res)

    return json.dumps({"data": "Followed"})

@app.route("/unfollow", methods=["POST"])
def unfollow():
    ID = int(request.form['ID'].strip())
    UID = int(request.form['UID'].strip())
    users_df = pd.read_csv(users_management)
    filepath = users_df.loc[users_df["ID"] == ID]['filename'].values[0]
    #print(filepath, ID)
    with open(filepath, 'r') as readfile:
        account = json.load(readfile, object_hook=from_json)
    api = Client('abc', 'abc', settings=account)
    
    res = api.friendships_destroy(UID)
    print(res)

    return json.dumps({"data": "Unfollowed"})


@app.route("/mutual", methods=["POST"])
def mutual():
    ID = int(request.form['ID'].strip())
    users_df = pd.read_csv(users_management)
    filepath = users_df.loc[users_df["ID"] == ID]['filename'].values[0]
    #print(filepath, ID)
    with open(filepath, 'r') as readfile:
        account = json.load(readfile, object_hook=from_json)
    api = Client('abc', 'abc', settings=account)
    followers = get_all_follower(api)
    following = get_all_following(api)

    mutual = []
    for f in following:
        if f in followers:
            f.follower = True
            mutual.append(f)
    print(mutual[0])
    #print(followers)
    print('Followers: ', len(followers))
    print('Following: ', len(following))
    print('Not Following you: ', len(mutual))

    return json.dumps(mutual)


@app.route("/fans", methods=["POST"])
def fans():
    ID = int(request.form['ID'].strip())
    max_keys = int(request.form['max_keys'].strip())
    users_df = pd.read_csv(users_management)
    filepath = users_df.loc[users_df["ID"] == ID]['filename'].values[0]
    #print(filepath, ID)
    with open(filepath, 'r') as readfile:
        account = json.load(readfile, object_hook=from_json)
    api = Client('abc', 'abc', settings=account)
    followers = get_all_follower(api)
    following = get_all_following(api)

    fans = []
    for f in followers:
        if f not in following:
            f.following = False
            fans.append(f)
    print(fans[0])
    #print(followers)
    print('Followers: ', len(followers))
    print('Following: ', len(following))
    print('Not Following you: ', len(fans))

    return json.dumps({"total_keys": len(fans), "data": fans[max_keys:max_keys + 50]})

if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True, debug=True)



