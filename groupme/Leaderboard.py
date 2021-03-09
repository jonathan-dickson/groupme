import requests
import json
import datetime


ACCESS_TOKEN='<put your API key here>'
TAMU_GROUP_ID = '59399869'
FIGHT_CLUB_ID = '60989593'

GROUPME_BASE_URL = 'https://api.groupme.com/v3'
USERS_GROUP_URL = '{}/groups?token={}'.format(GROUPME_BASE_URL, ACCESS_TOKEN)
GROUP_MESSAGES_URL = '{}/groups/{}/messages?token={}&limit=100'.format(GROUPME_BASE_URL, FIGHT_CLUB_ID, ACCESS_TOKEN)
# /groups/:group_id/likes?period=<day|week|month>
LEADERBOARD_URL = '{}/groups/{}/likes?period=month&token={}'.format(GROUPME_BASE_URL, FIGHT_CLUB_ID, ACCESS_TOKEN)


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


def get_group_message_info(before_id = None):
    '''
    Parses each message recording the user, and words in the message.
    '''
    if before_id == None:
        url = GROUP_MESSAGES_URL
    else:
        url = GROUP_MESSAGES_URL + "&before_id={}".format(before_id)

    word_message_map = {}
    user_message_map = {}
    total_message_count = 0
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
            # do message level work
            total_message_count += 1
            if message['name'] in user_message_map.keys():
                user_count = user_message_map[message['name']]
                user_message_map[message['name']] = user_count + 1
            else:
                user_message_map[message['name']] = 1

            if message['text'] is not None:  # filter out image only posts.

                #do word level work
                words = message['text'].lower().split(' ')
                for word in words:
                    if word in word_message_map.keys():
                        count = word_message_map[word]
                        word_message_map[word] = count + 1
                    else:
                        word_message_map[word] = 1
        
        if len(messages) < 1: 
            break

        last_message_id = messages[len(messages)-1]['id']
        url = GROUP_MESSAGES_URL + "&before_id={}".format(last_message_id)

    with open('words.csv', 'w', encoding="utf8") as outfile:
        for key, value in word_message_map.items():
            try:
                outfile.write('"{}","{}"\n'.format(key, value))
            except: 
                pass

    with open('users.csv', 'w') as outfile:
        for key, value in user_message_map.items():
            outfile.write('"{}", {}\n'.format(key, value))




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


get_group_message_info()
# get_group_info()
# get_leaderboard_info()