#include <iostream>

using namespace std;

int main(){








int n;
 cin >> n;
long long x = 0;

for(long long i = 0; i < 1000000000; i++){
    x = 0;
    for(long long j = 0; j < 100000000; j++){
        x += i;

    }
}



cout << n * 2;
return 0;

}
