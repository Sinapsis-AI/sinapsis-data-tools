# -*- coding: utf-8 -*-
from io import BytesIO

import numpy as np
from pydub import AudioSegment


def audio_bytes_to_numpy(audio_bytes: bytes) -> tuple[np.ndarray, int]:
    audio = AudioSegment.from_file(BytesIO(audio_bytes), format="mp3")

    samples = np.array(audio.get_array_of_samples())

    if audio.channels == 2:
        samples = samples.reshape((-1, 2))

    return samples, audio.frame_rate
