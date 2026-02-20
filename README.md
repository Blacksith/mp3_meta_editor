<p align="center">
  <img src="./logo.png" alt="MP3 Meta Editor Logo" width="180" />
</p>

# MP3 Meta Editor

## UA
Невеликий desktop-застосунок для перегляду та редагування ID3 метаданих MP3.

### GitHub Description
`Desktop MP3 ID3 tag editor with cover art preview, replace/remove support, and macOS .app packaging.`

### Опис проєкту
MP3 Meta Editor підтримує редагування основних полів, `WOAS` (source URL), коментаря, а також обкладинки (перегляд, заміна, видалення) з подальшим збереженням у файл.

### Що вміє
- відкривати `.mp3` файл;
- показувати всі ID3 теги в raw-вигляді;
- редагувати `title`, `artist`, `album`, `genre`, `date`, `tracknumber`, `WOAS` тощо;
- редагувати `comment`;
- переглядати, замінювати та видаляти обкладинку;
- зберігати зміни назад у файл.

### Запуск
1. Створіть та активуйте віртуальне оточення (опційно):
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
2. Встановіть залежності:
   - `pip install -r requirements.txt`
3. Запустіть програму:
   - `python3 app.py`

### Пакетування в macOS `.app`
1. Запустіть скрипт збірки:
   - `./package_macos.sh`
2. Результати:
   - `.app`: `dist/MP3 Meta Editor.app`
   - `.zip`: `dist/MP3 Meta Editor-macOS.zip`

Скрипт:
- створює/оновлює `.venv`;
- встановлює build-залежності з `requirements-dev.txt`;
- збирає `.app` через `PyInstaller`;
- пакує `.app` в `.zip`.

### Технічний стек
- Python 3
- PySide6 / Qt (GUI)
- mutagen (ID3 теги)

---

## EN
A desktop app for viewing and editing MP3 ID3 metadata.

### GitHub Description
`Desktop MP3 ID3 tag editor with cover art preview, replace/remove support, and macOS .app packaging.`

### Project Overview
MP3 Meta Editor supports editing core tags, `WOAS` (source URL), comments, and cover art (preview, replace, remove), with saving changes back to the file.

### Features
- open `.mp3` files;
- display all ID3 tags in raw view;
- edit `title`, `artist`, `album`, `genre`, `date`, `tracknumber`, `WOAS`, etc.;
- edit `comment`;
- preview, replace, and remove cover art;
- save metadata changes to the original file.

### Run
1. Create and activate a virtual environment (optional):
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Start the app:
   - `python3 app.py`

### Build macOS `.app`
1. Run the packaging script:
   - `./package_macos.sh`
2. Build artifacts:
   - `.app`: `dist/MP3 Meta Editor.app`
   - `.zip`: `dist/MP3 Meta Editor-macOS.zip`

The script:
- creates/updates `.venv`;
- installs build dependencies from `requirements-dev.txt`;
- builds `.app` with `PyInstaller`;
- archives `.app` into `.zip`.

### Tech Stack
- Python 3
- PySide6 / Qt (GUI)
- mutagen (ID3 tags)
