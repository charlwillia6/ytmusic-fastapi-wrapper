import json
from ytmusicapi import YTMusic
from typing import Dict, Any, Optional, List, cast, Union, Sequence, Tuple, Literal
from app.schemas.models import CredentialsModel

# Define order types
LibraryOrderType = Literal["a_to_z", "z_to_a", "recently_added"]
ArtistOrderType = Literal["Recency", "Popularity", "Alphabetical order"]

class YTMusicService:
    def __init__(self, credentials: CredentialsModel):
        """Initialize YTMusic service with credentials."""
        self.credentials = credentials
        self.client = self._create_client()

    def _create_client(self) -> YTMusic:
        """Create YTMusic client from credentials."""
        oauth_dict = {
            "token": self.credentials.token,
            "refresh_token": self.credentials.refresh_token,
            "token_uri": self.credentials.token_uri,
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "scopes": self.credentials.scopes if self.credentials.scopes else []
        }
        return YTMusic(auth=json.dumps(oauth_dict))

    def search(
        self,
        query: str,
        filter: Optional[str] = None,
        scope: Optional[str] = None,
        limit: int = 20,
        ignore_spelling: bool = False
    ) -> List[Dict[str, Any]]:
        """Search for songs, videos, albums, artists, or playlists.
        
        Args:
            query: Query string
            filter: Filter for item types. Allowed values: songs, videos, albums, artists, playlists, community_playlists, featured_playlists, uploads
            scope: Search scope. Allowed values: library, uploads
            limit: Number of search results to return
            ignore_spelling: Whether to ignore YTM spelling suggestions
        """
        kwargs = {
            "query": query,
            "limit": limit,
            "ignore_spelling": ignore_spelling
        }
        if filter is not None:
            kwargs["filter"] = filter
        if scope is not None:
            kwargs["scope"] = scope
        return self.client.search(**kwargs)

    def get_search_suggestions(self, query: str, detailed_runs: bool = False) -> Union[List[str], List[Dict[str, Any]]]:
        """Get search suggestions.
        
        Args:
            query: Query string
            detailed_runs: Whether to return detailed runs of each suggestion
        """
        return self.client.get_search_suggestions(query, detailed_runs=detailed_runs)

    def remove_search_suggestions(self) -> bool:
        """Remove search suggestions."""
        try:
            self.client.remove_search_suggestions(suggestions=[])
            return True
        except Exception:
            return False

    def get_home(self) -> List[Dict[str, Any]]:
        """Get home page content."""
        return self.client.get_home()

    def get_artist(self, channel_id: str = "", browse_id: Optional[str] = None) -> Dict[str, Any]:
        """Get artist details.
        
        Args:
            channel_id: Channel ID of the artist. One of channel_id or browse_id must be provided.
            browse_id: Browse ID of the artist. One of channel_id or browse_id must be provided.
        """
        kwargs = {}
        if channel_id:
            kwargs["channelId"] = channel_id
        if browse_id:
            kwargs["browseId"] = browse_id
        return self.client.get_artist(**kwargs)

    def get_artist_albums(
        self,
        channel_id: str,
        limit: Optional[int] = None,
        order: Optional[ArtistOrderType] = None,
        params: str = ""
    ) -> Dict[str, Any]:
        """Get artist's albums.
        
        Args:
            channel_id: Channel ID of the artist
            limit: Maximum number of albums to return
            order: Order of albums. Allowed values: 'Recency', 'Popularity', 'Alphabetical order'
            params: Continuation parameters for getting more albums
        """
        result = self.client.get_artist_albums(
            channelId=channel_id,
            limit=limit,
            order=order,
            params=params
        )
        return cast(Dict[str, Any], result)

    def get_album(self, browse_id: str) -> Dict[str, Any]:
        """Get album details."""
        return self.client.get_album(browse_id)

    def get_album_browse_id(self, audio_playlist_id: str) -> Optional[str]:
        """Get album browse id.
        
        Args:
            audio_playlist_id: Audio playlist ID (starting with OLAK5uy_)
        """
        result = self.client.get_album_browse_id(audioPlaylistId=audio_playlist_id)
        return str(result) if result else None

    def get_user(self, channel_id: str) -> Dict[str, Any]:
        """Get user details."""
        result = self.client.get_user(channelId=channel_id)
        return cast(Dict[str, Any], result)

    def get_user_playlists(
        self,
        channel_id: str,
        params: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user's playlists.
        
        Args:
            channel_id: Channel ID of the user
            params: Continuation parameters for getting more playlists
        """
        kwargs = {"channelId": channel_id}
        if params is not None:
            kwargs["params"] = params
        results = self.client.get_user_playlists(**kwargs)
        return cast(List[Dict[str, Any]], results)

    def get_song(self, video_id: str) -> Dict[str, Any]:
        """Get song details.
        
        Args:
            video_id: Video ID of the song
        """
        return self.client.get_song(video_id)

    def get_song_related(self, browse_id: str) -> Dict[str, Any]:
        """Get related songs."""
        result = self.client.get_song_related(browseId=browse_id)
        return cast(Dict[str, Any], result)

    def get_lyrics(self, browse_id: str) -> Dict[str, Any]:
        """Get song lyrics."""
        result = self.client.get_lyrics(browseId=browse_id)
        return cast(Dict[str, Any], result) if result else {}

    def get_tasteprofile(self) -> Dict[str, Any]:
        """Get your taste profile."""
        result = self.client.get_tasteprofile()
        return cast(Dict[str, Any], result)

    def set_tasteprofile(self, artists: List[str]) -> bool:
        """Set your taste profile.
        
        Args:
            artists: List of artist names
        """
        try:
            result = self.client.set_tasteprofile(artists)
            return bool(result)
        except Exception:
            return False

    def get_mood_categories(self) -> List[Dict[str, Any]]:
        """Get mood categories."""
        results = self.client.get_mood_categories()
        return cast(List[Dict[str, Any]], results)

    def get_mood_playlists(self, params: str) -> List[Dict[str, Any]]:
        """Get mood playlists."""
        results = self.client.get_mood_playlists(params)
        return cast(List[Dict[str, Any]], results)

    def get_charts(self, country_code: str = "ZZ") -> Dict[str, Any]:
        """Get charts for a country."""
        results = self.client.get_charts(country_code)
        if isinstance(results, str):
            results = json.loads(results)
        return cast(Dict[str, Any], results)

    def get_watch_playlist(
        self,
        video_id: Optional[str] = None,
        playlist_id: Optional[str] = None,
        limit: int = 25,
        radio: bool = False,
        shuffle: bool = False
    ) -> Dict[str, Any]:
        """Get watch playlist."""
        result = self.client.get_watch_playlist(
            videoId=video_id or "",
            playlistId=playlist_id or "",
            limit=limit,
            radio=radio,
            shuffle=shuffle
        )
        return cast(Dict[str, Any], result)

    def get_library_playlists(self, limit: Optional[int] = 25) -> List[Dict[str, Any]]:
        """Get library playlists.
        
        Args:
            limit: Number of playlists to return
        """
        return self.client.get_library_playlists(limit=limit)

    def get_library_songs(
        self,
        limit: int = 25,
        validate_responses: bool = False,
        order: Optional[LibraryOrderType] = None
    ) -> List[Dict[str, Any]]:
        """Get songs in the user's library.
        
        Args:
            limit: Number of songs to retrieve. Default: 25
            validate_responses: Validate and retry if songs are missing. Default: False
            order: Order of songs. Allowed values: a_to_z, z_to_a, recently_added. Default: Default order
        """
        result = self.client.get_library_songs(
            limit=limit,
            validate_responses=validate_responses,
            order=order
        )
        return cast(List[Dict[str, Any]], result)

    def get_library_albums(self, limit: int = 25, order: Optional[LibraryOrderType] = None) -> List[Dict[str, Any]]:
        """Get albums in the user's library.
        
        Args:
            limit: Number of albums to return. Default: 25
            order: Order of albums. Allowed values: a_to_z, z_to_a, recently_added. Default: Default order
        """
        result = self.client.get_library_albums(limit=limit, order=order)
        return cast(List[Dict[str, Any]], result)

    def get_library_artists(self, limit: int = 25, order: Optional[LibraryOrderType] = None) -> List[Dict[str, Any]]:
        """Get artists of songs in the user's library.
        
        Args:
            limit: Number of artists to return. Default: 25
            order: Order of artists. Allowed values: a_to_z, z_to_a, recently_added. Default: Default order
        """
        result = self.client.get_library_artists(limit=limit, order=order)
        return cast(List[Dict[str, Any]], result)

    def get_library_subscriptions(self, limit: int = 25, order: Optional[LibraryOrderType] = None) -> List[Dict[str, Any]]:
        """Get artists the user has subscribed to.
        
        Args:
            limit: Number of artists to return. Default: 25
            order: Order of artists. Allowed values: a_to_z, z_to_a, recently_added. Default: Default order
        """
        result = self.client.get_library_subscriptions(limit=limit, order=order)
        return cast(List[Dict[str, Any]], result)

    def get_liked_songs(self, limit: int = 100) -> Dict[str, Any]:
        """Get liked songs."""
        return self.client.get_liked_songs(limit=limit)

    def get_history(self) -> List[Dict[str, Any]]:
        """Get watch history."""
        return self.client.get_history()

    def add_history_item(self, song: Dict[str, Any]) -> Dict[str, Any]:
        """Add an item to the account's history.
        
        Args:
            song: Dictionary as returned by get_song
        """
        result = self.client.add_history_item(song)
        return cast(Dict[str, Any], result)

    def remove_history_items(self, feedback_tokens: List[str]) -> Dict[str, Any]:
        """Remove videos from your history.
        
        Args:
            feedback_tokens: List of feedback tokens
        """
        result = self.client.remove_history_items(feedbackTokens=feedback_tokens)
        return cast(Dict[str, Any], result)

    def rate_song(self, video_id: str, rating: str = "INDIFFERENT") -> Optional[Dict[str, Any]]:
        """Rate a song.
        
        Args:
            video_id: Video ID
            rating: One of LIKE, DISLIKE, INDIFFERENT. Default: INDIFFERENT
        """
        result = self.client.rate_song(videoId=video_id, rating=rating)
        return cast(Optional[Dict[str, Any]], result)

    def edit_song_library_status(self, feedback_tokens: Optional[List[str]] = None) -> Dict[str, Any]:
        """Edit song library status.
        
        Args:
            feedback_tokens: List of feedback tokens
        """
        result = self.client.edit_song_library_status(feedbackTokens=feedback_tokens if feedback_tokens else None)
        return cast(Dict[str, Any], result)

    def rate_playlist(self, playlist_id: str, rating: str = "INDIFFERENT") -> Dict[str, Any]:
        """Rate a playlist.
        
        Args:
            playlist_id: Playlist ID
            rating: One of LIKE, DISLIKE, INDIFFERENT. Default: INDIFFERENT
        """
        result = self.client.rate_playlist(playlistId=playlist_id, rating=rating)
        return cast(Dict[str, Any], result)

    def subscribe_artists(self, channel_ids: List[str]) -> Dict[str, Any]:
        """Subscribe to artists.
        
        Args:
            channel_ids: List of channel IDs
        """
        result = self.client.subscribe_artists(channelIds=channel_ids)
        return cast(Dict[str, Any], result)

    def unsubscribe_artists(self, channel_ids: List[str]) -> Dict[str, Any]:
        """Unsubscribe from artists.
        
        Args:
            channel_ids: List of channel IDs
        """
        result = self.client.unsubscribe_artists(channelIds=channel_ids)
        return cast(Dict[str, Any], result)

    def get_playlist(
        self,
        playlist_id: str,
        limit: Optional[int] = 100,
        related: bool = False,
        suggestions_limit: int = 0
    ) -> Dict[str, Any]:
        """Get playlist details.
        
        Args:
            playlist_id: Playlist ID
            limit: Number of tracks to return
            related: Whether to fetch related content
            suggestions_limit: Number of suggestions to return
        """
        return self.client.get_playlist(
            playlistId=playlist_id,
            limit=limit,
            related=related,
            suggestions_limit=suggestions_limit
        )

    def create_playlist(
        self,
        title: str,
        description: str,
        privacy_status: str = "PRIVATE",
        video_ids: Optional[List[str]] = None,
        source_playlist: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """Create a new playlist.
        
        Args:
            title: Playlist title
            description: Playlist description
            privacy_status: PRIVATE, PUBLIC, or UNLISTED. Default: PRIVATE
            video_ids: List of video IDs to add
            source_playlist: Another playlist to copy songs from
        """
        result = self.client.create_playlist(
            title=title,
            description=description,
            privacy_status=privacy_status,
            video_ids=video_ids,
            source_playlist=source_playlist
        )
        return result

    def edit_playlist(
        self,
        playlist_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        privacy_status: Optional[str] = None,
        move_item: Optional[Union[str, Tuple[str, str]]] = None,
        add_playlist_id: Optional[str] = None,
        add_to_top: Optional[bool] = None
    ) -> Union[str, Dict[str, Any]]:
        """Edit a playlist.
        
        Args:
            playlist_id: Playlist ID
            title: New title
            description: New description
            privacy_status: New privacy status
            move_item: Move item tuple (setVideoId, movedSetVideoIdSuccessor)
            add_playlist_id: Add songs from another playlist
            add_to_top: Whether to add songs to top of playlist
        """
        result = self.client.edit_playlist(
            playlistId=playlist_id,
            title=title,
            description=description,
            privacyStatus=privacy_status,
            moveItem=move_item,
            addPlaylistId=add_playlist_id,
            addToTop=add_to_top
        )
        return result

    def delete_playlist(self, playlist_id: str) -> Union[str, Dict[str, Any]]:
        """Delete a playlist.
        
        Args:
            playlist_id: Playlist ID
        """
        result = self.client.delete_playlist(playlistId=playlist_id)
        return result

    def add_playlist_items(
        self,
        playlist_id: str,
        video_ids: Optional[List[str]] = None,
        source_playlist: Optional[str] = None,
        duplicates: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """Add items to a playlist.
        
        Args:
            playlist_id: Playlist ID
            video_ids: List of video IDs to add
            source_playlist: Another playlist to add songs from
            duplicates: Allow duplicate songs. Default: False
        """
        result = self.client.add_playlist_items(
            playlistId=playlist_id,
            videoIds=video_ids,
            source_playlist=source_playlist,
            duplicates=duplicates
        )
        return result

    def remove_playlist_items(self, playlist_id: str, videos: List[Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
        """Remove items from a playlist.
        
        Args:
            playlist_id: Playlist ID
            videos: List of video dictionaries with setVideoId
        """
        result = self.client.remove_playlist_items(playlistId=playlist_id, videos=videos)
        return result

    def get_library_upload_songs(self, limit: int = 25, order: Optional[LibraryOrderType] = None) -> List[Dict[str, Any]]:
        """Get uploaded songs.
        
        Args:
            limit: How many songs to return. None retrieves them all
            order: Order of songs. Allowed values: 'a_to_z', 'z_to_a', 'recently_added'
        """
        results = self.client.get_library_upload_songs(
            limit=limit,
            order=order
        )
        return cast(List[Dict[str, Any]], results)

    def get_library_upload_artists(self, limit: int = 25, order: Optional[LibraryOrderType] = None) -> List[Dict[str, Any]]:
        """Get uploaded artists.
        
        Args:
            limit: How many artists to return. None retrieves them all
            order: Order of artists. Allowed values: 'a_to_z', 'z_to_a', 'recently_added'
        """
        results = self.client.get_library_upload_artists(
            limit=limit,
            order=order
        )
        return cast(List[Dict[str, Any]], results)

    def get_library_upload_albums(self, limit: int = 25, order: Optional[LibraryOrderType] = None) -> List[Dict[str, Any]]:
        """Get uploaded albums.
        
        Args:
            limit: How many albums to return. None retrieves them all
            order: Order of albums. Allowed values: 'a_to_z', 'z_to_a', 'recently_added'
        """
        results = self.client.get_library_upload_albums(
            limit=limit,
            order=order
        )
        return cast(List[Dict[str, Any]], results)

    def get_library_upload_artist(self, browse_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get uploaded artist details.
        
        Args:
            browse_id: Browse id of the upload artist
            limit: Number of songs to return
        """
        results = self.client.get_library_upload_artist(browseId=browse_id, limit=limit)
        return cast(List[Dict[str, Any]], results)

    def get_library_upload_album(self, browse_id: str) -> Dict[str, Any]:
        """Get uploaded album details.
        
        Args:
            browse_id: Browse id of the upload album
        """
        result = self.client.get_library_upload_album(browseId=browse_id)
        return cast(Dict[str, Any], result)

    def upload_song(self, filepath: str) -> bool:
        """Upload a song.
        
        Args:
            filepath: Path to the music file (mp3, m4a, wma, flac or ogg)
        """
        try:
            result = self.client.upload_song(filepath)
            return result == 'STATUS_SUCCEEDED'
        except Exception:
            return False

    def delete_upload_entity(self, entity_id: str) -> bool:
        """Delete an uploaded entity.
        
        Args:
            entity_id: The entity id of the uploaded song or album
        """
        try:
            result = self.client.delete_upload_entity(entityId=entity_id)
            return result == 'STATUS_SUCCEEDED'
        except Exception:
            return False

    def get_channel(self, channel_id: str) -> Dict[str, Any]:
        """Get information about a podcast channel.
        
        Args:
            channel_id: Channel ID
        """
        return self.client.get_channel(channel_id)

    def get_channel_episodes(self, channel_id: str, params: str) -> List[Dict[str, Any]]:
        """Get all channel episodes.
        
        Args:
            channel_id: Channel ID
            params: Params obtained from get_channel
        """
        return self.client.get_channel_episodes(channel_id, params)

    def get_podcast(self, playlist_id: str, limit: Optional[int] = 100) -> Dict[str, Any]:
        """Get podcast metadata and episodes.
        
        Args:
            playlist_id: Playlist ID
            limit: How many episodes to return. None retrieves all. Default: 100
        """
        return self.client.get_podcast(playlist_id, limit=limit)

    def get_episode(self, video_id: str) -> Dict[str, Any]:
        """Get episode data for a single episode.
        
        Args:
            video_id: Video ID or browse ID (MPED...) for a single episode
        """
        return self.client.get_episode(video_id)

    def get_episodes_playlist(self, playlist_id: str = "RDPN") -> Dict[str, Any]:
        """Get all episodes in an episodes playlist.
        
        Args:
            playlist_id: Playlist ID, defaults to "RDPN", the ID of the New Episodes playlist
        """
        return self.client.get_episodes_playlist(playlist_id)

    def get_library_podcasts(self, limit: int = 25, order: Optional[LibraryOrderType] = None) -> List[Dict[str, Any]]:
        """Get podcasts the user has added to the library.
        
        Args:
            limit: Number of podcasts to return. Default: 25
            order: Order of podcasts to return. Allowed values: a_to_z, z_to_a, recently_added. Default: Default order
        """
        return self.client.get_library_podcasts(limit=limit, order=order)

    def get_saved_episodes(self, limit: int = 100) -> Dict[str, Any]:
        """Get playlist items for the 'Saved Episodes' playlist.
        
        Args:
            limit: How many items to return. Default: 100
        """
        return self.client.get_saved_episodes(limit=limit)

    def get_account_info(self) -> Dict[str, Any]:
        """Get information about the currently authenticated user's account.
        
        Returns:
            Dictionary with user's account name, channel handle, and URL of their account photo.
        """
        result = self.client.get_account_info()
        return cast(Dict[str, Any], result)

    def get_user_videos(self, channel_id: str, params: str) -> List[Dict[str, Any]]:
        """Get a list of videos for a given user.
        
        Args:
            channel_id: channelId of the user
            params: params obtained by get_user
        """
        return self.client.get_user_videos(channel_id, params)

    def get_library_channels(self, limit: int = 25, order: Optional[LibraryOrderType] = None) -> List[Dict[str, Any]]:
        """Get channels the user has added to the library.
        
        Args:
            limit: Number of channels to return
            order: Order of channels to return. Allowed values: a_to_z, z_to_a, recently_added
        """
        return self.client.get_library_channels(limit=limit, order=order)
