#include <openssl/sha.h>
#include <stdio.h>
#include <string.h>

int main() {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    char *string = "0";
    SHA256((unsigned char *)string, strlen(string), hash);

    printf("SHA256 hash: ");
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        printf("%02x", hash[i]);
    }
    printf("\n");
    return 0;
}