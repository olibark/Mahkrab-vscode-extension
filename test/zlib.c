#include <zlib.h>
#include <stdio.h>
#include <string.h>

int main() {
    const char *original = "Hello, zlib!";
    char compressed[100];
    char decompressed[100];
    uLong compressed_len = sizeof(compressed);
    uLong decompressed_len = sizeof(decompressed);

    if (compress((Bytef *)compressed, &compressed_len, (const Bytef *)original, strlen(original)) != Z_OK) {
        printf("Compression failed\n");
        return 1;
    }

    if (uncompress((Bytef *)decompressed, &decompressed_len, (const Bytef *)compressed, compressed_len) != Z_OK) {
        printf("Decompression failed\n");
        return 1;
    }

    printf("Original: %s\n", original);
    printf("Decompressed: %s\n", decompressed);
    return 0;
}