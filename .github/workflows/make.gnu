#
# Include file for OASIS3 Makefile for a Linux system using
# Gnu 10 compilers and OpenMPI
#
###############################################################################
#
# CHAN  : communication technique used in OASIS3 (MPI1/MPI2)
CHAN            = MPI1
#
# Paths for libraries, object files and binaries
#
# COUPLE        : path for oasis3-mct main directory
COUPLE          = /home/runner/work/eophis/eophis/oasis3-mct/
#
# ARCHDIR       : directory created when compiling
ARCHDIR         = $(COUPLE)/BLD
#
# MPI libraries
MPIDIR      = /usr/lib/x86_64-linux-gnu/
MPIBIN      = $(MPIDIR)/bin
MPI_INCLUDE = $(MPIDIR)/mpich/
MPILIB      = -L$(MPIDIR)/lib -lmpi
MPIRUN      = $(MPIBIN)/mpirun --oversubscribe
#
# NETCDF libraries
NETCDF_INCLUDE = /usr/include
NETCDF_LIBRARY = -L/usr/lib/x86_64-linux-gnu/ -lnetcdff -lnetcdf
#
# Make command
F90         = mpifort -I$(MPI_INCLUDE)
F           = $(F90)
f90         = $(F90)
f           = $(F90)
CC          = mpicc -I$(MPI_INCLUDE)
# Linker (needed for shared libraries)
LD          = $(F90) $(MPILIB)
# Static libraries compilation options
STATOPT     =
# Shared libraries options
DYNOPT      = -fPIC
LDDYNOPT    = -shared
# Static archiver
AR          = ar
ARFLAGS     = -ruv
#
# CPP keys and compiler options
#
CPPDEF    = -Duse_comm_$(CHAN) -D__VERBOSE -DTREAT_OVERLAY
#
FCBASEFLAGS  = -O2 -I. -ffree-line-length-0 -fallow-argument-mismatch -mcmodel=large
CCBASEFLAGS  = -O2
INC_DIR = -I$(ARCHDIR)/include
#
F90FLAGS = $(FCBASEFLAGS) $(INC_DIR) $(CPPDEF) -I$(NETCDF_INCLUDE) $(NETCDF_LIBRARY)
f90FLAGS = $(FCBASEFLAGS) $(INC_DIR) $(CPPDEF) -I$(NETCDF_INCLUDE) $(NETCDF_LIBRARY)
FFLAGS   = $(FCBASEFLAGS) $(INC_DIR) $(CPPDEF) -I$(NETCDF_INCLUDE) $(NETCDF_LIBRARY)
fFLAGS   = $(FCBASEFLAGS) $(INC_DIR) $(CPPDEF) -I$(NETCDF_INCLUDE) $(NETCDF_LIBRARY)
CCFLAGS  = $(CCBASEFLAGS) $(INC_DIR) $(CPPDEF) -I$(NETCDF_INCLUDE) $(NETCDF_LIBRARY)
LDFLAGS  = $(FCBASEFLAGS) $(INC_DIR)
F2C_LDFLAGS = -lmpi_mpifh -lgfortran
#
#############################################################################
#
# Additional definitions that should not be changed
#
FLIBS           = $(NETCDF_LIBRARY)
# BINDIR        : directory for executables
BINDIR          = $(ARCHDIR)/bin
# LIBBUILD      : contains a directory for each library
LIBBUILD        = $(ARCHDIR)/build/lib
# INCPSMILE     : includes all *o and *mod for each library
INCPSMILE       = -I$(ARCHDIR)/include -I$(LIBBUILD)/cbindings -I$(LIBBUILD)/psmile.$(CHAN) -I$(LIBBUILD)/mct -I$(LIBBUILD)/scrip
