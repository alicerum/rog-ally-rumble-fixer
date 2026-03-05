CC = gcc
CFLAGS = -Wall -O2
TARGET = rumble-fixer
SRC = src/rumble-fixer.c
OUT_DIR = out

.PHONY: all clean

all: $(OUT_DIR)/$(TARGET)

$(OUT_DIR)/$(TARGET): $(SRC)
	@mkdir -p $(OUT_DIR)
	$(CC) $(CFLAGS) -o $@ $<
	chmod 755 $@
	@echo "Built: $@"

clean:
	rm -rf $(OUT_DIR)

# For CI builds - outputs to backend/out
build: all
