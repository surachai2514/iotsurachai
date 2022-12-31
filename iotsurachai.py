from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage,TextSendMessage
from datetime import datetime

import paho.mqtt.client as mqttClient
import time

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import gspread
sa = gspread.service_account(filename="iot-esp32-373206-ead1109082b3.json")
sh = sa.open("googlesheet")
wks = sh.worksheet("Sheet1")
                            

# Set up the Sheets API client
service = build('sheets', 'v4', credentials=Credentials.from_authorized_user_info())

# Define the spreadsheet ID and range for the data to be appended
spreadsheet_id = '1MEu_0SHmRa8XNmp5CjKXL7WHGqtwwnlHXAH7ZpEjUSY'
range_name = 'Sheet1!A1:D1'  # Append data to the first three columns of the first sheet

#date = nowday.strftime("%B %d, %Y")     #December 22, 2022
#date = nowday.strftime("%m/%d/%y")      #12/27/22
#date = nowday.strftime("%b-%d-%Y")      #Dec-27-2022


temp = ""
humi = ""

def on_message(client, userdata, msg):
    global temp,humi
    print(msg.topic+" "+str(msg.payload))

    nowday = datetime.now()
    date = nowday.strftime("%d/%m/%Y")       #22/12/2022
    time = nowday.strftime("%H:%M:%S")
    
    text_t_h = msg.payload.decode('UTF-8')
    values = [[date, time, text_t_h]]

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        insertDataOption='INSERT_ROWS',
        valueInputOption='RAW',
        body={'values': values}
    ).execute()
    
    
    #wks.append_row(text_t_h.split(','))
    t_and_h = text_t_h.split(',')
    temp = t_and_h[0]
    humi = t_and_h[1]

channel_secret = "b84a7a715d28ad8ffe10dd01c12ea072"
channel_access_token = "gw1Clt9cLIzdHoSgDuwDCoLzxKt1aIbsCspIz6NCLdfT+qQy5Dp0gOtmDV4yceMIvYSHFyOLpnEwQLn5DLKRP4hk7REbOeNQQahogh63V539OpGQBlemj/qdkLtEB3jWyof0B+mIDBxmvClxxvow8gdB04t89/1O/w1cDnyilFU="

broker_address= "mqtt.netpie.io"
port = 1883

client = mqttClient.Client("708fa3d4-72d6-458b-9bea-f386eb2cbbe5") # Client ID
user = "QYa6Hob9NGKsxckFe8RAY1yWaWR7kpJF" # Token
password = "5ublVkr8m9avYKDN4Kw6~L2e53*6bTqc" # Secret              
client.username_pw_set(user, password=password)    
client.on_message = on_message

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def home():
    try:
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)
        handler.handle(body, signature)
    except:
        pass
    
    return "Hello Line Chatbot"

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    global temp,humi
    text = event.message.text
    print(text)

    try:
        client.connect(broker_address, port=port)        
    except:
        print("Connection failed")
    
    if (text=="เปิดไฟ"):
        client.publish("@msg/led","ledon")
        text_out = "เปิดไฟเรียบร้อยแล้ว"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text_out))

    if (text=="ปิดไฟ"):
        client.publish("@msg/led","ledoff")
        text_out = "ปิดไฟเรียบร้อยแล้ว"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text_out))

    if (text=="สีแดง"):
        client.publish("@msg/color","red")
        text_out = "เปิดไฟสีแดงเรียบร้อยแล้ว"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text_out))

    if (text=="สีเขียว"):
        client.publish("@msg/color","green")
        text_out = "เปิดไฟสีเขียวเรียบร้อยแล้ว"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text_out))

    if (text=="สีน้ำเงิน"):
        client.publish("@msg/color","blue")
        text_out = "เปิดไฟสีน้ำเงินเรียบร้อยแล้ว"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text_out))

    if (text=="อุณหภูมิและความชื้น"):
        client.subscribe("@msg/t_h")
        client.loop_start()
        time.sleep(1.5) 
        client.loop_stop()
        if len(temp) > 0 and len(humi) > 0:
            text_out = "อุณหภูมิ " + temp + " ความชื้น " + humi
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text_out))
                     
if __name__ == "__main__":          
    app.run()

