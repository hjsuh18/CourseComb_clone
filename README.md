# coursecomb
## How to start
#### Virtualenv
Make a virtualenv and activate it
```
cd coursecomb
virtualenv env
source bin/activate/env
```
Download requirements (make sure your virtualenv is activated)
```
pip install -r requirements.txt
```
#### Database
Follow this: https://tutorial-extensions.djangogirls.org/en/optional_postgresql_installation. For the update settings part, the code we have already link to postgres, but make sure that user and the database name match whatever you choose.
#### Scraper stuff
To run `scraper_all`
```
cd test
python manage.py shell < courses/scrape_all.py
```

Clear, scrape and update database (when new :
cd test
./rescrape.sh