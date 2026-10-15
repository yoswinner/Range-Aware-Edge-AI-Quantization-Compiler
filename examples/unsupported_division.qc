// Unsupported operation example: real division is non-integral and
// unsupported by the INT8 quantization pass. Independent safe variables
// (a, b) are quantized to int8, while c is safely kept as fp32.
int a = 40;
int b = 8;
float c = a / b;
print c;
