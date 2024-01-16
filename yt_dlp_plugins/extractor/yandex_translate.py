import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "\\..\\yandex\\")
import yandex

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.extractor.youtube import YoutubeIE

def getYT (url, dld):
  test = YoutubeIE()
  test.set_downloader(dld)
  data = test.extract(url)


class YandexTranslateIE(InfoExtractor):
    _WORKING = False
    _VALID_URL = r'.*'
    _ENABLED = False


    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def _real_extract(self, url):
        self.to_screen('URL "%s" successfully captured' % url)
        if YoutubeIE.suitable(url):
          tmpIE = YoutubeIE()
          tmpIE.set_downloader(self._downloader)
          video_id = tmpIE._match_id(url)
          info = tmpIE.extract(url)
          vidTr = yandex.requestVideoTranslation(self, f'https://youtu.be/{video_id}', video_id)
          if vidTr.status == 2:
            self.report_warning(f"Video translate delayed. Please wait {vidTr.remainingTime}s")
          subTr = yandex.requestSubtitlesTranslation(self, f'https://youtu.be/{video_id}', video_id)
        else:
          raise Exception
        if info is None: info = { "_type": "video", "url":url, "id": video_id, "title": f"Yandex translation", "duration": vidTr.duration}
        if not "formats" in info:  info["formats"]=[]
        if not "subtitles" in info: info["subtitles"]={}
        if vidTr.status==1: info["formats"].append({"url": vidTr.url, "ext": "mp3", "format": "MPEG Audio",
                                "format_id": "YT", "format_note": "Yandex translation", "audio_channels": 1,
                                "vcodec": 'none', "acodec": "LAME3.1", "abr":128, "container":"mp3", "language":"ru",
                                "http_headers":{"User-Agent": yandex._yandexUserAgent}})
        if subTr.subtitles:
          for subLang in subTr.subtitles:
            if not subLang.translatedLanguage in info["subtitles"]: info["subtitles"][subLang.translatedLanguage] = []
            info["subtitles"][subLang.translatedLanguage].append({"ext": "YTjson", "url": subLang.translatedUrl, "name": f'{subLang.language}->{subLang.translatedLanguage}',
                                               "http_headers":{"User-Agent": yandex._yandexUserAgent}})
        return info
