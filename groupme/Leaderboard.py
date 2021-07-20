import requests
import json
import datetime
import webbrowser


ACCESS_TOKEN='<put your API key here>'
TAMU_GROUP_ID = '59399869'
FIGHT_CLUB_ID = '67203699'

GROUPME_BASE_URL = 'https://api.groupme.com/v3'
USERS_GROUP_URL = '{}/groups?token={}'.format(GROUPME_BASE_URL, ACCESS_TOKEN)
GROUP_MESSAGES_URL = '{}/groups/{}/messages?token={}&limit=100'.format(GROUPME_BASE_URL, FIGHT_CLUB_ID, ACCESS_TOKEN)
# /groups/:group_id/likes?period=<day|week|month>
LEADERBOARD_URL = '{}/groups/{}/likes?period=month&token={}'.format(GROUPME_BASE_URL, FIGHT_CLUB_ID, ACCESS_TOKEN)
DESTROY_GROUP_URL = '{}/groups/{}/destroy'.format(GROUPME_BASE_URL, FIGHT_CLUB_ID)

RESULTS_LIST = []

def destroy_group():
    r = requests.post(DESTROY_GROUP_URL)
    print(r)

def get_group_info():
    '''
    Gets info about the groups you belong to. This is needed to make any meaningful calls, and are used as global vars above
    '''
    r = requests.get(USERS_GROUP_URL)
    if r.status_code != 200:
        raise ApiError('Did not get 200 response: {}'.format(r.status_code))

    j = json.loads(r.content)
    for group in j['response']:
        print("%s - %s" %(group['name'], group['group_id']))

def iterate_all_messages(message_operator):
    '''
    Parses each message recording the user, and words in the message.
    '''
    url = GROUP_MESSAGES_URL
    while True:
        r = requests.get(url)
        if r.status_code == 304:
            # we are done.
            break
        if r.status_code != 200:
            print('Did not get 200 response: {}'.format(r.status_code))
            break

        j = json.loads(r.content)
        messages = j['response']['messages']
        for message in messages:
            message_operator(message)

        if len(messages) < 1: 
            break

        last_message_id = messages[len(messages)-1]['id']
        url = GROUP_MESSAGES_URL + "&before_id={}".format(last_message_id)


def get_leaderboard_info():
    '''
    Finds the most liked message for the past month.
    '''
    r = requests.get(LEADERBOARD_URL)
    if r.status_code != 200:
        raise ApiError('Did not get 200 response: {}'.format(r.status_code))

    j = json.loads(r.content)
    messages = j['response']['messages']
    top_message = messages[0]
    print("User: {} \nMessage: {}\nLikes: {}\nDate: {}".format(top_message['name'], top_message['text'], len(top_message['favorited_by']), datetime.datetime.fromtimestamp(top_message['created_at'])))
    #print(j['response'])


def get_images(message):
    if 'attachments' in message.keys() and len(message['attachments']) > 0:
        for attachment in message['attachments']:
            if 'url' in attachment.keys():
                RESULTS_LIST.append(attachment['url'])



# destroy_group()
#get_group_message_info()
# get_group_info()
# get_leaderboard_info()
iterate_all_messages(get_images)

for m in RESULTS_LIST:
    print(m)