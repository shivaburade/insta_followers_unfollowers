import pandas as pd
import pickle
import time
import json
import codecs

df = pd.read_csv('user_management.csv')
print(df.loc[df['ID']==333521760]['filename'].values[0])
'''
user_name = 'cute_pawster'
password = '**'
Session_folder = 'Session/'
users_management = 'user_management.csv'

#UDF
current_milli_time = lambda: str(int(round(time.time() * 1000)))

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



api = Client(user_name, password)
print(api.authenticated_user_id)
print(api.authenticated_user_name)
print(api.current_user())

uname = api.authenticated_user_name
filename = Session_folder + uname
onlogin_callback(api, filename)

users_df = pd.read_csv(users_management)
row = {}
row["ID"] = api.authenticated_user_id
row["uname"] = uname
row["filename"] = filename
users_df = users_df.append(row, ignore_index=True)
users_df.to_csv(users_management, index=False)
'''