import sys, os, re, json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "\\..\\yandex\\")
import yandex

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.extractor.youtube import YoutubeIE
from yt_dlp.extractor.vk import VKIE

IEList = [YoutubeIE, VKIE]

class YandexTranslateIE(InfoExtractor):
    _WORKING = False
    _VALID_URL = r'^YT:.*'
    _ENABLED = False

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    @classmethod
    def suitable(cls, url):
      for ie in IEList:
        if ie.suitable(url):
          return True
      return csl._match_id(url) is None

    @classmethod
    def _match_id(cls, url):
      for ie in IEList:
        if ie.suitable(url):
          return ie._match_id(url)
      return False

    def _real_extract(self, url):
        info = None
        for ie in IEList:
          if ie.suitable(url):
            ie_tmp = ie()
            video_id = ie_tmp._match_id(url)
            if 'Youtube' in ie.ie_key():
              ie_tmp.set_downloader(self._downloader)
              yt_url = f'https://youtu.be/{video_id}'
            else:
              yt_url = url
            info = ie_tmp.extract(url)
            vid_tr = yandex.request_video_translation(self, yt_url , video_id)
            last_resp = 0
            while vid_tr["resp"].status == 2:
              last_resp = vid_tr["resp"].remainingTime
              self._sleep(vid_tr["resp"].remainingTime, video_id, f'Waiting for translation ({vid_tr["resp"].remainingTime}s)')
              vid_tr = yandex.request_video_translation(self, yt_url, video_id, first_request = False, uuid = vid_tr["uuid"])
              if last_resp == vid_tr["resp"].remainingTime:
                self.report_warning(f"Video translate delayed")
                break

            sub_tr = yandex.request_subtitles_translation(self, yt_url, video_id)
            break

        if info is None: info = { "_type": "video", "url":url, "id": video_id, "title": f"Yandex translation", "duration": vid_tr["resp"].duration}
        if not "formats" in info:  info["formats"]=[]
        if not "subtitles" in info: info["subtitles"]={}
        if vid_tr["resp"].status == 1: info["formats"].append({"url": vid_tr["resp"].url, "ext": "mp3", "format": "MPEG Audio",
                                "format_id": "YT", "format_note": "Yandex translation", "audio_channels": 1,
                                "vcodec": 'none', "acodec": "LAME3.1", "abr":128, "container":"mp3", "language":"ru",
                                "http_headers":vid_tr["headers"]})
        if sub_tr["resp"].subtitles:
          for sub_lang in sub_tr["resp"].subtitles:
            if not sub_lang.translatedLanguage in info["subtitles"]: info["subtitles"][sub_lang.translatedLanguage] = []
            info["subtitles"][sub_lang.translatedLanguage].append({"ext": "YTjson", "url": sub_lang.translatedUrl, "name": f'{sub_lang.language}->{sub_lang.translatedLanguage}',
                                               "http_headers":sub_tr["headers"]})
        if True:
          with open("info.json", "w") as f:
            json.dump(info, f, indent = 2)
        return info
