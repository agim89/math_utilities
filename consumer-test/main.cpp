#include <mylib/sum.h>
#include <iostream>

int main() {
	int a = 2;
	int b = 3;
	int result = sum(a, b);
	std::cout << "sum(" << a << "," << b << ") = " << result << std::endl;
	return result == 5 ? 0 : 1;
}
