# API Documentation

## Authentication

All endpoints except `/auth/oauth-url` and `/auth/login` require authentication. Include an Authorization header with a Bearer token:

```http
Authorization: Bearer your_access_token
```

### Get OAuth URL

```http
GET /api/v1/auth/oauth-url
```

Returns the OAuth2 authorization URL for user authentication.

### Login

```http
POST /api/v1/auth/login
```

Exchange authorization code for access token.

**Parameters:**

- `code` (string, required): The authorization code from OAuth flow

### Get Current User

```http
GET /api/v1/auth/me
```

Get current user information.

**Headers:**

- `Authorization`: Bearer token

## Browse

### Get Home Content

```http
GET /api/v1/browse/home
```

Get personalized home page content.

### Get Artist

```http
GET /api/v1/browse/artists/{channel_id}
```

Get artist details and content.

### Get Album

```http
GET /api/v1/browse/albums/{browse_id}
```

Get album details and tracks.

### Get Playlist

```http
GET /api/v1/browse/playlists/{playlist_id}
```

Get playlist details and tracks.

### Get Song

```http
GET /api/v1/browse/songs/{video_id}
```

Get song details.

## Library

### Get Library Playlists

```http
GET /api/v1/library/playlists
```

Get user's library playlists.

### Get Library Songs

```http
GET /api/v1/library/songs
```

Get songs in user's library.

### Get Library Albums

```http
GET /api/v1/library/albums
```

Get albums in user's library.

### Get Library Artists

```http
GET /api/v1/library/artists
```

Get artists in user's library.

### Get Liked Songs

```http
GET /api/v1/library/liked
```

Get user's liked songs.

### Get History

```http
GET /api/v1/library/history
```

Get user's watch history.

### Add History Item

```http
POST /api/v1/library/history/add
```

Add an item to watch history.

**Body:**

```json
{
    "video_id": "string"
}
```

### Remove History Items

```http
POST /api/v1/library/history/remove
```

Remove items from watch history.

**Body:**

```json
{
    "video_ids": ["string"]
}
```

## Playlists

### Create Playlist

```http
POST /api/v1/playlists/create
```

Create a new playlist.

**Body:**

```json
{
    "title": "string",
    "description": "string",
    "privacy_status": "PRIVATE | PUBLIC | UNLISTED",
    "video_ids": ["string"],
    "source_playlist": "string"
}
```

### Edit Playlist

```http
POST /api/v1/playlists/{playlist_id}/edit
```

Edit playlist details.

**Body:**

```json
{
    "title": "string",
    "description": "string",
    "privacy_status": "PRIVATE | PUBLIC | UNLISTED",
    "move_item": ["string", "string"],
    "add_playlist_id": "string",
    "add_to_top": true
}
```

### Delete Playlist

```http
DELETE /api/v1/playlists/{playlist_id}
```

Delete a playlist.

### Add Playlist Items

```http
POST /api/v1/playlists/{playlist_id}/items
```

Add items to a playlist.

**Body:**

```json
{
    "video_ids": ["string"]
}
```

### Remove Playlist Items

```http
DELETE /api/v1/playlists/{playlist_id}/items
```

Remove items from a playlist.

**Body:**

```json
{
    "video_ids": ["string"]
}
```

## Search

### Search Content

```http
GET /api/v1/search
```

Search for content.

**Parameters:**

- `query` (string, required): Search query
- `filter` (string, optional): Filter type (songs, videos, albums, artists, playlists)
- `scope` (string, optional): Search scope (library, uploads)
- `limit` (integer, optional, default=20): Maximum number of results

### Get Search Suggestions

```http
GET /api/v1/search/suggestions
```

Get search suggestions.

**Parameters:**

- `query` (string, required): Input query

### Remove Search Suggestions

```http
POST /api/v1/search/suggestions/remove
```

Remove search suggestions.

**Body:**

```json
{
    "suggestions": [
        {"text": "string"}
    ]
}
```

## Error Responses

All endpoints may return these error responses:

### 401 Unauthorized

```json
{
    "detail": "Not authenticated"
}
```

### 403 Forbidden

```json
{
    "detail": "Not enough permissions"
}
```

### 404 Not Found

```json
{
    "detail": "Resource not found"
}
```

### 422 Validation Error

```json
{
    "detail": [
        {
            "loc": ["string"],
            "msg": "string",
            "type": "string"
        }
    ]
}
```
