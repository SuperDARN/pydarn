compile:
	gcc -c -Wall -Werror -fPIC dmap.c -o dmap.o -I./*.h
	gcc -shared -o libdmap.so dmap.o

clean:
	rm -f libdmap.a libdmap.so *.o 

