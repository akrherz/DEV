"""Word Cloud of IEM Features"""
import psycopg2
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def main():
    """Go!"""
    pgconn = psycopg2.connect(
        database="mesosite", host="iemdb", user="nobody", port=5555
    )
    cursor = pgconn.cursor()
    data = ""
    cursor.execute("""SELECT story from feature""")
    for row in cursor:
        data += " %s " % (row[0],)
    wordcloud = WordCloud().generate(data)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig("test.png")


if __name__ == "__main__":
    main()
