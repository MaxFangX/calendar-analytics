# Calendar Analytics


## About
Django, Angular, pg


## Features and Usage


## Running the App on Your Local Machine

### Installation
Install [virtualenv](https://virtualenv.pypa.io/en/stable/) in a separate folder

Install [Django](https://www.djangoproject.com/). We use Python 2.7

Install [sass](http://sass-lang.com/install) for front-end

Fork or clone this app at https://github.com/MaxFangX/calendar-analytics


### Running the App
Run the virtualenv by entering the virtualenv directory, and run `source ENV-NAME/bin/./activate`

Enter the calendar-analytics/cal

Run `python manage.py migrate`, which sets up the database

Run `python manage.py runserver`, which runs the app itself

Run `sass-watch .` or `sass --watch .`, which live updates the front-end if you make a change

And you're done! If you have an issue, look below.


### Issues
**Google Client ID is not found**
Your bashrc is not configured. Run $echo PATH to ensure bashrc is being utilized correctly.

**Angular 404 Message**
Try running `python manage.py bower install`

**Egg info failed error**
May be specific to what dependency is being downloaded, but if for “postgresql”, brew install it instead with `brew install postgresql`

**'Module_six_moves_urllib_parse' object has no attribute 'urlparse'**
According to [Google](https://developers.google.com/google-apps/tasks/quickstart/python), 'this error can occur in Mac OSX where the default installation of the "six" module (a dependency of this library) is loaded before the one that pip installed.' There are a variety of different methods to fix this, and you can try any or all of the following methods:
- Add pip's install location to the PYTHONPATH system environment variable:
	1. Determine pip's install location with the following command: `pip show six | grep "Location:" | cut -d " " -f2`
	2. Add the following line to your ~/.bashrc file, replacing <pip_install_path> with the value determined above: `export PYTHONPATH=$PYTHONPATH:<pip_install_path>`
	3. Reload your ~/.bashrc file in any open terminal windows using the following command: `source ~/.bashrc`
	If this doesn't work, try running the command again, or editing the pip_install_path then running the command again, this value might change. (Example of one that works: export PYTHONPATH=/Users/tiffanyqi/Desktop/env/env/lib/python2.7/site-packages)
- Uninstall and reinstall six by running `sudo pip uninstall six` and `sudo pip install six`
- Uninstall and reinstall [python2.7](http://stackoverflow.com/questions/34303294/how-to-fix-broken-python-2-7-11-after-osx-updates)
- Uninstall and reinstall Calendar Analytics altogether
- DO NOT DOWNGRADE to google-api-python-client 1.3.2 (will throw another kind of error)

**Category20 undefined**:
Run `python manage.py bower update` again, and choose “d3#^3.4.4 which resolved to 3.5.17 and is required by nvd3#1.8.5”


## Acknowledgements


## License


####If you use your calendar often, then you must have a decent timeline of how you spend your time. Why not analyze it?
Tip: If you fill in the gaps, your stats will be even more meaningful!

#### Connect your Google Calendar and immediately see stats on how you've been spending your time.



Mostly built for fun!
