from werkzeug.middleware.dispatcher import DispatcherMiddleware
from apimain_flask import app2
from search_videos_flask import app as app1

# Create a root "empty" Flask app
from flask import Flask
main_app = Flask(__name__)

# Mount both apps
application = DispatcherMiddleware(main_app, {
    '/': app1,         # search_videos app -> /videos
    '/api': app2       # apimain app -> /api/ask
})