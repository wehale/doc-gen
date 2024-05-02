
# Original: calc.c
```c
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int ctoi(char c) {
    int ret = -1;
    if (!(c < '0' || c > '9')) {
        ret = c - '0';
    }
    return ret;
}

char itoc(int i) {
    char ret = '\0';
    if (!(i < 0 || i > 9)) {
        ret = '0' + i;
    }
    return ret;
}

void add_buffers(char *bufA, char *bufB) {
    int bufLen = strlen(bufA);
    int carry = 0;
    int i = 0;
    for (i = 0; i < bufLen; i++) {
        int buf_idx = bufLen - i - 1;
        char ba = bufA[buf_idx];
        char bb = bufB[buf_idx];
        int a = ctoi(ba);
        int b = ctoi(bb);
        int sab = (a + b + carry);
        carry = sab / 10;
        int remainder = sab % 10;
        bufA[buf_idx] = itoc(remainder);
    }
}

char *multiply(char* a, int lenA, char *b, int lenB) {
    int bufSize = lenA + lenB;
    char *buf = calloc(bufSize+1, sizeof(char));
    char *retBuf = calloc(bufSize+1, sizeof(char));
    memset(retBuf, '0', bufSize);
    for (int i = 0; i < lenA; i++) {
        memset(buf, '0', bufSize);
        int carry = 0;
        int a_idx = lenA - i - 1;
        for (int j = 0; j < lenB; j++) {
            int buf_idx = bufSize - i - j - 1;
            int b_idx = lenB - j - 1;
            int intA = ctoi(a[a_idx]);
            int intB = ctoi(b[b_idx]);
            int prod = intA * intB + carry;
            int remainder = (prod % 10);
            carry = prod / 10;
            buf[buf_idx] = itoc(remainder);
            if (j+1==lenB && carry) {
                buf[buf_idx-1] = itoc(carry);
            }
        }
        add_buffers(retBuf, buf);
    }
    free(buf);
    return retBuf;
}

int main(int argc, char *argv[]) {
    char *s1 = argv[1];
    char *s2 = argv[2];

    int lenS1 = strlen(s1);
    int lenS2 = strlen(s2);

    //check incoming
    //printf("s2 [%d] = %s\n", lenS2, s2);
    //printf("s1 [%d] = %s\n", lenS1, s1);

    //test add_buffers function
    //char bufA[5] = {'0', '0', '6', '2', '\0'};
    //char bufB[5] = {'0', '1', '0', '8', '\0'};
    //add_buffers(bufA, bufB);
    //printf("%s\n", bufA);

    char *result = multiply(s1, lenS1, s2, lenS2);

    printf("%s * %s = %s\n", s1, s2, result);

    free(result);

    return 0;
}
```
