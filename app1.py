from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from twilio.rest import Client
import sys
import os

app = Flask(__name__)
app.secret_key = "PPFWSLGJR9F3MJXVNPYHECCU"
# 'c8d2d3a8e2b9e9f02c2a372de65f79aa3d90d4b1674a836f'

VIRTUAL_TWILIO_NUMBER = "+15414223629"
VERIFIED_NUMBER = "+919597481792"
STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"
# STOCK_ENDPOINT = "https://www.alphavantage.co/query"
# NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
# STOCK_API_KEY = "45XD54292SZ6OZPC"
# NEWS_API_KEY = "3ca2e82b25c74710be8353d1abedc32d"
# TWILIO_SID = "ACdccb044018adf23c5f3d7c8a1c1e42a4"
# TWILIO_AUTH_TOKEN = "befd7fc6d0ce335d1dabb088da095896"

STOCK_ENDPOINT = os.getenv("STOCKENDPOINT")
NEWS_ENDPOINT = os.getenv("NEWSENDPOINT ")
STOCK_API_KEY = os.getenv("STOCKAPIKEY")
NEWS_API_KEY = os.getenv("NEWSAPIKEY")
TWILIO_SID = os.getenv("TWILIOSID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIOAUTHTOKEN")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_update', methods=['POST'])
def send_update():
    phone = request.form['phone']
    stock_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK_NAME,
        "apikey": STOCK_API_KEY,
    }
    response = requests.get(STOCK_ENDPOINT, params=stock_params)
    data = response.json()["Time Series (Daily)"]
    data_list = [value for (key, value) in data.items()]
    yesterday_data = data_list[0]
    yesterday_closing_price = yesterday_data["4. close"]

    day_before_yesterday_data = data_list[1]
    day_before_yesterday_closing_price = day_before_yesterday_data["4. close"]

    difference = float(yesterday_closing_price) - float(day_before_yesterday_closing_price)
    up_down = "🔺" if difference > 0 else "🔻"
    diff_percent = round((difference / float(yesterday_closing_price)) * 100)

    if abs(diff_percent) > 1:
        news_params = {
            "apiKey": NEWS_API_KEY,
            "qInTitle": COMPANY_NAME,
        }
        news_response = requests.get(NEWS_ENDPOINT, params=news_params)
        articles = news_response.json()["articles"]
        three_articles = articles[:3]

        formatted_articles = [
            f"{STOCK_NAME}: {up_down}{diff_percent}% \nHeadline: {article['title']}. \nBrief: {article['description']}. \nUrl: {article['url']} "
            for article in three_articles
        ]

        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        for article in formatted_articles:
            client.messages.create(
                body=article,
                from_=VIRTUAL_TWILIO_NUMBER,
                to=phone
            )
        flash('Stock update sent successfully! You will get updated in a few minutes!', 'success_send')
    else:
        flash('No significant changes in stock price.', 'info_send')

    return redirect(url_for('index'))

@app.route('/contact', methods=['POST'])
def contact():
    user_email = request.form['email']
    user_number = request.form['number']
    user_message = request.form['message']
    
    message_body = (
        f"Contact Form Submission:\n"
        f"From: {user_email} ({user_number})\n"
        f"Message: {user_message}"
    )
    
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message_body,
        from_=VIRTUAL_TWILIO_NUMBER,
        to=VERIFIED_NUMBER
    )
    
    flash('Your message has been sent successfully!', 'success_contact')
    return redirect(url_for('index'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


if __name__ == "__main__":
    app.run(debug=True)
