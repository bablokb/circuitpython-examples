# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Download URL (project zip): https://learn.adafruit.com/mp3-playback-rp2040/pico-i2s-mp3
"""
CircuitPython I2S MP3 playback example.
Plays a single MP3 once.
"""
import board
import audiomp3
import audiobusio

audio = audiobusio.I2SOut(board.GP7, board.GP8, board.GP14)

mp3 = audiomp3.MP3Decoder(open("slow.mp3", "rb"))

audio.play(mp3)
while audio.playing:
    pass

print("Done playing!")
