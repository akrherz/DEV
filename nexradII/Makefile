CFLAGS=-I/home/ldm/include -I/usr/local/include -g

all: nexradII

nexradII:	nexradII.o getbuf.o
	$(CC) -o nexradII nexradII.o getbuf.o -L/home/ldm/lib -lldm -lbz2

nexradII_filter:	nexradII_filter.o getbuf.o
	$(CC) -o nexradII_filter nexradII_filter.o getbuf.o -L/usr/local/ldm/lib -lldm -lbz2 -lz -llzo
