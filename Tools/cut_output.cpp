#include <cstdio>

const int LIMIT_KILOBYTES = 100;
const int OLE_KILOBYTES = 1024 * 128;

char buffer[1024];

int main(){
    int kilobytes = 0;
    while(true){
        size_t sz = fread(buffer, 1, 1024, stdin);
        if(sz == 0) break;
        kilobytes++;
        if(kilobytes < LIMIT_KILOBYTES) fwrite(buffer, 1, sz, stdout);
    }
    if(kilobytes > OLE_KILOBYTES){
        fputs("2", stderr);
    } else if(kilobytes > LIMIT_KILOBYTES){
        fputs("1", stderr);
    } else {
        fputs("0", stderr);
    }
    return 0;
}
