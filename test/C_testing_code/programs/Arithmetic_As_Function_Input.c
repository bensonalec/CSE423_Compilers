int func(int arithmetic_input) {
    return arithmetic_input;
}

int main() {

    int value_1 = func(1);

    int value_2 = func(1 + 1);

    int value_3 = func(1 + 1 * 1);

    int value_4 = func((1 + 1 * 1));

    int value_5 = func((1 + 1) * 1);

}