import argparse
import datetime
import os
import re
import sys
from pathlib import Path
from typing import Optional

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


class YouTubeDownloader:
	def __init__(self, output_dir: str = '.'):
		self.output_dir = Path(output_dir)
		self.output_dir.mkdir(exist_ok=True)
	
	def get_video_id(self, url: str) -> str:
		"""Extract video ID from YouTube URL"""
		pattern = r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)'
		match = re.search(pattern, url)
		if not match:
			raise ValueError('URL de YouTube no válida')
		return match.group(1)
	
	def get_clean_title(self, title: str) -> str:
		"""Clean title for filename"""
		clean_title = re.sub(r'[\\/*?:"<>|]', '', title)
		return re.sub(r'\s+', '_', clean_title.strip())
	
	def generate_filename(self, title: str, extension: str) -> str:
		"""Generate filename with date and clean title"""
		fecha = datetime.datetime.now().strftime('%d-%m-%Y')
		clean_title = self.get_clean_title(title)
		return f'{fecha}_{clean_title}.{extension}'
	
	def download_video(self, url: str, quality: str = 'best') -> None:
		"""Download video with specified quality"""
		ydl_opts = {
			'format': quality,
			'outtmpl': str(self.output_dir / '%(upload_date)s_%(title)s.%(ext)s'),
			'ignoreerrors': True,
		}
		
		try:
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				info = ydl.extract_info(url, download=False)
				title = info.get('title', 'video_sin_titulo')
				print(f'Descargando video: {title}')
				ydl.download([url])
				print(f'Video descargado correctamente')
		except Exception as e:
			print(f'Error descargando video: {e}')
			sys.exit(1)
	
	def download_audio(self, url: str, format_audio: str = 'mp3') -> None:
		"""Download only audio in specified format"""
		ydl_opts = {
			'format': 'bestaudio/best',
			'outtmpl': str(self.output_dir / '%(upload_date)s_%(title)s.%(ext)s'),
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': format_audio,
				'preferredquality': '192',
			}],
			'ignoreerrors': True,
		}
		
		try:
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				info = ydl.extract_info(url, download=False)
				title = info.get('title', 'audio_sin_titulo')
				print(f'Descargando audio: {title}')
				ydl.download([url])
				print(f'Audio descargado correctamente en formato {format_audio}')
		except Exception as e:
			print(f'Error descargando audio: {e}')
			sys.exit(1)
	
	def download_transcript(self, url: str, language: Optional[str] = None) -> None:
		"""Download video transcript"""
		try:
			video_id = self.get_video_id(url)
			
			# Get video info for title
			ydl_opts = {'quiet': True, 'no_warnings': True}
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				info = ydl.extract_info(url, download=False)
				title = info.get('title', 'transcripcion_sin_titulo')
			
			available_transcripts = YouTubeTranscriptApi().list(video_id)
			transcript = None
			if language:
				try:
					transcript = available_transcripts.find_transcript([language])
				except Exception:
					print(f'No hay transcripción en "{language}", se usa el idioma original del video')
			if transcript is None:
				# The auto-generated transcript is in the spoken (original) language
				transcripts = list(available_transcripts)
				transcript = next((t for t in transcripts if t.is_generated), transcripts[0])
			transcript_list = transcript.fetch()
			print(f'Transcripción obtenida en idioma: {transcript.language}')
			
			# Format transcript
			formatter = TextFormatter()
			transcript_text = formatter.format_transcript(transcript_list)
			
			# Save transcript
			filename = self.generate_filename(title, 'txt')
			output_path = self.output_dir / filename
			
			with open(output_path, 'w', encoding='utf-8') as f:
				f.write(f'# Transcripción: {title}\n\n')
				f.write(f'URL: {url}\n')
				f.write(f'Fecha: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}\n\n')
				f.write('---\n\n')
				f.write(transcript_text)
			
			print(f'Transcripción guardada en: {output_path}')
			
		except Exception as e:
			print(f'Error obteniendo transcripción: {e}')
			sys.exit(1)
	
	def get_video_formats(self, url: str) -> None:
		"""Show available video formats"""
		ydl_opts = {'listformats': True, 'quiet': False}
		try:
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				ydl.extract_info(url, download=False)
		except Exception as e:
			print(f'Error obteniendo formatos: {e}')


def main():
	parser = argparse.ArgumentParser(
		description='Descarga videos, audio o transcripciones de YouTube',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog='''
Ejemplos de uso:
  %(prog)s --video https://youtube.com/watch?v=VIDEO_ID
  %(prog)s --audio https://youtube.com/watch?v=VIDEO_ID --audio-format mp3
  %(prog)s --transcript https://youtube.com/watch?v=VIDEO_ID --language es
  %(prog)s --formats https://youtube.com/watch?v=VIDEO_ID
		'''
	)
	
	parser.add_argument('url', help='URL del video de YouTube')
	parser.add_argument('--output-dir', default='.', help='Directorio de salida (default: directorio actual)')
	
	# Download options
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--video', action='store_true', help='Descargar video')
	group.add_argument('--audio', action='store_true', help='Descargar solo audio')
	group.add_argument('--transcript', action='store_true', help='Descargar transcripción')
	group.add_argument('--formats', action='store_true', help='Mostrar formatos disponibles')
	
	# Additional options
	parser.add_argument('--quality', default='best', help='Calidad del video (default: best)')
	parser.add_argument('--audio-format', default='mp3', choices=['mp3', 'wav', 'ogg', 'm4a'], 
						help='Formato de audio (default: mp3)')
	parser.add_argument('--language', help='Idioma de la transcripción (default: idioma original del video)')
	
	args = parser.parse_args()
	
	downloader = YouTubeDownloader(args.output_dir)
	
	try:
		if args.video:
			downloader.download_video(args.url, args.quality)
		elif args.audio:
			downloader.download_audio(args.url, args.audio_format)
		elif args.transcript:
			downloader.download_transcript(args.url, args.language)
		elif args.formats:
			downloader.get_video_formats(args.url)
	except KeyboardInterrupt:
		print('\nDescarga cancelada por el usuario')
		sys.exit(0)
	except Exception as e:
		print(f'Error inesperado: {e}')
		sys.exit(1)


if __name__ == '__main__':
	main()
