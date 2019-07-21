from worldbankapp import app

import json, plotly
from flask import render_template, request, Response, jsonify,  Flask,  abort, redirect
from scripts.data import return_figures
from uuid import uuid4
import requests
import requests.auth
import urllib.parse

CLIENT_ID = "0f7ac5c75709e1eb1558"
CLIENT_SECRET = "6be38a7698c54227cb8d27922ac222115916cbc7"
REDIRECT_URI = "https://github-network-app.herokuapp.com/callback"

state = str(uuid4())

@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
	return render_template('index.html')


@app.route("/forward/", methods=['POST'])
def move_forward():
    return redirect(make_authorization_url())


@app.route('/about/')
def aboutpage():
    title = "Github Network App"
    paragraph = ["This app"]
    pageType = 'about'
    return render_template("index.html", title=title, paragraph=paragraph, pageType=pageType)


@app.route('/callback')
def reddit_callback():
	error = request.args.get('error', '')
	if error:
		return "Error: " + error
	state = request.args.get('state', '')
	if not is_valid_state(state):
		# Uh-oh, this request wasn't started by us!
		abort(403)
	code = request.args.get('code')
	# We'll change this next line in just a moment
	return redirect(get_user_webpage(get_users(get_token(code))), code=302) # "got a code! %s" % get_users(get_token(code))
	

def get_token(code):
    save_created_state(state)
    print("here")
    params = {"client_id": CLIENT_ID,
              "redirect_uri": REDIRECT_URI,
              "client_secret": CLIENT_SECRET,
              "code": code,
			  "state": state
			  }
    import urllib
    url = "https://github.com/login/oauth/access_token?" + urllib.parse.urlencode(params)
    response = requests.post(url)
    token = parse_response_text(response)
    return  token 

def parse_response_text(response):
    output = response.text.split("&")
    token = output[0].split("=")
    return token[1]

def make_authorization_url():
	# Generate a random string for the state parameter
	# Save it for use later to prevent xsrf attacks
	save_created_state(state)
	params = {"client_id": CLIENT_ID,
			  "response_type": "code",
			  "state": state,
			  "redirect_uri": REDIRECT_URI,
			  "duration": "temporary",
			  "scope": "identity"}
	import urllib
	url = "https://github.com/login/oauth/authorize?" + urllib.parse.urlencode(params) 
	return url
    
def get_users(access_token):
	params = {"access_token": access_token}
	import urllib
	url = "https://api.github.com/user?" + urllib.parse.urlencode(params) 
	response = requests.get(url)
	return response.json()

def get_user_webpage(json_response):
	html_url = json_response['html_url']
	return html_url


def get_user_emails(json_response):
	email = json_response['email']
	return email

def get_user_login_name(json_response):
	login = json_response['login']
	return login	    
    
def get_user_name(json_response):
	name = json_response['name']
	return name	    
    
def get_followers(json_response):
	url = json_response['followers_url']
	import urllib 
	response = requests.get(url)
	return response.json()
   
def get_repos(json_response):
	url = json_response['repos_url']
	import urllib 
	response = requests.get(url)
	return response.json()


def get_collaborators(json_repos, access_token):
	params = {"access_token": access_token}
	import urllib
	url = "https://api.github.com/repos/magrathj/shinyforms/collaborators" + urllib.parse.urlencode(params)
	return url

# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache,
# or perhaps cryptographically sign them and verify upon retrieval.
def save_created_state(state):
	pass
def is_valid_state(state):
	return True

## TODO create class repo to hold individual repos
class Repo:
	def __init__(self, repo_name, repo_url):
		self.repo_name = repo_name
		self.repo_url = repo_url


## TODO create class user to hold individual user details
class User:
	def __init__(self, name, github_url, login):
		self.name = name
		self.github_url = github_url
		self.login = login


## TODO create class Github to handle all Github methods
class Github:
	def __init__(self, client_id, client_secret):
		self.client_id = client_id
		self.client_secret = client_secret

