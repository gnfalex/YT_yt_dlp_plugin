import sys, os
from uuid import uuid4 as getUUID
import hmac, hashlib
try:
  # Check is protobuf installed
  from google.protobuf import descriptor as _descriptor
except:
  sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "\\..\\protobuf-4.25.2-py3-none-any.whl.pypi")
  from google.protobuf import descriptor as _descriptor

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "\\.")

import yandex_pb2

_workerHost = "api.browser.yandex.ru"
_yandexHmacKey = b"xtGCyGdTY2Jy6OMEKdTuXev3Twhkamgm"
_yandexUserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 YaBrowser/23.7.1.1140 Yowser/2.5 Safari/537.36"
_getSignature = lambda body: hmac.new(_yandexHmacKey, msg=body, digestmod=hashlib.sha256).hexdigest()

def request_subtitles_translation(self, sub_url, video_id, request_lang="en", first_request = True, uuid = getUUID().hex):
  subReq = yandex_pb2.VideoSubtitlesRequest()
  subReq.url = sub_url
  subReq.language = request_lang
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
