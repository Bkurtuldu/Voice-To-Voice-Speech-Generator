# Windows Local Installation

1 => pip install -r requirements.txt

2 => python -m src.orchestrator


# Docker Linux Installation

1 => docker compose build

2 => docker compose run --rm -it   -e AUDIODEV_INDEX=5   -e CHANNELS=2   voice-orchestrator

AUDIODEV_INDEX and CHANNELS environment variables are needed to specify the recording device in Docker Linux, in the container following commands can be run to detect index and channels

1 => docker compose run --rm -it voice-orchestrator bash

2 => python

3 => import sounddevice as sd 
     print(sd.query_devices())

In Windows Docker cannot directly access input output devices so it is quite hard to configure it with WSL, Linux is preferred in the context of Docker

For any permisson related errors 

1 => sudo usermod -aG docker $USER
2 => newgrp docker
