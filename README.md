# Yandex.Translate yt-dlp plugin
Плагин для [yt-dlp](https://github.com/yt-dlp/yt-dlp#readme) для скачивания автоматического перевода с Yandex Translate, основанный на [voice-over-translation](https://github.com/ilyhalight/voice-over-translation) и [vot-cli](https://github.com/FOSWLY/vot-cli).

Все наработки и благодарности принадлежат [ilyhalight](https://github.com/ilyhalight), [FOSWLY](https://github.com/FOSWLY) и аффилированым с ними особам.

Репозитарий содержит распакованный Google Protobuf [protobuf-4.25.2-py3-none-any.whl](https://pypi.org/project/protobuf/#files)

## Установка

[installing yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins)

В случае использования standalone yt-dlp.exe папка yt_dlp_plugins должна быть скопированна внутрь папки yt-dlp-plugins\YandexTranslate, находящейся возле yt-dlp.exe

Пример структуры:

- d:\Test\yt-dlp.exe
- d:\Test\yt-dlp-plugins\YandexTranslate\yt_dlp_plugins\extractor\yandex_translate.py
- ... и т.д и т.п. ... 
- d:\Test\yt-dlp-plugins\YandexTranslate\yt_dlp_plugins\yandex.protoc

## Использование

По умолчанию отключен, для включения используйте опцию '--use-extractors YandexTranslate'.

Желательно использование опций '--audio-multistreams' и '--merge-output-format mkv'.

Громкость оригинального звука задается параметром orig_volume. Например, '--extractor-args YandexTranslate:orig_volume=0.2'. При 0 дополнительный мюксинг не запускается.

Перевод в список скачиваемых форматов добавляется автоматически. Субтитры - нужно выбирать. yt-dlp.conf - пример конфига.

Пробует работать со всеми экстракторами, доступными в yt-dlp.

