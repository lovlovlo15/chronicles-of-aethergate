"""Lightweight sound manager for Chronicles of Aether Gate.

Prioritizes cross-platform behavior with minimal deps:
- Uses pygame.mixer if available (better sounds)
- Falls back to Tk bell or ASCII bell if pygame isn't present

API:
- SoundManager(enabled=True)
- play(event: str)
- toggle() -> bool
"""

from __future__ import annotations

import math
import os
import shutil
import struct
import subprocess
import tempfile
import threading
import wave
from typing import Dict, Optional

try:
	import pygame
	_HAS_PYGAME = True
except Exception:
	_HAS_PYGAME = False

try:
	import tkinter as _tk
except Exception:
	_tk = None


class SoundManager:
	"""Cross-platform sound manager with graceful fallbacks."""

	def __init__(self, enabled: bool = True):
		self.enabled = enabled
		self._mixer_ready = False
		self._sounds: Dict[str, Optional[object]] = {}
		self._event_wavs: Dict[str, str] = {}
		self._sample_rate = 22050
		self._system_player: Optional[str] = None
		# Background music state (pygame.mixer.music)
		self._bg_path: Optional[str] = None
		self._bg_loop: bool = True
		self._bg_volume: float = 0.2  # Fixed 20% volume

		# Define simple event-to-file mapping (in-memory or bundled files later)
		# For now, we’ll use pygame-generated beeps or fallback beeps.
		# Keys: 'menu', 'pickup', 'attack', 'heal', 'victory', 'defeat'

		if _HAS_PYGAME:
			try:
				# Initialize mixer with optimal settings for better audio quality
				# 44100Hz matches most music files, -16 = 16-bit signed samples
				# channels=2 for stereo, buffer=1024 for good performance/quality balance
				pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
				pygame.mixer.init()
				self._mixer_ready = True
			except Exception:
				self._mixer_ready = False

		# Detect a system audio player on Linux (PulseAudio/ALSA/ffmpeg)
		for cmd in ("paplay", "aplay", "ffplay"):
			if shutil.which(cmd):
				self._system_player = cmd
				break

	def toggle(self) -> bool:
		"""Enable/disable sounds; returns new state."""
		self.enabled = not self.enabled
		# Stop bg music when disabling; resume when enabling
		try:
			if not self.enabled:
				self.stop_music()
				print("🔇 Sound disabled - music stopped")
			else:
				# Resume if we had bg music configured
				if self._bg_path:
					result = self.play_music(self._bg_path, loop=self._bg_loop, volume=self._bg_volume)
					if result:
						print("🔊 Sound enabled - music resumed")
					else:
						print("⚠️ Sound enabled but music failed to resume")
		except Exception as e:
			print(f"⚠️ Error during sound toggle: {e}")
		return self.enabled

	def play(self, event: str):
		"""Play a short sound for the given event name."""
		if not self.enabled:
			return
		# Use background thread to avoid blocking UI
		threading.Thread(target=self._play_impl, args=(event,), daemon=True).start()

	# Internal implementation
	def _play_impl(self, event: str):
		"""Play sound using available backends.

		Priority: pygame mixer (if available) -> system player (paplay/aplay/ffplay) -> Tk bell -> ASCII bell.
		"""
		# Ensure we have a wav file ready for this event (short tone)
		wav_path = self._get_or_create_wav(event)

		# pygame backend
		if self._mixer_ready and wav_path:
			try:
				snd = self._sounds.get(event)
				if snd is None:
					snd = pygame.mixer.Sound(wav_path)
					self._sounds[event] = snd
				snd.play()
				return
			except Exception:
				pass

		# system player backend (Linux)
		if self._system_player and wav_path:
			try:
				if self._system_player == "paplay":
					subprocess.Popen(["paplay", wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
					return
				if self._system_player == "aplay":
					subprocess.Popen(["aplay", "-q", wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
					return
				if self._system_player == "ffplay":
					subprocess.Popen(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", wav_path],
									 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
					return
			except Exception:
				pass

		# Tk bell fallback
		if _tk is not None:
			try:
				root = _tk._default_root
				if root is not None:
					root.bell()
					return
			except Exception:
				pass

		# ASCII bell fallback
		try:
			print("\a", end="")
		except Exception:
			pass

	# ---- Tone generation helpers ----
	def _get_or_create_wav(self, event: str) -> Optional[str]:
		"""Return a path to a short sound file for the given event, creating it if needed.

		Prefers an existing file under data/sounds/{event}.(wav|ogg). If missing, generates a
		small WAV tone into data/sounds/{event}.wav so it persists for later runs.
		"""
		# In-memory cache hit
		path = self._event_wavs.get(event)
		if path and os.path.exists(path):
			return path

		# Look for user-provided assets first
		try:
			assets_dir = os.path.join("data", "sounds")
			candidates = [
				os.path.join(assets_dir, f"{event}.wav"),
				os.path.join(assets_dir, f"{event}.ogg"),
			]
			for p in candidates:
				if os.path.exists(p):
					self._event_wavs[event] = p
					return p
		except Exception:
			pass

		# Choose a simple tone per event (fallback)
		tones = {
			"menu": [(880, 0.12)],
			"pickup": [(1200, 0.08)],
			"attack": [(700, 0.08)],
			"heal": [(1000, 0.1)],
			"victory": [(880, 0.12), (1175, 0.12), (1568, 0.2)],  # A5, D6, G6
			"defeat": [(196, 0.25)],  # low G3
		}
		sequence = tones.get(event, [(1000, 0.1)])

		# Ensure sounds dir exists and generate a persistent wav file
		try:
			assets_dir = os.path.join("data", "sounds")
			os.makedirs(assets_dir, exist_ok=True)
			path = os.path.join(assets_dir, f"{event}.wav")
			self._write_tone_wav(path, sequence)
			self._event_wavs[event] = path
			return path
		except Exception:
			# Last resort: temp file (should rarely happen)
			try:
				fd, path = tempfile.mkstemp(prefix=f"aether_{event}_", suffix=".wav")
				os.close(fd)
				self._write_tone_wav(path, sequence)
				self._event_wavs[event] = path
				return path
			except Exception:
				return None

	def _write_tone_wav(self, path: str, sequence: list[tuple[int, float]]):
		"""Write a mono WAV file containing the provided (freqHz, durationSec) sequence."""
		sr = self._sample_rate
		amplitude = 16000  # 16-bit range
		samples: list[int] = []
		# Small 10ms gap between tones
		gap_len = int(0.01 * sr)
		for idx, (freq, dur) in enumerate(sequence):
			length = int(dur * sr)
			for n in range(length):
				# simple sine wave
				t = n / sr
				val = int(amplitude * math.sin(2.0 * math.pi * freq * t))
				samples.append(val)
			if idx < len(sequence) - 1:
				samples.extend([0] * gap_len)

		with wave.open(path, "w") as wf:
			wf.setnchannels(1)
			wf.setsampwidth(2)  # 16-bit
			wf.setframerate(sr)
			# Pack as little-endian signed 16-bit
			frames = struct.pack("<" + "h" * len(samples), *samples)
			wf.writeframes(frames)

	# ---- Background music API (pygame required) ----
	def play_music(self, path: str, *, loop: bool = True, volume: float = 0.2) -> bool:
		"""Play background music from a file path. Returns True if started.

		Uses pygame.mixer.music. If sounds are disabled or pygame isn't ready, returns False.
		"""
		self._bg_path = path
		self._bg_loop = loop
		self._bg_volume = max(0.0, min(1.0, volume))

		if not self.enabled:
			print("🔇 Sound manager disabled")
			return False
		if not self._mixer_ready:
			print("❌ pygame.mixer not ready")
			return False
		try:
			import pygame  # local import to ensure module present
			pygame.mixer.music.load(path)
			pygame.mixer.music.set_volume(self._bg_volume)
			pygame.mixer.music.play(-1 if loop else 0)
			print(f"🎵 Background music started: {path} (volume: {int(self._bg_volume*100)}%)")
			return True
		except Exception as e:
			print(f"❌ Failed to play background music: {e}")
			return False

	def stop_music(self):
		"""Stop background music if playing (pygame)."""
		if not self._mixer_ready:
			return
		try:
			import pygame
			pygame.mixer.music.stop()
		except Exception:
			pass

	def set_music_volume(self, volume: float):
		"""Set background music volume (0.0 - 1.0)."""
		self._bg_volume = max(0.0, min(1.0, volume))
		if not self._mixer_ready:
			return
		try:
			import pygame
			pygame.mixer.music.set_volume(self._bg_volume)
		except Exception:
			pass


__all__ = ["SoundManager"]
