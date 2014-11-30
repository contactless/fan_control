
LIB_LOCATION=/usr/lib/wb-softpwm
.PHONY: all clean

all:
clean :

install: all
	install -m 0755 softpwm.py  $(DESTDIR)/$(LIB_LOCATION)
	ln -s $(LIB_LOCATION)/softpwm.py $(DESTDIR)/usr/bin/wb-softpwm





