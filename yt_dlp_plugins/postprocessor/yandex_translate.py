import json, os
from yt_dlp.postprocessor.common import PostProcessor 
from yt_dlp.postprocessor.ffmpeg import FFmpegPostProcessor
from yt_dlp.utils import traverse_obj, prepend_extension, PostProcessingError

class YandexTranslateAutoAddPP(PostProcessor):
    def run(self, info, downloader = None):
      if not traverse_obj(info, "requested_formats"):
        return [], info
      YTStream = traverse_obj(info, ("formats", (lambda key, value: traverse_obj(value, "format_id")=="YT")))
      if YTStream and not traverse_obj(info, ("requested_formats", (lambda key, value: traverse_obj(value, "format_id")=="YT"))):
        info["requested_formats"].extend(YTStream)
      return [], info

class YandexTranslateSubtitleFixPP(PostProcessor):
    def run(self, info, downloader = None):
        def ms2str (s):
          H = int(s/3600000%24); M = int(s/60000%60); S =  int(s/1000%60); MS = int(s%1000)
          return f'{H:02d}:{M:02d}:{S:02d},{MS:03d}'

        delFiles = []
        for subs_lang, subs_data in traverse_obj(info, "requested_subtitles", {}).items():
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

class YandexTranslateMergePP(FFmpegPostProcessor):
    def __init__(self, downloader, orig_volume = "0.5"):
        FFmpegPostProcessor.__init__(self, downloader)
        self.orig_volume = orig_volume

    def run(self, info, downloader = None):
        orig_stream = None; trans_stream = None
        success = False
        if not traverse_obj(info, ("requested_formats", (lambda key, value: traverse_obj(value, "format_id")=="YT"))):
          return [], info

        filename = info['filepath']
        metadata = self.get_metadata_object(filename)
        temp_filename = prepend_extension(filename, "tmp")

        options = ['-c', 'copy', '-map', '0']
        audio_streams = traverse_obj(metadata, ("streams", (lambda key, value: traverse_obj(value, "codec_type")=="audio")), [None])

        if len(audio_streams) > 1:
          orig_stream = traverse_obj(audio_streams, (lambda key,value: traverse_obj(value, ("disposition", "default"), 0) == 1), [None])[0]
          if orig_stream is None:
            orig_stream = audio_streams[0]
          else:
            options.extend([f"-disposition:{orig_stream['index']}", "0"])
          trans_stream = traverse_obj(audio_streams, (lambda key,value: value["index"] != orig_stream['index']),[None])[-1]

        if not (orig_stream is None and trans_stream is None):
          options.extend(['-map', f'-0:{trans_stream["index"]}', '-filter_complex',
                          f'[0:{orig_stream["index"]}]volume={self.orig_volume}[original];[original][0:{trans_stream["index"]}]amix=inputs=2:duration=longest[audio_out]',
                          '-map', '[audio_out]', f'-c:{trans_stream["index"]}', 'libmp3lame', f'-disposition:{trans_stream["index"]}', 'default',
                          f'-metadata:s:{trans_stream["index"]}', 'language=rus', f'-metadata:s:{trans_stream["index"]}', f'title=YandexTranslated + {self.orig_volume} orig'
                        ])
          try:
            self.to_screen('Remuxing Yandex Translate')
            self.run_ffmpeg(filename, temp_filename, options)
            success = True
          except PostProcessingError as err:
            pass
        if success:
            os.replace(temp_filename, filename)
        return [], info  # return list_of_files_to_delete, info_dict