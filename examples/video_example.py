from TikTokApi import TikTokApi

with TikTokApi() as api:
    video = api.video(id="7041997751718137094")

    # Bytes of the TikTok video
    video_data = video.bytes()

    with open("out.mp4", "wb") as out_file:
        out_file.write(video_data)
