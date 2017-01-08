# Calendar Analytics


## About
Django, Angular, pg


## Features and Usage


## Running the App on Your Local Machine

### Installation

#### Required Downloads

Install the following, if you haven't already:
- [Virtualenv](https://virtualenv.pypa.io/en/stable/) in a separate folder
- [Django](https://www.djangoproject.com/). We use Python 2.7
- [Sass](http://sass-lang.com/install) for front-end
- [Bower](https://bower.io/)
- Fork or clone this app at https://github.com/MaxFangX/calendar-analytics


#### Setup

- Turn on the Google Calendar API by following the following steps:
	1. Use [this wizard](https://console.developers.google.com/start/api?id=calendar) to create or select a project in the Google Developers Console and automatically turn on the API. Click **Continue**, then **Go to credentials**.
	2. On the **Add credentials to your project** page, click the **Cancel** button.
	3. At the top of the page, select the **OAuth consent screen** tab. Select an **Email address**, enter a **Product name** if not already set, and click the Save button.
	4. Select the **Credentials tab**, click the **Create credentials** button and select **OAuth client ID**.
	5. Select the application type **Other**, enter the name "Calendar Analytics Local Project", and click the **Create** button.
	6. Identify the client_id and client_secret.

- If you're using bash, add the following as your environment variables in ~/.bashrc
	```
	export CJ_GOOGLE_CALENDAR_API_CLIENT_ID="YOUR_CLIENT_ID_HERE"
	export CJ_GOOGLE_CALENDAR_API_CLIENT_SECRET="YOUR_CLIENT_SECRET_HERE"
	export APP_ENVIRONMENT="dev"
	```

- Refresh your command line so that the secret keys are in your environment. You can also run `source ~/.bashrc`. You can check that it work with `echo $APP_ENVIRONMENT`

- Cd into the project directory and run the following:
```
pip install -r requirements.txt
```

- Run the following:
```
python manage.py bower install
```
Select "d3#^3.4.4 which resolved to 3.5.17 and is required by nvd3#1.8.5" for the right d3 version


### Running the App
Run the virtualenv by entering the virtualenv directory, and run:
```
source ENV-NAME/bin/./activate
```

Enter the calendar-analytics/cal directory

Set up the database by running
```
python manage.py migrate
```

Run the app itself by running
```
python manage.py runserver
```

Finally, to live update the front-end when you make a change, run one of the following:
```
sass-watch
sass --watch .
```


### Issues

#### Google Client ID is not found
Your bashrc is not configured. To ensure bashrc is being utilized correctly, run:
```
$echo PATH
```

#### Angular 404 Message
Try running the following: 
```
python manage.py bower install
```

Make sure you select "d3#^3.4.4 which resolved to 3.5.17 and is required by nvd3#1.8.5"!

#### Egg info failed error
May be specific to what dependency is being downloaded, but if for “postgresql”, brew install it instead with: 
```
brew install postgresql
```

#### 'Module_six_moves_urllib_parse' object has no attribute 'urlparse'
According to [Google](https://developers.google.com/google-apps/tasks/quickstart/python), 'this error can occur in Mac OSX where the default installation of the "six" module (a dependency of this library) is loaded before the one that pip installed.' There are a variety of different methods to fix this, and you can try any or all of the following methods:

- Add pip's install location to the PYTHONPATH system environment variable:
	
	Determine pip's install location with the following command:
	```
	pip show six | grep "Location:" | cut -d " " -f2
	```
	
	Add the following line to your ~/.bashrc file, replacing <pip_install_path> with the value determined above:
	```
	export PYTHONPATH=$PYTHONPATH:<pip_install_path>
	```
	
	Reload your ~/.bashrc file in any open terminal windows using the following command
	```
	source ~/.bashrc
	```
	
	If this doesn't work, try running the command again, or editing the pip_install_path then running the command again, this value might change. (Example of one that works: export PYTHONPATH=/Users/tiffanyqi/Desktop/env/env/lib/python2.7/site-packages)

- Uninstall and reinstall six by running
	```
	sudo pip uninstall six
	sudo pip install six
	```

- Uninstall and reinstall [python2.7](http://stackoverflow.com/questions/34303294/how-to-fix-broken-python-2-7-11-after-osx-updates)

- Uninstall and reinstall Calendar Analytics altogether

- DO NOT DOWNGRADE to google-api-python-client 1.3.2 (will throw another kind of error)

#### Category20 undefined
Run the following: 
```
python manage.py bower update
```

Be sure to choose “d3#^3.4.4 which resolved to 3.5.17 and is required by nvd3#1.8.5”!


## Acknowledgements


## License

## old stuff to incorporate

If you use your calendar often, then you must have a decent timeline of how you spend your time. Why not analyze it?

Tip: If you fill in the gaps, your stats will be even more meaningful!

Connect your Google Calendar and immediately see stats on how you've been spending your time.

Mostly built for fun!
