"""
This module contains classes that all represent different types of data sent back by the TikTok servers.

The files within in module correspond to what type of object is described and all have different methods associated with them.


### How To Interpret TikTok Data
There are quite a few ambigious keys in the JSON that TikTok returns so here's a section that tries to document some of them.

**Note**: These are incomplete, if you get confused about something feel free to add it here as a PR once you figure it out.

| JSON Key         | Description |
|------------------|-------------|
| createTime | The [unix epoch](https://docs.python.org/3/library/datetime.html#datetime.date.fromtimestamp) of creation, all other time fields are also unix epochs.  |
| secUid & (userId or id) | Two different unique attributes that are used in conjunction to reference a specific account, so if you're storing users somewhere in a database, you should store both secUid & userId. |
| id | A unique attribute used to reference a non-user object like video, hashtag, etc |
| diggCount | The likes for a specific video. |
| digged | Used to check if the current user has liked/digged a video, this will always be false since this package doesn't support logged-in user functions. |
"""
