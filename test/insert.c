#include <stdio.h> 
#include <time.h>
#include <stdlib.h>
#include <string.h>

void genPass(int lenofpass) {
    const char avaliable[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@£$^&*()_+./<>?;:[]{}";
    const char insert[] = "ILOVEANTONY";
    char password[lenofpass];
    srand(time(NULL));
    int half = lenofpass / 2;
    for (double i = 0; i < lenofpass; i++) {
        for (int i = 0; i < lenofpass; i++) {
            if (i >= half && i < half + strlen(insert) && i < lenofpass) {
                password[i] = insert[i - half];
            } else {
                int place = rand() % (sizeof(avaliable) - 1);
                password[i] = avaliable[place];
            }
        }
    }   
    printf("Password is: %s\n", password);
}   

int main() {
    int lenofpass;
    scanf("%i", &lenofpass);
    return 0;
}