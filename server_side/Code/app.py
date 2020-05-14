from instagram import WebAgentAccount, Account, Media, WebAgent
import pickle, os

account = None
if os.path.exists("session"):
    with open("session", 'rb') as f:
        account = pickle.load(f)
print(account)
if account == None:
    account = WebAgentAccount("shivaburade")
    account.auth("shivadon")
    print(account)
    with open("session", 'wb') as f:
        pickle.dump(account, f)

arr = list(account.get_followers(count=50, limit=200))
followers = []
while arr[1] != None :
    #print(arr[0])
    followers += arr[0]
    arr = list(account.get_followers(pointer=arr[1], count=50, limit=200))
    if arr[1] == None:
        followers += arr[0]

arr = list(account.get_follows(count=200, limit=200))
follows = []
while arr[1] != None :
    #print(arr[0])
    follows += arr[0]
    arr = list(account.get_follows(pointer=arr[1], count=200, limit=200))
    if arr[1] == None:
        follows += arr[0]

not_followers = []
for f in follows:
    if f not in followers:
        not_followers.append((f, f.profile_pic_url, "https://www.instagram.com/"+str(f.username)))
print(len(followers), len(follows), len(not_followers))
print(not_followers)


