import os
from datetime import datetime, date
import asyncio
from ffmpeg import Progress
from ffmpeg.asyncio import FFmpeg
from pathlib import Path

CAMERA_IP = os.environ.get("RTSP_ADDR")
CAMERA_NAME = os.environ.get("CAMERA_NAME")
BASE_DIR = Path(__file__).resolve().parent.parent()
RECORDING_DIR = os.path.join(BASE_DIR,"shared","recordings", CAMERA_NAME)
os.makedirs(os.path.join(RECORDING_DIR), exist_ok=True)
async def getAV():
    startDate = date.today()
    startHour = datetime.now().hour
    while True:
        file_name =f"output_{CAMERA_NAME}_{startDate.strftime('%Y-%m-%d')}_{startHour:02d}00.mp4"
        file_path = os.path.join(RECORDING_DIR, file_name)
        state = {"restart":False}
        ffmpeg = (
            FFmpeg()
            .option("y")
            .input(
                CAMERA_IP,
                rtsp_transport="tcp",
                rtsp_flags="prefer_tcp",
                stimeout="5000000"
            )
            .output(file_path, vcodec="copy")

        )
        @ffmpeg.on("progress")
        def on_progress(progress):
            currentDate = date.today()
            currentHour = datetime.now().hour
            if currentDate != startDate:
                ffmpeg.terminate()
                state["restart"] = True
            elif currentHour != startHour:
                ffmpeg.terminate()
                state["restart"] = True
            
        try:
            await ffmpeg.execute()
        except Exception as e:
            print(f"failed to write video {e}")

        if state["restart"] == True :
            await asyncio.sleep(2)
            startDate = date.today()
            startHour = datetime.now().hour
        else:
            await asyncio.sleep(5)
            print("recording interupted for unknown reason")

if __name__ == "__main__":
    asyncio.run(getAV())