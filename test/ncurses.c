#include <ncurses.h>

int main() {
    initscr(); // Initialize the screen
    printw("Hello, ncurses!"); // Print a message
    refresh(); // Refresh the screen to show the message
    getch(); // Wait for user input
    endwin(); // End ncurses mode
    return 0;
}