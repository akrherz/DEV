"""Put four images into one."""

from PIL import Image


def main():
    """Go Main Go."""
    for i in range(364):
        out = Image.new('RGB', (2048, 1536))
        i1 = Image.open("images/%05i_0.png" % (i, ))
        i2 = Image.open("images/%05i_36.png" % (i, ))
        i3 = Image.open("images/%05i_37.png" % (i, ))
        i4 = Image.open("images/%05i_38.png" % (i, ))
        out.paste(i1, (0, 0))
        out.paste(i2, (1024, 0))
        out.paste(i3, (0, 768))
        out.paste(i4, (1024, 768))
        i1.close()
        i2.close()
        i3.close()
        i4.close()
        out.save('images/%05i.png' % (i, ))
        del out


if __name__ == '__main__':
    main()
