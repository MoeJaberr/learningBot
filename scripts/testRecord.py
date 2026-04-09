import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.recordMic import record_microphone

record_microphone(duration=10)
