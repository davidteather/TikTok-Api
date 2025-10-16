from .comment import Comment
from .hashtag import Hashtag
from .playlist import Playlist
from .search import Search
from .sound import Sound
from .trending import Trending
from .user import User
from .video import Video

User.model_rebuild()
Comment.model_rebuild()
Hashtag.model_rebuild()
Playlist.model_rebuild()
Sound.model_rebuild()
Video.model_rebuild()
