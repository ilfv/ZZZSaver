# HoyoSaver
Can save info about DeadlyAssault in ZZZ and respresent it on image(in TG bot) or gui

# Dependencies
[Python 3.11](https://www.python.org/downloads/release/python-3110/) or later

# Deployment
## 1: Install all dependencies
## 2: Install all required libs
```bash
pip install -r requirements.txt
```
## 3: Setup
Create `.env` file.
`.env` file should have the following content (instead of <> text you should specify your data)
```env
Cookie=<your cookie file from https://act.hoyolab.com, it necessarily required>
BOT_TOKEN=<Telegram bot token(It necessarily only if you use it)>
```

## 4: Running
Run bot `bot.bat` or `tgbot/main.py`; gui `ui.bat` or `ui/main.py`
