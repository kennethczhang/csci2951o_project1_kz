CXX = g++
CXXFLAGS = -std=c++11 -Wall -O3
INCLUDES = -I src

# Define directories
SRC_DIR = src
BUILD_DIR = build

# Define sources and objects
SRCS = $(SRC_DIR)/Main.cpp $(SRC_DIR)/SATInstance.cpp $(SRC_DIR)/DimacsParser.cpp
OBJS = $(SRCS:$(SRC_DIR)/%.cpp=$(BUILD_DIR)/%.o)
TARGET = $(BUILD_DIR)/solver

all: $(BUILD_DIR) $(TARGET)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $(TARGET) $(OBJS)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -rf $(BUILD_DIR)
