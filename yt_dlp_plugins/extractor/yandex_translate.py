import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "\\..\\yandex\\")
import yandex

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.extractor.youtube import YoutubeIE

class YandexTranslateIE(InfoExtractor):
    _WORKING = False
    _VALID_URL = r'YT:.*'
    _ENABLED = False


    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def _real_extract(self, url):
        self.to_screen('URL "%s" successfully captured' % url)
        if YoutubeIE.suitable(url[3:]):
          video_id = YoutubeIE._match_id(url[3:])
          vidTr = yandex.requestVideoTranslation(self, f'https://youtu.be/{video_id}', video_id)
          subTr = yandex.requestSubtitlesTranslation(self, f'https://youtu.be/{video_id}', video_id)
        else:
          raise Exception
        info = {
          "_type": "video",
          "url":url,
          "id": video_id,
          "title": f"Yandex translation",
          "duration": vidTr.duration,
          "formats": None if vidTr.status!=1 else [{
            "url": vidTr.url,
            "ext": "mp3",
            "format": "MPEG Audio",
            "format_id": "YT",
            "format_note": "Yandex translation",
            "audio_channels": 1,
            "vcodec": None,
            "acodec": "LAME3.1",
            "abr":128,
            "container":"mp3",
            "language":"ru",
            "http_headers":{"User-Agent": yandex._yandexUserAgent},
          }],
          "subtitles": {x.translatedLanguage:[{
            "ext": "YTjson",
            "url": x.translatedUrl,
            "name": f'{x.language}->{x.translatedLanguage}',
            "http_headers":{"User-Agent": yandex._yandexUserAgent},
          }] for x in subTr.subtitles}
        }
        return info
