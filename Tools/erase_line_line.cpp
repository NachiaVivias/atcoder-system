#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
using namespace std;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    while(true){
        string buf;
        getline(cin, buf);
        if(cin.eof()) break;
        if(buf.size() >= 6) if(buf.substr(0,6) == "#line ") continue;
        cout << buf << "\n";
    }
    return 0;
}
