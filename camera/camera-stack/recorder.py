import asyncio
import os
from datetime import date, datetime
from pathlib import Path

from ffmpeg.asyncio import FFmpeg

CAMERA_IP = os.environ.get("RTSP_ADDR")
CAMERA_NAME = os.environ.get("CAMERA_NAME")
BASE_DIR = Path(__file__).resolve().parent.parent
RECORDING_DIR = os.path.join(BASE_DIR, "shared", "recordings", CAMERA_NAME)
os.makedirs(os.path.join(RECORDING_DIR), exist_ok=True)


async def getAV():
    startDate = date.today()
    startHour = datetime.now().hour
    while True:
        os.makedirs(f"{RECORDING_DIR}/{startDate}", exist_ok=True)
        file_name = f"output_{CAMERA_NAME}_{startDate.strftime('%Y-%m-%d')}_{startHour:02d}00.mp4"
        file_path = os.path.join(RECORDING_DIR, str(startDate), file_name)
        state = {"restart": False}
        ffmpeg = (
            FFmpeg()
            .option("y")
            .input(
                CAMERA_IP,
                rtsp_transport="tcp",
                rtsp_flags="prefer_tcp",
                stimeout="5000000",
            )
            .output(file_path, vcodec="copy", movflags="frag_keyframe+empty_moov")
        )

        @ffmpeg.on("progress")
        def on_progress(progress):
            currentDate = date.today()
            currentHour = datetime.now().hour
            if currentDate != startDate || currentHour != startHour:
                state["restart"] = True
                try:
                    ffmpeg.terminate()
                except:
                    pass
            

        try:
            await ffmpeg.execute()
        except Exception as e:
            print(f"failed to write video {e}")

        if state["restart"] == True:
            await asyncio.sleep(2)
            startDate = date.today()
            startHour = datetime.now().hour
        else:
            await asyncio.sleep(5)
            startDate = date.today()
            startHour = datetime.now().hour

if __name__ == "__main__":
    asyncio.run(getAV())
