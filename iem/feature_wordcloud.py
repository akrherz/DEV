"""Word Cloud of IEM Features"""
from wordcloud import WordCloud

import matplotlib.pyplot as plt
from pyiem.util import get_dbconn


def main():
    """Go!"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    data = ""
    cursor.execute("SELECT story from feature")
    for row in cursor:
        data += f" {row[0]} "
    wordcloud = WordCloud().generate(data)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig("test.png")


if __name__ == "__main__":
    main()
