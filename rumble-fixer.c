#include <linux/input.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>

volatile sig_atomic_t keep_running = 1;

void signal_handler(int signum) {
    keep_running = 0;
}

void print_usage(const char *program_name) {
    fprintf(stderr, "Usage: %s <device_path> <gain_percent> <interval_sec>\n", program_name);
    fprintf(stderr, "\n");
    fprintf(stderr, "Arguments:\n");
    fprintf(stderr, "  device_path   - Path to input device (e.g., /dev/input/event7)\n");
    fprintf(stderr, "  gain_percent  - Rumble gain percentage (0-100)\n");
    fprintf(stderr, "  interval_sec  - How often to set gain in seconds (e.g., 1)\n");
    fprintf(stderr, "\n");
    fprintf(stderr, "Example:\n");
    fprintf(stderr, "  %s /dev/input/event7 60 1\n", program_name);
    fprintf(stderr, "\n");
}

int set_gain(const char *device, int gain_percent) {
    int fd = open(device, O_RDWR);
    if (fd < 0) {
        return -1;
    }
    
    unsigned short gain_value = (unsigned short)((gain_percent / 100.0) * 0xFFFF);
    
    struct input_event ie;
    memset(&ie, 0, sizeof(ie));
    ie.type = EV_FF;
    ie.code = FF_GAIN;
    ie.value = gain_value;
    
    int result = write(fd, &ie, sizeof(ie));
    close(fd);
    
    return (result < 0) ? -1 : 0;
}

int main(int argc, char *argv[]) {
    // Check arguments
    if (argc != 4) {
        fprintf(stderr, "Error: Wrong number of arguments\n\n");
        print_usage(argv[0]);
        return 1;
    }
    
    const char *device_path = argv[1];
    int gain_percent = atoi(argv[2]);
    int interval_sec = atoi(argv[3]);
    
    // Validate arguments
    if (gain_percent < 0 || gain_percent > 100) {
        fprintf(stderr, "Error: gain_percent must be between 0 and 100 (got %d)\n", gain_percent);
        return 1;
    }
    
    if (interval_sec < 1) {
        fprintf(stderr, "Error: interval_sec must be at least 1 (got %d)\n", interval_sec);
        return 1;
    }
    
    // Check if device exists
    if (access(device_path, F_OK) != 0) {
        fprintf(stderr, "Error: Device not found: %s\n", device_path);
        return 1;
    }
    
    // Set up signal handlers for clean shutdown
    signal(SIGTERM, signal_handler);
    signal(SIGINT, signal_handler);
    
    fprintf(stderr, "ROG Ally X Rumble Keeper starting...\n");
    fprintf(stderr, "Device: %s\n", device_path);
    fprintf(stderr, "Target gain: %d%%\n", gain_percent);
    fprintf(stderr, "Check interval: %d second(s)\n\n", interval_sec);
    
    // Initial set on startup
    if (set_gain(device_path, gain_percent) < 0) {
        fprintf(stderr, "Warning: Failed to set initial gain (device may not be ready yet)\n");
    } else {
        fprintf(stderr, "Initial gain set successfully\n");
    }
    
    // Main loop
    int success_count = 0;
    int fail_count = 0;
    
    while (keep_running) {
        sleep(interval_sec);
        
        if (set_gain(device_path, gain_percent) == 0) {
            success_count++;
            if (success_count == 1 || success_count % 100 == 0) {
                fprintf(stderr, "Gain set successfully (total: %d)\n", success_count);
            }
        } else {
            fail_count++;
            fprintf(stderr, "Warning: Failed to set gain (failures: %d)\n", fail_count);
        }
    }
    
    fprintf(stderr, "Rumble Keeper shutting down cleanly\n");
    fprintf(stderr, "Statistics: %d successful, %d failed\n", success_count, fail_count);
    return 0;
}
