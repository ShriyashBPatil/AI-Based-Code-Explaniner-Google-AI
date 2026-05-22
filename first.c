#include <stdio.h>

void greet(char name[]){
    printf("Hello %s\n", name);
}

int main(){
    printf("input a value:");
    int number;
    scanf("%d", &number);
    printf("You entered: %d\n", number);
    return 0;
}