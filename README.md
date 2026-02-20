<p align="center">
  <img src="./logo.png" alt="MP3 Meta Editor Logo" width="180" />
</p>

# MP3 Meta Editor

Невеликий desktop-застосунок для редагування ID3 метаданих MP3.

## GitHub Description
`Desktop MP3 ID3 tag editor with cover art preview, replace/remove support, and macOS .app packaging.`

## Проєкт для GitHub
MP3 Meta Editor це локальний desktop-застосунок для перегляду та редагування ID3 тегів у MP3 файлах.  
Підтримує редагування основних полів, `WOAS` (source URL), коментаря, а також обкладинки (перегляд, заміна, видалення) з подальшим збереженням змін у файл.

## Що вміє
- відкривати `.mp3` файл;
- показувати всі наявні ID3 теги в raw-вигляді;
- редагувати основні поля (title, artist, album, genre, year/date тощо);
- редагувати comment;
- зберігати зміни назад у файл.

## Запуск
1. Створіть та активуйте віртуальне оточення (опційно):
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
2. Встановіть залежності:
   - `pip install -r requirements.txt`
3. Запустіть програму:
   - `python3 app.py`

## Пакетування в macOS `.app`
1. Запустіть скрипт збірки:
   - `./package_macos.sh`
2. Результати збірки:
   - `.app`: `dist/MP3 Meta Editor.app`
   - `.zip`: `dist/MP3 Meta Editor-macOS.zip`

Скрипт сам:
- створює/оновлює `.venv`;
- встановлює build-залежності з `requirements-dev.txt`;
- збирає `.app` через `PyInstaller`;
- пакує `.app` в `.zip`.

## Технічний стек
- Python 3
- PySide6 / Qt (GUI)
- mutagen (робота з ID3 тегами)
