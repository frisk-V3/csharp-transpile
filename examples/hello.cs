class Hello {
    static int add(int a, int b) {
        int s = a + b;
        return s;
    }

    static int main() {
        int x = add(2, 3);
        if (x > 4) {
            x = x + 1;
        } else {
            x = x - 1;
        }
        return x;
    }
}
