import unittest
import configparser
import sys
sys.path.insert(0, '..')
from ytmusicapi.ytmusic import YTMusic

config = configparser.RawConfigParser()
config.read('./test.cfg', 'utf-8')

youtube = YTMusic()
youtube_auth = YTMusic(config['auth']['headers_file'])
youtube_brand = YTMusic(config['auth']['headers'], config['auth']['brand_account'])


class TestYTMusic(unittest.TestCase):
    def test_init(self):
        self.assertRaises(Exception, YTMusic, "{}")

    def test_setup(self):
        YTMusic.setup(config['auth']['headers_file'], config['auth']['headers_raw'])

    ###############
    # BROWSING
    ###############

    def test_search(self):
        query = "Oasis Wonderwall"
        self.assertRaises(Exception, youtube_auth.search, query, "song")
        results = youtube_auth.search(query)
        self.assertGreater(len(results), 0)
        results = youtube_auth.search(query, 'songs')
        self.assertGreater(len(results), 0)
        results = youtube_auth.search(query, 'videos')
        self.assertGreater(len(results), 0)
        results = youtube_auth.search(query, 'albums')
        self.assertGreater(len(results), 0)
        results = youtube_auth.search(query, 'artists')
        self.assertGreater(len(results), 0)
        results = youtube_auth.search(query, 'playlists')
        self.assertGreater(len(results), 0)

    def test_get_artist(self):
        results = youtube.get_artist("UCmMUZbaYdNH0bEd1PAlAqsA")
        self.assertEqual(len(results), 7)

    def test_get_artist_albums(self):
        artist = youtube.get_artist("UCAeLFBCQS7FvI8PvBrWvSBg")
        results = youtube.get_artist_albums(artist['albums']['browseId'],
                                            artist['albums']['params'])
        self.assertGreater(len(results), 0)

    def test_get_artist_singles(self):
        artist = youtube_auth.get_artist("UCAeLFBCQS7FvI8PvBrWvSBg")
        results = youtube_auth.get_artist_albums(artist['singles']['browseId'],
                                                 artist['singles']['params'])
        self.assertGreater(len(results), 0)

    def test_get_album(self):
        results = youtube.get_album("MPREb_BQZvl3BFGay")
        self.assertEqual(len(results), 8)
        self.assertEqual(len(results['tracks']), 7)

    ###############
    # LIBRARY
    ###############

    def test_get_library_playlists(self):
        playlists = youtube_brand.get_library_playlists(50)
        self.assertGreater(len(playlists), 0)

    def test_get_library_songs(self):
        songs = youtube_brand.get_library_songs(200)
        self.assertGreater(len(songs), 0)

    def test_get_library_albums(self):
        albums = youtube_brand.get_library_albums(50)
        self.assertGreater(len(albums), 0)

    def test_get_library_artists(self):
        artists = youtube_brand.get_library_artists(50)
        self.assertGreater(len(artists), 0)

    def test_get_library_subscriptions(self):
        artists = youtube_brand.get_library_subscriptions(50)
        self.assertGreater(len(artists), 0)

    def test_get_liked_songs(self):
        songs = youtube_brand.get_liked_songs(200)
        self.assertGreater(len(songs['tracks']), 100)

    def test_get_history(self):
        songs = youtube_auth.get_history()
        self.assertGreater(len(songs), 0)

    def test_rate_song(self):
        response = youtube_auth.rate_song('ZrOKjDZOtkA', 'LIKE')
        self.assertIn('actions', response)
        response = youtube_auth.rate_song('ZrOKjDZOtkA', 'INDIFFERENT')
        self.assertIn('actions', response)

    def test_rate_playlist(self):
        response = youtube_auth.rate_playlist('OLAK5uy_l3g4WcHZsEx_QuEDZzWEiyFzZl6pL0xZ4',
                                              'DISLIKE')
        self.assertIn('actions', response)
        response = youtube_auth.rate_playlist('OLAK5uy_l3g4WcHZsEx_QuEDZzWEiyFzZl6pL0xZ4',
                                              'INDIFFERENT')
        self.assertIn('actions', response)

    def test_subscribe_artists(self):
        youtube_auth.subscribe_artists(['UCmMUZbaYdNH0bEd1PAlAqsA', 'UCEPMVbUzImPl4p8k4LkGevA'])
        youtube_auth.unsubscribe_artists(['UCmMUZbaYdNH0bEd1PAlAqsA', 'UCEPMVbUzImPl4p8k4LkGevA'])

    ###############
    # PLAYLISTS
    ###############

    def test_get_foreign_playlist(self):
        playlist = youtube.get_playlist("PLQwVIlKxHM6qv-o99iX9R85og7IzF9YS_", 300)
        self.assertGreater(len(playlist['tracks']), 200)

    def test_get_owned_playlist(self):
        playlist = youtube_auth.get_playlist(config['playlists']['own'], 300)
        self.assertGreater(len(playlist['tracks']), 200)

    def test_edit_playlist(self):
        playlist = youtube_auth.get_playlist(config['playlists']['own'])
        response = youtube_auth.edit_playlist(playlist['id'],
                                              title='',
                                              description='',
                                              privacyStatus='PRIVATE',
                                              moveItem=(playlist['tracks'][1]['setVideoId'],
                                                        playlist['tracks'][0]['setVideoId']))
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Playlist edit failed")
        youtube_auth.edit_playlist(playlist['id'],
                                   title=playlist['title'],
                                   description=playlist['description'],
                                   privacyStatus=playlist['privacy'],
                                   moveItem=(playlist['tracks'][0]['setVideoId'],
                                             playlist['tracks'][1]['setVideoId']))
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Playlist edit failed")

    # end to end test adding playlist, adding item, deleting item, deleting playlist
    def test_end2end(self):
        playlistId = youtube_auth.create_playlist(
            "test",
            "test description",
            source_playlist="OLAK5uy_lGQfnMNGvYCRdDq9ZLzJV2BJL2aHQsz9Y")
        self.assertEqual(len(playlistId), 34, "Playlist creation failed")
        response = youtube_auth.add_playlist_items(playlistId, ['y0Hhvtmv0gk'])
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Adding playlist item failed")
        playlist = youtube_auth.get_playlist(playlistId)
        self.assertEqual(len(playlist['tracks']), 41, "Getting playlist items failed")
        response = youtube_auth.remove_playlist_items(playlistId, playlist['tracks'])
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Playlist item removal failed")
        response = youtube_auth.delete_playlist(playlistId)
        self.assertEqual(response['command']['handlePlaylistDeletionCommand']['playlistId'],
                         playlistId, "Playlist removal failed")

    ###############
    # UPLOADS
    ###############

    def test_get_library_upload_songs(self):
        results = youtube_auth.get_library_upload_songs(126)
        self.assertGreater(len(results), 100)

    def test_get_library_upload_albums(self):
        results = youtube_auth.get_library_upload_albums(50)
        self.assertGreater(len(results), 25)

    def test_get_library_upload_artists(self):
        results = youtube_auth.get_library_upload_artists(50)
        self.assertGreater(len(results), 25)

    def test_upload_song(self):
        self.assertRaises(Exception, youtube_auth.upload_song, 'song.wav')
        response = youtube_auth.upload_song(config['uploads']['file'])
        self.assertEqual(response.status_code, 409)

    def test_delete_uploaded_song(self):
        results = youtube_auth.get_library_upload_songs()
        response = youtube_auth.delete_uploaded_song(results[0])
        self.assertEqual(response, 'STATUS_SUCCEEDED')


if __name__ == '__main__':
    unittest.main()
