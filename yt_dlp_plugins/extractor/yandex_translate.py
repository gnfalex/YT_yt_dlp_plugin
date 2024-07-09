import sys, os, re, json
from uuid import uuid4 as getUUID
import hmac, hashlib

from yt_dlp.utils import ExtractorError
from yt_dlp.extractor.common import InfoExtractor
from ..postprocessor.yandex_translate import YandexTranslateSubtitleFixPP, YandexTranslateMergePP, YandexTranslateAutoAddPP
from yt_dlp.extractor._extractors import *

from ..extractor import yandex_pb2 


_workerHost = "api.browser.yandex.ru"
_yandexHmacKey = b"bt8xH3VOlb4mqf0nqAibnDOoiPlXsisf"
_yandexUserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/24.4.0.0 Safari/537.36"
_getSignature = lambda body: hmac.new(_yandexHmacKey, msg=body, digestmod=hashlib.sha256).hexdigest()

def request_subtitles_translation(self, sub_url, video_id, request_lang="en", first_request = True, uuid = getUUID().hex):
  subReq = yandex_pb2.VideoSubtitlesRequest()
  subReq.url = sub_url; subReq.language = request_lang
  body = subReq.SerializeToString()

  headers = {"Accept": "application/x-protobuf", "Content-Type": "application/x-protobuf", "Accept-Language": "en",
             "User-Agent": _yandexUserAgent, "Vsubs-Signature": _getSignature(body), "Sec-Vsubs-Token": uuid}
  binResp = self._request_webpage( f"https://{_workerHost}/video-subtitles/get-subtitles", video_id, data = body, headers = headers)

  translateResponse = yandex_pb2.VideoSubtitlesResponse()
  try:
    translateResponse.ParseFromString(binResp.read())
  except:
    self.report_warning ("Yandex subtitles error")
  finally:
    return {"resp":translateResponse, "uuid":uuid, "headers":headers}

def request_video_translation(self, video_url, video_id, duration = 341, request_lang="en", response_lang="ru", first_request = True, uuid = getUUID().hex):
  videoReq = yandex_pb2.VideoTranslationRequest()
  videoReq.duration = duration ; videoReq.url = video_url ; videoReq.language = request_lang
  videoReq.responseLanguage = response_lang ; videoReq.firstRequest = first_request
  videoReq.unknown2 = 1; videoReq.unknown3 = videoReq.unknown4 = videoReq.unknown5 = 0
  body = videoReq.SerializeToString()

  headers = {"Accept": "application/x-protobuf", "Content-Type": "application/x-protobuf", "Accept-Language": "en",
             "User-Agent": _yandexUserAgent, "Vtrans-Signature": _getSignature(body), "Sec-Vtrans-Token": uuid}
  binResp = self._request_webpage( f"https://{_workerHost}/video-translation/translate", video_id, data = body, headers = headers)

  translateResponse = yandex_pb2.VideoTranslationResponse()
  try:
    translateResponse.ParseFromString(binResp.read())
  except:
    self.report_warning ("Yandex video translation error")
  finally:
    return {"resp":translateResponse, "uuid":uuid, "headers":headers}

IEList = [klass for name, klass in globals().items() if name.endswith('IE') and not name in ['GenericIE', 'YandexTranslateIE']]
IEList.append(GenericIE)

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
            ie_tmp = ie(self._downloader)
            video_id = ie_tmp._match_id(url)
            if 'Youtube' in ie.ie_key():
              yt_url = f'https://youtu.be/{video_id}' # Subtitle glitch
            else:
              yt_url = url
            info = ie_tmp.extract(url)
            #print (info)
            vid_tr = request_video_translation(self, yt_url , video_id)
            last_resp = 0
            while vid_tr["resp"].status == 2:
              last_resp = vid_tr["resp"].remainingTime
              self._sleep(vid_tr["resp"].remainingTime, video_id, f'Waiting for translation ({vid_tr["resp"].remainingTime}s)')
              vid_tr = request_video_translation(self, yt_url, video_id, first_request = False, uuid = vid_tr["uuid"])
              if last_resp == vid_tr["resp"].remainingTime:
                #self.report_warning(f"Video translate delayed")
                raise ExtractorError(f'Video translate delayed {video_id}. Please try later', expected=True)
                break
            sub_tr = request_subtitles_translation(self, yt_url, video_id)
            break

        if info is None: info = { "_type": "video", "url":url, "id": video_id, "title": f"Yandex translation", "duration": vid_tr["resp"].duration}
        if not "formats" in info:  info["formats"]=[]
        if not "subtitles" in info: info["subtitles"]={}
        if vid_tr["resp"].status == 1:
          orig_volume = self._configuration_arg('orig_volume', [0.4])[0]
          codec = self._configuration_arg('codec', ['libopus'])[0]
          self.to_screen("Audio translation available")
          info["formats"].append({"url": vid_tr["resp"].url, "ext": "mp3", "format": "MPEG Audio",
                                "format_id": "YT", "format_note": "Yandex translation", "audio_channels": 1,
                                "vcodec": 'none', "acodec": "LAME3.1", "abr":128, "container":"mp3", "language":"ru",
                                "http_headers":vid_tr["headers"], "preference":-2})
          if orig_volume != '0':
            self._downloader.add_post_processor(YandexTranslateMergePP(self._downloader, orig_volume=orig_volume, codec=codec), when='post_process')
          self._downloader.add_post_processor(YandexTranslateAutoAddPP(self._downloader), when='video')
        elif vid_tr["resp"].status == 0:
          self.report_warning (f'Err {vid_tr["resp"].errcode}')
          self.report_warning (vid_tr["resp"].message.decode('utf-8'))
        else:
          raise ExtractorError(f'Unknown error: \n{str(vid_tr["resp"])}', expected=True)

        if sub_tr["resp"].subtitles:
          self.to_screen("Subtitles translation available")
          for sub_lang in sub_tr["resp"].subtitles:
            if not sub_lang.translatedLanguage in info["subtitles"]: info["subtitles"][sub_lang.translatedLanguage] = []
            info["subtitles"][sub_lang.translatedLanguage].append({"ext": "json3", "url": sub_lang.translatedUrl, "name": f'{sub_lang.language}->{sub_lang.translatedLanguage}',
                                               "http_headers":sub_tr["headers"]})
          self._downloader.add_post_processor(YandexTranslateSubtitleFixPP(self._downloader), when='before_dl')
        return info
