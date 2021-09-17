#
.PHONY: rootcint
.PHONY: lib
.PHONY: all
.PHONY: clean

LIBS := libhistcomp.so

LINKDEFS := $(wildcard *linkdef.hh)
DICTINCLUDES := $(subst _linkdef,, $(LINKDEFS))
DICTS := $(subst _linkdef.hh,_dict.cc,$(LINKDEFS))
INCLUDES := $(filter-out $(LINKDEFS), $(wildcard *.hh))

CXX = `root-config --cxx`
CXXFLAGS = `root-config --cflags` -fPIC -g
ROOTLIBS = `root-config --glibs`
SHARED = -shared
# coqmma:= +
# eqmpty:=
# space:= $(empty) $(empty)
# dash:= -
# foo:= a-b-c
# bar:= $(subst -,+,$(foo))

all:  $(DICTS) lib

$(DICTS) :  $(LINKDEFS) $(DICTINCLUDES)
	for i in $(LINKDEFS); do \
	  echo Bulding dictionary from $$i ; \
	  rootcint -f `echo $$i | sed -e "s/_linkdef.hh/_dict.cc/g"` -c -p \
	  `echo $$i | sed -e "s/_linkdef.hh/.hh/g"` $$i ;\
	done
	
lib : $(DICTS) $(filter-out $(DICTS), $(wildcard *.cc)) $(INCLUDES)
# lib : *cc *hh 
	$(CXX) $(CXXFLAGS) -I$(ROOTSYS)/include $(SHARED) -o libhistcomp.so  *.cc  $(ROOTLIBS) 
#	echo DICTS = $(DICTS)
#
#	echo bar = $(bar)

clean: 
	rm *.so ; \
	rm *_dict.cc ; \
	rm *_dict.hh ; \
	rm *_dict.h

