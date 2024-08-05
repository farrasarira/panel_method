# LBM Makefile

TARGET= panelMethod
CXX= g++
CXXFLAGS=-Wall -O3 -fopenmp -march=native
SRCDIR= ./src
OBJDIR= ./obj
RESTART= ./restart
SOURCE= $(wildcard $(SRCDIR)/*.cpp)
OBJECT= $(addprefix $(OBJDIR)/, $(notdir $(SOURCE:.cpp=.o)))
OUTPUT= out.$(TARGET).txt field*.vtr output0* rst stt output0*.vtm geometryflag.vtm geometryflag stop *.txt ./Output



$(TARGET): $(OBJECT)
	$(CXX) $(CXXFLAGS) $(shell pkg-config --cflags cantera) -o $(TARGET) $(OBJECT) $(shell pkg-config --libs cantera) -lpetsc -llapack -lblas
	export OMP_NUM_THREADS=1

$(OBJDIR)/%.o: $(SRCDIR)/%.cpp 
	-mkdir -p $(OBJDIR)
	$(CXX) $(CXXFLAGS) -o $@ -c $< -I./src/headers -I/usr/lib/petsc/include -I/usr/lib/x86_64-linux-gnu/openmpi/include/

.PHONY: clean
clean: 
	rm -rf $(TARGET) $(OBJECT) $(OUTPUT) $(OBJDIR) $(RESTART)
output_clean:
	rm -rf $(OUTPUT)