# yt-downloader

Command-line tool to download YouTube videos, audio, or transcripts. Built on [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api).

## Install

```sh
brew tap pookdeveloper/youtube-downloader https://github.com/pookdeveloper/youtube-downloader
brew install pookdeveloper/youtube-downloader/yt-downloader
```

Homebrew also installs `ffmpeg` (audio extraction) and `deno` (JavaScript runtime yt-dlp needs for YouTube).

Update:

```sh
brew update && brew upgrade yt-downloader
```

## Usage

```sh
yt-downloader [--video | --audio | --transcript | --formats] URL [options]
```

Quote the URL: an unquoted `&` sends the command to the background.

| Command | Result |
| --- | --- |
| `yt-downloader --video "URL"` | Downloads the video |
| `yt-downloader --audio "URL"` | Downloads the audio (mp3 by default) |
| `yt-downloader --transcript "URL"` | Saves the transcript as a `.txt` file |
| `yt-downloader --formats "URL"` | Lists the available formats |

### Options

| Option | Default | Description |
| --- | --- | --- |
| `--output-dir DIR` | current directory | Where files are saved |
| `--quality FORMAT` | `best` | yt-dlp format for `--video` (see `--formats`) |
| `--audio-format` | `mp3` | `mp3`, `wav`, `ogg` or `m4a` |
| `--language CODE` | video's original language | Transcript language, e.g. `es`, `en` |

Without `--language`, the transcript comes from YouTube's auto-generated captions, which are in the spoken language. If the requested language is not available, the tool falls back to the original language.

Transcripts are saved as `DD-MM-YYYY_Title.txt`.

## Development

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
yt-downloader --help
```

## Release

1. Bump `version` in `pyproject.toml`, commit, tag `vX.Y.Z` and push the tag.
2. In `Formula/yt-downloader.rb`, update the tag in `url` and set `sha256` to:
   ```sh
   curl -sL https://github.com/pookdeveloper/youtube-downloader/archive/refs/tags/vX.Y.Z.tar.gz | shasum -a 256
   ```
3. Commit and push the formula.
