"""pip3 install pyserial numpy faster-whisper mlx-whisper"""

import os
import serial
import time
import struct
import numpy as np
#from faster_whisper import WhisperModel
import mlx_whisper
import mlx.core as mx
from mlx_whisper.load_models import load_model
from mlx_whisper.transcribe import transcribe

# Konfig

os.environ["PATH"] = os.path.expanduser("~/bin") + ":" + os.environ.get("PATH", "")

# Einstellungen

PORT = "/dev/cu.usbserial-110"  # aktuell halten
BAUD = 460800
SAMPLE_RATE = 4000

# Whisper lokal laden

print("Lade Whisper-Modell...")

# medium -> gut (30cm, kein hintergrund)
# small -> ok (30cm, kein hintergrund)
"""
model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)
"""
MODEL_NAME = "mlx-community/whisper-medium-mlx"

print("Whisper ist bereit!")

# Serielle Daten empfangen

def read_exact(ser, size):
    data = bytearray()

    while len(data) < size:
        chunk = ser.read(size - len(data))

        if chunk:
            data.extend(chunk)

    return bytes(data)


def wait_for_magic(ser):
    buffer = bytearray()

    while True:
        b = ser.read(1)

        if not b:
            continue

        buffer.extend(b)

        if len(buffer) > 4:
            buffer.pop(0)

        if buffer == b"AUD1":
            return


# Sprache mit Whisper erkennen


def recognize_audio(raw_audio):

    import numpy as np

    # 8-Bit-Audio in Float umwandeln
    samples = np.frombuffer(
        raw_audio,
        dtype=np.uint8
    ).astype(np.float32)

    # Mittelpunkt entfernen und normalisieren
    samples = (samples - 128) / 128.0

    # 4 kHz auf 16 kHz hochrechnen
    old_positions = np.arange(len(samples))
    new_positions = np.arange(len(samples) * 4) / 4.0

    samples_16k = np.interp(
        new_positions,
        old_positions,
        samples
    ).astype(np.float32)

    # WAV-Datei für MLX Whisper erzeugen
    import tempfile
    import wave
    import os

    filename = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp:
            filename = temp.name

        pcm = np.clip(
            samples_16k * 32767,
            -32768,
            32767
        ).astype("<i2")

        with wave.open(filename, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(pcm.tobytes())

        # MLX Whisper: Apple GPU
        result = mlx_whisper.transcribe(
            filename,
            path_or_hf_repo=MODEL_NAME,
            language="de",
            task="transcribe",
            temperature=0,
            condition_on_previous_text=False,
            initial_prompt="Dies ist eine deutsche Sprachaufnahme. Erkenne die gesprochenen deutschen Wörter möglichst genau."
        )

        return result["text"].strip()

    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)


# Hauptprogramm

print("Verbinde mit ESP32...")

ser = serial.Serial(
    PORT,
    BAUD,
    timeout=1
)

time.sleep(2)

print("Bereit! Warte auf Aufnahme...")

while True:

    try:
        wait_for_magic(ser)

        count = struct.unpack(
            "<I",
            read_exact(ser, 4)
        )[0]

        if count == 0 or count > 40000:
            raise ValueError("Ungueltige Audiolaenge")

        raw_audio = read_exact(ser, count)

        print("Audio empfangen:", count, "Samples")
        print("Erkenne Sprache...")

        try:
            text = recognize_audio(raw_audio)

            if not text:
                text = "Keine Sprache erkannt"

        except Exception as error:
            print("Whisper Fehler:", error)
            text = "Erkennungsfehler"

        print("Erkannt:", text)

        response = "TEXT:" + text.replace("\n", " ") + "\n"

        ser.write(response.encode("utf-8"))

    except Exception as error:
        print("Fehler:", error)
