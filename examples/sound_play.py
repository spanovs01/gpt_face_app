from pydub import AudioSegment
from pydub.playback import play

sound_audio = AudioSegment.from_wav('13999.wav')
play( sound_audio)