import random
import time
import pandas as pd
import tweepy
import logging
from datetime import datetime, timedelta
from config import create_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

selected_rows = []
#In my file all data is in the Lyrics column
def lyrics_tweet(api, last_tweeted):
    if last_tweeted < datetime.now()-timedelta(hours=3):
        # Read CSV file
        df = pd.read_csv('lyricsTheQueenisDead.csv', encoding='utf-8')

        rows = list(range(0, len(df.index)))
        rows = [i for i in rows if i not in selected_rows]
        if len(rows) == 0:
            api.update_status('(crossfading audio: time for next album...) \U0001F4BD \U0001F97A \U0001F44B')
            return last_tweeted
        else:
            try:
                readRow = random.choice(rows)
                selected_rows.append(readRow)
                tweet = str(df.iat[readRow, 2])
                api.update_status(tweet)
                logger.info(f'Tweeted {tweet} at {datetime.now().strftime("%d/%m/%y, %H:%M:%S")}')
                return datetime.now()
            except Exception as e:
                logger.error('Error posting tweet', exc_info=True)
    return last_tweeted    

# Likes all mentions
def fav_tweet(api, last_id):
    logger.info('Retrieving mentions')
    # if last_id is None:
    #     last_id = 1
    new_last_id = last_id

    for mention in tweepy.Cursor(api.mentions_timeline, last_id=last_id).items():
        new_last_id = max(mention.id, new_last_id)
        # Reply or own tweet
        if mention.in_reply_to_status_id is not None or mention.user.id == api.me().id:
            continue
        if not mention.favorited:
            try:
                mention.favorite()
                logger.info(f'Liked tweet by {mention.user.name}')
            except Exception as e:
                logger.error('Error faving tweet', exc_info=True)
    return new_last_id


def main():
    api = create_api()
    last_tweeted = datetime.now() - timedelta(hours=3)
    last_id = 1

    while True:
        last_id = fav_tweet(api, last_id)
        last_tweeted = lyrics_tweet(api, last_tweeted)
        logger.info('Waiting...')
        time.sleep(60)
    
if __name__ == "__main__":
    main()