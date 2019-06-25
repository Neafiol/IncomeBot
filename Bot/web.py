from flask import Flask
import os

#heroku scale worker=1 - for start bot on heroku
app = Flask(__name__)
@app.route('/')
def root():
    return "acura bot is running"
if __name__ == '__main__':
    import subprocess


    if 'DYNO' in os.environ:
        port = os.environ.get('PORT', 5000)
        app.run('0.0.0.0', port, debug=False)

