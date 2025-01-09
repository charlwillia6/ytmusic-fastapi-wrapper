# YTMusic API Usage Documentation

This document provides examples of how to use the YTMusic API endpoints. All authenticated endpoints require a `session_token` in the request headers.

For comprehensive information about the underlying YTMusic API methods and their parameters, please refer to the [official YTMusic API documentation](https://ytmusicapi.readthedocs.io/en/stable/reference/index.html).

## Table of Contents

- [YTMusic API Usage Documentation](#ytmusic-api-usage-documentation)
  - [Table of Contents](#table-of-contents)
  - [Authentication](#authentication)
    - [Login](#login)
    - [Callback](#callback)
    - [Get User](#get-user)
  - [Search and Suggestions](#search-and-suggestions)
    - [Search](#search)
    - [Get Search Suggestions](#get-search-suggestions)
    - [Remove Search Suggestions](#remove-search-suggestions)
  - [Browse](#browse)
    - [Get Home](#get-home)
    - [Get Artist](#get-artist)
    - [Get Artist Albums](#get-artist-albums)
    - [Get Album](#get-album)
    - [Get Album Browse ID](#get-album-browse-id)
    - [Get User Info](#get-user-info)
    - [Get User Videos](#get-user-videos)
    - [Get Song](#get-song)
    - [Get Related Songs](#get-related-songs)
  - [Watch](#watch)
    - [Get Watch Playlist](#get-watch-playlist)
    - [Get Lyrics](#get-lyrics)
  - [Library](#library)
    - [Get Library Playlists](#get-library-playlists)
    - [Get Library Songs](#get-library-songs)
    - [Get Liked Songs](#get-liked-songs)
    - [Get History](#get-history)
    - [Add History Item](#add-history-item)
    - [Remove History Items](#remove-history-items)
  - [Playlists](#playlists)
    - [Create Playlist](#create-playlist)
    - [Edit Playlist](#edit-playlist)
    - [Delete Playlist](#delete-playlist)
  - [Uploads](#uploads)
    - [Upload Song](#upload-song)
    - [Delete Uploaded Song](#delete-uploaded-song)
    - [Get Upload Library](#get-upload-library)
  - [Podcasts](#podcasts)
    - [Get Podcast](#get-podcast)
    - [Get Episode](#get-episode)
    - [Get Episodes Playlist](#get-episodes-playlist)
  - [Explore](#explore)
    - [Get Mood Categories](#get-mood-categories)
    - [Get Mood Playlists](#get-mood-playlists)
    - [Get Charts](#get-charts)
  - [Error Responses](#error-responses)
    - [401 Unauthorized](#401-unauthorized)
    - [400 Bad Request](#400-bad-request)
    - [500 Internal Server Error](#500-internal-server-error)

## Authentication

### Login

```http
GET /auth/login
```

Redirects to Google OAuth2 login page.

### Callback

```http
GET /auth/callback?code={auth_code}
```

Handles OAuth2 callback and returns a session token.

Response:

```json
{
    "message": "Authentication successful",
    "session_token": "uuid-token"
}
```

### Get User

```http
GET /auth/user
Headers: { "session_token": "your-session-token" }
```

Returns current user information.

Response:

```json
{
    "username": "user@example.com"
}
```

## Search and Suggestions

### Search

```http
GET /search?query=your_search_query&filter=songs&limit=20&ignore_spelling=false
Headers: { "session_token": "your-session-token" }
```

Parameters:

- `query`: Search query string
- `filter` (optional): Filter type (songs, videos, albums, artists, playlists)
- `limit` (optional): Number of results (default: 20)
- `ignore_spelling` (optional): Whether to ignore spelling suggestions (default: false)

Response:

```json
{
    "results": [
        {
            "title": "Song Title",
            "artist": "Artist Name",
            "videoId": "video-id"
        }
    ]
}
```

### Get Search Suggestions

```http
GET /search/suggestions?query=your_query
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": ["suggestion1", "suggestion2"]
}
```

### Remove Search Suggestions

```http
POST /search/suggestions/remove
Headers: { "session_token": "your-session-token" }
Body: {
    "suggestions": [{"text": "suggestion to remove"}]
}
```

Response:

```json
{
    "message": "Search suggestions removed successfully"
}
```

## Browse

### Get Home

```http
GET /browse/home?limit=3
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": [
        {
            "title": "Section Title",
            "contents": []
        }
    ]
}
```

### Get Artist

```http
GET /browse/artists/{channel_id}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "artist": {
        "name": "Artist Name",
        "description": "Artist Description",
        "songs": []
    }
}
```

### Get Artist Albums

```http
GET /browse/artists/{artist_id}/albums?params=albums&limit=25
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": [
        {
            "title": "Album Title",
            "year": "2023"
        }
    ]
}
```

### Get Album

```http
GET /browse/albums/{browse_id}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "album": {
        "title": "Album Title",
        "artist": "Artist Name",
        "tracks": []
    }
}
```

### Get Album Browse ID

```http
GET /browse/albums/browse-id/{video_id}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": "browse-id"
}
```

### Get User Info

```http
GET /browse/users/{channel_id}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": {
        "name": "User Name",
        "playlists": []
    }
}
```

### Get User Videos

```http
GET /browse/users/{channel_id}/videos
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": [
        {
            "title": "Video Title",
            "videoId": "video-id"
        }
    ]
}
```

### Get Song

```http
GET /browse/songs/{video_id}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": {
        "title": "Song Title",
        "artist": "Artist Name"
    }
}
```

### Get Related Songs

```http
GET /browse/songs/{video_id}/related
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": [
        {
            "title": "Related Song",
            "artist": "Artist Name"
        }
    ]
}
```

## Watch

### Get Watch Playlist

```http
GET /watch/playlist?video_id=video_id&playlist_id=playlist_id&limit=25&radio=false&shuffle=false
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "playlist": {
        "tracks": [
            {
                "title": "Song Title",
                "videoId": "video-id"
            }
        ]
    }
}
```

### Get Lyrics

```http
GET /watch/lyrics/{browse_id}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "lyrics": {
        "text": "Song lyrics..."
    }
}
```

## Library

### Get Library Playlists

```http
GET /library/playlists?limit=25
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": [
        {
            "title": "Playlist Title",
            "playlistId": "playlist-id"
        }
    ]
}
```

### Get Library Songs

```http
GET /library/songs?limit=25&order=recently_added
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": [
        {
            "title": "Song Title",
            "artist": "Artist Name"
        }
    ]
}
```

### Get Liked Songs

```http
GET /library/liked-songs?limit=100
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": {
        "tracks": [
            {
                "title": "Song Title",
                "videoId": "video-id"
            }
        ]
    }
}
```

### Get History

```http
GET /library/history
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": [
        {
            "title": "Song Title",
            "played": "timestamp"
        }
    ]
}
```

### Add History Item

```http
POST /library/history/add
Headers: { "session_token": "your-session-token" }
Body: {
    "video_id": "video-id"
}
```

Response:

```json
{
    "message": "History item added successfully"
}
```

### Remove History Items

```http
POST /library/history/remove
Headers: { "session_token": "your-session-token" }
Body: {
    "video_ids": ["video-id-1", "video-id-2"]
}
```

Response:

```json
{
    "message": "History items removed successfully"
}
```

## Playlists

### Create Playlist

```http
POST /playlists/create
Headers: { "session_token": "your-session-token" }
Parameters:
- title: Playlist title
- description: Playlist description
- privacy_status: PRIVATE/PUBLIC/UNLISTED
- video_ids: Optional list of video IDs
- source_playlist: Optional source playlist ID
```

Response:

```json
{
    "playlist_id": "new-playlist-id"
}
```

### Edit Playlist

```http
POST /playlists/{playlist_id}/edit
Headers: { "session_token": "your-session-token" }
Parameters:
- title: New title
- description: New description
- privacy_status: New privacy status
- move_item: Item to move
- add_playlist_id: Playlist to add
- add_to_top: Whether to add to top
```

Response:

```json
{
    "message": "Playlist edited successfully"
}
```

### Delete Playlist

```http
DELETE /playlists/{playlist_id}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "message": "Playlist deleted successfully"
}
```

## Uploads

### Upload Song

```http
POST /uploads/songs
Headers: { "session_token": "your-session-token" }
Parameters:
- filepath: Path to the song file
```

Response:

```json
{
    "message": "Song uploaded successfully"
}
```

### Delete Uploaded Song

```http
DELETE /uploads/songs/{song_id}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "message": "Song deleted successfully"
}
```

### Get Upload Library

```http
GET /uploads/songs
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": [
        {
            "title": "Uploaded Song",
            "artist": "Artist Name"
        }
    ]
}
```

## Podcasts

### Get Podcast

```http
GET /podcasts/{podcast_id}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": {
        "title": "Podcast Title",
        "description": "Podcast Description"
    }
}
```

### Get Episode

```http
GET /podcasts/episodes/{episode_id}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": {
        "title": "Episode Title",
        "description": "Episode Description"
    }
}
```

### Get Episodes Playlist

```http
GET /podcasts/episodes/playlist/{episode_id}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": {
        "title": "Episodes Playlist",
        "episodes": []
    }
}
```

## Explore

### Get Mood Categories

```http
GET /explore/moods
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": [
        {
            "title": "Mood Category",
            "params": "category-params"
        }
    ]
}
```

### Get Mood Playlists

```http
GET /explore/moods/{params}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": [
        {
            "title": "Mood Playlist",
            "playlistId": "playlist-id"
        }
    ]
}
```

### Get Charts

```http
GET /explore/charts/{country_code}
Headers: { "session_token": "your-session-token" }
```

Response:

```json
{
    "results": {
        "trends": [
            {
                "title": "Trending Song",
                "rank": "1"
            }
        ]
    }
}
```

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized

```json
{
    "detail": "Invalid or expired session token"
}
```

### 400 Bad Request

```json
{
    "detail": "Invalid request parameters"
}
```

### 500 Internal Server Error

```json
{
    "detail": "Error message from YTMusic API"
}
```
