ffmpeg -i %05d.png -vcodec libx264 -r 10 -pix_fmt yuv420p out.mp4
# needed this for the larger 4panel plots
# ffmpeg -i %05d.png -s:v 1280x720 -vcodec libx264 -r 10 -pix_fmt yuv420p out.mp4
