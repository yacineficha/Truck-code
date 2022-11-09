import ffmpeg

def encode_video_h264(input_file, output_file):
    stream = ffmpeg.input(input_file)
    stream = ffmpeg.output(stream, output_file, vcodec='h264')
    ffmpeg.run(stream, overwrite_output=True)