import json, os
from yt_dlp.postprocessor.common import PostProcessor 

class YandexTranslateSubtitleFixPP(PostProcessor):
    def run(self, info, downloader = None):
        print (downloader)
        def ms2str (s):
          H = int(s/3600000%24); M = int(s/60000%60); S =  int(s/1000%60); MS = int(s%1000)
          return f'{H:02d}:{M:02d}:{S:02d},{MS:03d}'

        delFiles = []
        for subs_lang, subs_data in info.get("requested_subtitles", {}).items():
          if subs_data.get("ext")=="YTjson":
            try:
              oldName = subs_data.get("filepath")
              if oldName is None: raise
              newName = os.path.splitext(oldName)[0] + ".srt"
              with open(oldName, "r", encoding='utf-8') as f_in:
                  with open(newName,'w', encoding='utf-8') as f_out:
                    data = json.load(f_in)
                    for i,sub in enumerate(data.get("subtitles",[])):
                      f_out.write (f'{i+1}\n{ms2str(sub.get("startMs", 0))} --> {ms2str(sub.get("startMs", 0)+sub.get("durationMs", 0))}\n{sub.get("text","")}\n\n')               
              subs_data["ext"], subs_data["filepath"] = "str", newName
              if oldName in info.get("__files_to_move"):
                del info["__files_to_move"][oldName]
                info["__files_to_move"][newName]=newName
                delFiles.append(oldName)
            except:
              pass
        return delFiles, info  # return list_of_files_to_delete, info_dict
