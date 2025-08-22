#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <stdbool.h>

void roll(int* result) {
    for (int i = 0; i < 3; i++) {
        result[i] = (rand() % (3)) + 1;
    }
}

void comproll(int* result) {
    for (int i = 0; i < 3; i++) {
        result[i] = (rand() % (3)) + 1;
    }
}

void clrscr()
{
    system("clear");
}

int main() {
    bool running = true;
    srand(time(NULL));
    while (running) {
        int rollResult[3];
        char choice;
        roll(rollResult);
        printf("Roll: [%d %d %d]\n", rollResult[0], rollResult[1], rollResult[2]);
        int comprollResult[3];
        comproll(comprollResult);
        printf("Roll: [%d %d %d]\n", comprollResult[0], comprollResult[1], comprollResult[2]);
        printf("Roll again: y/n\n" );
        scanf(" %c", &choice);
        if (comprollResult[0] == rollResult[0] && 
            comprollResult[1] == rollResult[1] && 
            comprollResult[2] == rollResult[2]) {
            printf("Matching numbers! You win!\n");
            exit(0);
        }
        if (choice == 'n') {
            running = false;
        }
        else if (choice == 'y') {
            clrscr();
            continue;
        }
        else {
            printf("invalid");
            break;
        }
    }  
    return 0;
}