

#include <iostream>

using namespace std;


long long dele(){
long long x = 1;
for(long long i = 0; i < 10000000; i++){
//    x = 0;
//    cout << 1;
    for(long long j = 0; j < 1000000000000; j++){
        x *= i % 123434345;


    }
}
return x;
}

int main(){








int n;
 cin >> n;
long long x = 1;

//while(1){
//    int y = 0;
//    y = x +
//}

for(long long i = 0; i < 10000000; i++){
//    x = 0;
//    cout << 1;
    for(long long j = 0; j < 1000000000000; j++){
        x += dele() % 123434345;
        


    }
}



cout << 2 * n;
return 0;

}
