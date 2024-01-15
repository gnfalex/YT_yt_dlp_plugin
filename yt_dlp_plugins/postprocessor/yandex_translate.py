import json, os
from yt_dlp.postprocessor.common import PostProcessor 

class YandexTranslatePrePP(PostProcessor):
    def run(self, info):
        print (info)
        input()
        url = info.get("original_url",info.get("url"))
#        if YoutubeIE.suitable(url):
#          print (self.url_result(url, YandexTranslateIE))
        return [], info  # return list_of_files_to_delete, info_dict

class YandexTranslatePostPP(PostProcessor):
    def run(self, info):
        print (info)
        return [], info  # return list_of_files_to_delete, info_dict

class YandexTranslateSubtitleFixPP(PostProcessor):
    def run(self, info, downloader = None):
        print (downloader)
        def ms2str (s):
          H = int(s/3600000%24); M = int(s/60000%60); S =  int(s/1000%60); MS = int(s%1000)
          return f'{H:02d}:{M:02d}:{S:02d},{MS:03d}'

        delFiles = []
        if "requested_subtitles" in info:
          for subs_lang, subs_data in info["requested_subtitles"].items():
            if subs_data["ext"]=="YTjson":
              try:
                oldName = subs_data["filepath"]
                newName = os.path.splitext(oldName)[0] + ".str"
                with open(oldName, "r", encoding='utf-8') as f_in:
                  with open(newName,'w', encoding='utf-8') as f_out:
                    data = json.load(f_in)
                    for i,sub in enumerate(data["subtitles"]):
                      f_out.write (f'{i+1}\n{ms2str(sub["startMs"])} --> {ms2str(sub["startMs"]+sub["durationMs"])}\n{sub["text"]}\n\n')
                subs_data["ext"], subs_data["filepath"] = "str", newName
                if oldName in info["__files_to_move"]:
                  del info["__files_to_move"][oldName]
                  info["__files_to_move"][newName]=newName
                delFiles.append(oldName)
              except:
                pass
        return delFiles, info  # return list_of_files_to_delete, info_dict
