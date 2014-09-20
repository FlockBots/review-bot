# | Download Archive
# | Convert CSV into Database
# Stop Bot
# | Backup old database
# | Migrate Review Table to old Database
# - Test/Check if migration was successfull
# Start Bot

import sys, os, csv, shutil, sqlite3, praw, requests, logging
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor

### START CONFIG ###
DB_TMP = 'tmp.db'
DB_BOT = 'bot.db'
DB_BK = 'data.bk'
DB_TABLE = 'reviews'
CSV_ARCHIVE = 'archive.csv'
ARCHIVE_KEY = '0AsnkEzAVwhUVdF91M3R1NFdvQWYwY1JEeHNpNnZCbVE'
### END  CONFIG ###

def download():
    logging.debug('Downloading CSV Archive.')
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    resp = opener.open('https://docs.google.com/spreadsheet/ccc?key={key}&output=csv'.format(key=ARCHIVE_KEY))
    data = resp.read().decode('utf-8')
    with open(CSV_ARCHIVE, 'w') as f:
        f.write(data)

def create_tmp_db():
    logging.debug('Creating Temporary Database.')
    db = sqlite3.connect(DB_TMP)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE {table} (
        id INTEGER NOT NULL,
        submission_id VARCHAR,
        title VARCHAR,
        user VARCHAR,
        url VARCHAR,
        subreddit VARCHAR,
        date INTEGER,
        score INTEGER,
        PRIMARY KEY (id)
    )'''.format(table = DB_TABLE))
    cursor.execute('CREATE UNIQUE INDEX review ON {table}(user, url)'.format(table = DB_TABLE))
    db.commit()
    return db

### mm/dd/yyyy or dd/mm/yyyy
def string_to_date(date_string):
    month = date_string[0:1]
    day   = date_string[3:4]
    year  = date_string[6:]
    if int(month) > 12:
        month, day = day, month
    if len(year) == 2:
        year = '20' + year
    return '{y}{m}{d}'.format(y=year, m=month, d=day)

def parse(archive, db):
    logging.info('Parsing Archive.')
    cursor = db.cursor()
    r = praw.Reddit('Whisky Archive Parser by /u/FlockOnFire')
    reader = csv.reader(archive)
    counter = 0
    for row in reader:
        if counter > 0:
            user = row[2]

            # Fix url
            if row[3][0] != 'h':
                if row[3][0] != 'w':
                    row[3] = 'www.' + row[3]
                row[3] = 'http://' + row[3]
            row[3] = row[3].replace('http://reddit', 'http://www.reddit')

            try:
                submission = r.get_submission(row[3])
                review_date = string_to_date(row[5])
                score = row[6]
                cursor.execute('INSERT INTO {table} VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)'.format(table = DB_TABLE), (
                    submission.id, 
                    submission.title.encode('utf-8'), 
                    user.lower(), 
                    submission.permalink, 
                    submission.subreddit.display_name.lower(),
                    review_date,
                    score
                ))
            except sqlite3.IntegrityError as e:
                # skip inserting this one
                pass
            except requests.exceptions.HTTPError as e:
                print('{0:<10}, {1}'.format(counter, row[3]))
        counter += 1
        if counter % 100 == 0:
            logging.debug(' | {} documents parsed.'.format(counter))
    db.commit()

def migrate_reviews():
    logging.info('Migrating Reviews.')
    db = sqlite3.connect(DB_BOT)
    cursor = db.cursor()
    cursor.execute('DROP TABLE {table}'.format(DB_TABLE))
    cursor.execute('ATTACH {db} AS tmp'.format(DB_TMP))
    cursor.execute('INSERT INTO reviews SELECT * FROM tmp.{table}'.format(DB_TABLE))
    db.commit()
    db.close()

# Temporary solution
def migration_succeeded(cursor):
    db = sqlite3.connect(DB_BOT)
    cursor = db.cursor()
    count = cursor.execute('SELECT COUNT(*) FROM {table}'.format(DB_TABLE))
    db.close()
    return count > 8000

logging.basicConfig(format = '{asctime} | {levelname:<8} | {message}', style='{')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
req_logger = logging.getLogger('requests')
req_logger.propagate = False

download()
tmp_db = create_tmp_db()
with open(CSV_ARCHIVE, 'r') as archive:
    parse(archive, tmp_db)
shutil.copy(DB_BOT, DB_BK)
migrate_reviews()
if not migration_succeeded():
    logging.warning('Migration was not successfull. Recovering previous database.')
    os.remove(DB_BOT)
    shutil.copy(DB_BK, DB_BOT)
else:
    logging.info('Migration successfull.')

logging.debug('Cleaning up..')
os.remove(DB_BK)
os.remove(DB_TMP)
os.remove(CSV_ARCHIVE)