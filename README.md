# Calendar Analytics

## About

Calendar Analytics takes your calendar and shows you what you've done over the years. The most sophisticated way to analyze your time. Built for fun by a couple of UC Berkeley students and grads!


## Features

**We show you accurate statistics based on your Google Calendar**. With that information, we can answer questions like:
- How many hours did you spend on your "Work" calendar each month?
- How big of a slice was your "Sleep" category?
- How many hours did you spend watching TV, by querying event names like "Game of Thrones" and "Westworld" as keywords?
- What was the history of time spent with your Significant Other in the past year?

**We give you the ability to make cross connections with other data.**
Showing detailed statistics of your data allows you to create comparisons with other data that you have. For example, a college student (and one of the founders) used Calendar Analytics' tagging system to determine [how much time she spent on her different classes and compared it to the grades she received in those classes](https://medium.com/@tiffanyqi/a-college-students-individual-analysis-of-productivity-of-four-years-e51e5ec3af6). With that information, she used real data to power real insights.

**We help you orient you on your goals.**
With transparency comes focus and goal setting. If you feel you spent too much time watching TV, you can actively work to decrease the numbers and see the results immediately.


## Development

Want to help contribute, fix a bug, or enhance an existing feature? Great! Here's how you can run Calendar Analytics on your local machine.

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
	export CJ_DJANGO_SECRET="still-secret"
	export CJ_GOOGLE_CALENDAR_API_CLIENT_ID="YOUR_CLIENT_ID_HERE"
	export CJ_GOOGLE_CALENDAR_API_CLIENT_SECRET="YOUR_CLIENT_SECRET_HERE"
	export APP_ENVIRONMENT="dev"
	```

- Refresh your command line so that the secret keys are in your environment. You can also run `source ~/.bashrc`. You can check that it works with `echo $APP_ENVIRONMENT`

- `cd` into the project directory and run the following:
	```
	pip install -r requirements.txt
	```

- Run the following:
	```
	python manage.py bower install
	```


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

Finally, to generate `.css` files from your `.scss` changes automatically, run one of the following:
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


### Another issue?
Feel free to add a issue to this repo, and someone will get back to you!


## Built on
- Django
- Angular
- Postgresql
- Angular-NVD3
- FullCalendar
- Angular UI Calendar
- JQuery - Ajax
- Moment
- Google Auth
- Bower

## Our Team
- [Max Fang](http://maxfangx.com/): Full-Stack Developer, Creator
- [Tiffany Qi](http://tiffanyqi.com/): Product Manager, Front-End Developer
- [James Uejio](http://jamesuejio.com/): Full-Stack Developer
- [Cindy Tung](https://www.linkedin.com/in/cindytung96): Full-Stack Developer
- [David Nguyen](https://www.linkedin.com/in/dnguyenv): Visual Designer
- [Andrew Huang](http://andrewhuang.tk): Full-Stack Developer

## License
The MIT License (MIT)

Copyright (c) 2016-2017 Calendar Analytics Team

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
