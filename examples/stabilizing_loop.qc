// Stabilizing loop example: loop-carried value oscillates within [0, 1]
// Fixed-point stabilizes within widen_after threshold and is proven INT8-safe.
int x = 1;
int i = 0;
while (i < 4) {
    x = 1 - x;
    i = i + 1;
}
print x;
