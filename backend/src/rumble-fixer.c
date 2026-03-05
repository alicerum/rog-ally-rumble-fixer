#include <linux/input.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

int set_gain(const char *device, int gain_percent) {
    int fd = open(device, O_RDWR);
    if (fd < 0) {
        fprintf(stderr, "Error: Failed to open device %s: %s\n", device, strerror(errno));
        return -1;
    }
    
    unsigned short gain_value = (unsigned short)((gain_percent / 100.0) * 0xFFFF);
    
    struct input_event ie;
    memset(&ie, 0, sizeof(ie));
    ie.type = EV_FF;
    ie.code = FF_GAIN;
    ie.value = gain_value;
    
    int result = write(fd, &ie, sizeof(ie));
    if (result < 0) {
        fprintf(stderr, "Error: Failed to write to device: %s\n", strerror(errno));
        close(fd);
        return -1;
    }
    
    close(fd);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <device_path> <gain_percent>\n", argv[0]);
        fprintf(stderr, "Example: %s /dev/input/event7 60\n", argv[0]);
        return 1;
    }
    
    const char *device_path = argv[1];
    int gain_percent = atoi(argv[2]);
    
    if (gain_percent < 0 || gain_percent > 100) {
        fprintf(stderr, "Error: gain_percent must be between 0 and 100 (got %d)\n", gain_percent);
        return 1;
    }
    
    if (access(device_path, F_OK) != 0) {
        fprintf(stderr, "Error: Device not found: %s\n", device_path);
        return 1;
    }
    
    if (set_gain(device_path, gain_percent) < 0) {
        fprintf(stderr, "Error: Failed to set gain on %s\n", device_path);
        return 1;
    }
    
    return 0;
}
