import requests

client_id = 'YOUR_TWITCH_CLIENT_ID'
client_secret = 'YOUR_TWITCH_CLIENT_SECRET'
def StreamerGame(streamer_name):

    body = {
        'client_id': client_id,
        'client_secret': client_secret,
        "grant_type": 'client_credentials'
    }
    r = requests.post('https://id.twitch.tv/oauth2/token', body)

    #data output
    keys = r.json()

    headers = {
        'Client-ID': client_id,
        'Authorization': 'Bearer ' + keys['access_token']
    }

    stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + streamer_name, headers=headers)

    stream_data = stream.json()
    if stream.status_code == 200:
        if len(stream_data['data']) == 1:
            return str(stream_data['data'][0]['game_id'])
        else:
            return None
    else:
        return None

