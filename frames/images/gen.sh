# Safari,woof
#ffmpeg -r 6  -pattern_type glob -i '*.jpg' -c:v libx264 -profile:v main -vf format=yuv420p -filter:v "crop=840:480:300:440" -c:a aac -movflags +faststart out.mp4
ffmpeg -framerate 12 -i '%05d.png' -c:v libx264 -profile:v main -vf format=yuv420p  -c:a aac -movflags +faststart out.mp4

# needed this for the larger 4panel plots
# ffmpeg -i %05d.png -s:v 1280x720 -vcodec libx264 -r 10 -pix_fmt yuv420p out.mp4
