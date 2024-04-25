
# calc.c

## Description of calc.c


The provided source code is a C program that performs the multiplication of two large numbers represented as strings. The main components of the program are as follows:

1. `ctoi()` Function:
   - Converts a character representing a digit (0-9) to its corresponding integer value.
   - Parameters:
     - `char c`: The character to be converted.
   - Returns `-1` if the character is not between '0' and '9', otherwise returns the integer value of the character.

2. `itoc()` Function:
   - Converts an integer (0-9) to its corresponding character.
   - Parameters:
     - `int i`: The integer to be converted.
   - Returns `'\0'` if the integer is not between 0 and 9, otherwise returns the character representation of the integer.

3. `add_buffers()` Function:
   - Performs addition on two null-terminated strings `bufA` and `bufB` that represent numbers, storing the result back into `bufA`.
   - Assumes that `bufA` and `bufB` are of the same length and contain only digit characters.
   - The addition is done in place, and `bufA` is modified to hold the result of the sum.

4. `multiply()` Function:
   - Multiplies two numbers represented as strings `a` and `b`.
   - Parameters:
     - `char *a`: The first number as a string.
     - `int lenA`: The length of the first number string.
     - `char *b`: The second number as a string.
     - `int lenB`: The length of the second number string.
   - Allocates memory for the buffer to hold the result and a return buffer initialized with zeros.
   - Performs the multiplication digit by digit, taking care of carry, and adds the intermediate results using `add_buffers()`.
   - Returns a pointer to the buffer containing the result. It is the caller's responsibility to free this memory.

5. `main()` Function:
   - Entry point of the program.
   - Accepts two command-line arguments representing the numbers to be multiplied.
   - Calls the `multiply()` function with the provided arguments.
   - Prints the result of the multiplication.
   - Frees the memory allocated for the result before exiting.

Additional Details:
- The `multiply()` function assumes that the input strings consist of digits only and do not have leading zeros.
- The `memset()` function is used to initialize the result buffer with zeros.
- `calloc()` is used to allocate memory for buffers, which is initialized to zero.
- Intermediate and final results are stored in dynamically allocated buffers which are freed after their use.
- The program includes commented-out code for testing the `add_buffers()` function and for printing the inputs.

Overall, the program is capable of multiplying very large numbers that may not fit into standard data types such as `int` or `long long`. It outputs the result of the multiplication in the form of "number1 * number2 = result".

## Functions in calc.c


### `ctoi(char c)`
Converts a character to the corresponding integer value if the character is a digit ('0' to '9'). Otherwise, returns -1.

#### Parameters:
- `char c`: The character to convert.

#### Returns:
- An `int` of the converted digit.
- Returns `-1` if `c` is not a digit.

#### Example Usage:
```c
int digit = ctoi('3'); // digit will be 3
int non_digit = ctoi('a'); // non_digit will be -1
```

### `itoc(int i)`
Converts an integer to the corresponding character if the integer is between 0 and 9.

#### Parameters:
- `int i`: The integer to convert.

#### Returns:
- A `char` of the converted integer.
- Returns `'\0'` if `i` is not between 0 and 9.

#### Example Usage:
```c
char character = itoc(5); // character will be '5'
char invalid = itoc(10); // invalid will be '\0'
```

### `add_buffers(char *bufA, char *bufB)`
Performs in-place addition of two null-terminated strings representing numbers of equal length.

#### Parameters:
- `char *bufA`: A string representing the first number. The sum will be stored here.
- `char *bufB`: A string representing the second number, to be added to `bufA`. 

#### Returns:
Nothing. The result of the addition is stored in `bufA`.

#### Notes:
- Both `bufA` and `bufB` are expected to have the same length.
- Assumes the strings only contain digit characters ('0' to '9').

#### Example Usage:
```c
char bufA[5] = {'0', '0', '6', '2', '\0'};
char bufB[5] = {'0', '1', '0', '8', '\0'};
add_buffers(bufA, bufB); // bufA now contains the string "0170"
```

### `multiply(char *a, int lenA, char *b, int lenB)`
Multiplies two strings that represent numbers and returns a new string representing the product.

#### Parameters:
- `char *a`: A string representing the first number to multiply.
- `int lenA`: The length of string `a`.
- `char *b`: A string representing the second number to multiply.
- `int lenB`: The length of string `b`.

#### Returns:
- A pointer to a null-terminated string representing the product.
- The caller is responsible for freeing the allocated memory.

#### Example Usage:
```c
char *product = multiply("123", 3, "456", 3); // product -> "56088"
free(product); // Remember to free the allocated memory!
```

### `main(int argc, char *argv[])`
The main entry point of the program, which takes command-line arguments and prints the product of two large numbers.

#### Parameters:
- `int argc`: Argument count.
- `char *argv[]`: Argument vector.

#### Returns:
- An `int` representing the exit status of the program. Returns `0` on successful execution.

#### Example Usage:
Run the program via command line with two arguments:
```shell
./program_name 123 456
```
The output will be:
```plaintext
123 * 456 = 56088
```

## Security Vulnerabilities in calc.c


### Buffer Overflow
The `add_buffers` function does not perform any bounds checking on the input buffers `bufA` and `bufB`. This has the potential to cause a buffer overflow if either of the input buffers is shorter than expected. If the length is not properly validated before calling this function, an attacker could exploit this vulnerability to execute arbitrary code or cause a crash.

### Null Pointer Dereference
The `multiply` function returns a pointer to dynamically allocated memory that is expected to be freed by the caller. If the caller forgets to free this memory or if the result pointer is `NULL` due to unsuccessful memory allocation and not checked for `NULL` before being used, this can lead to a memory leak or a null pointer dereference, respectively.

### Command Line Argument Handling
The `main` function does not check if there are enough command line arguments (`argc`) before attempting to use them. If the program is run with fewer than the expected number of arguments, it will attempt to access `argv[1]` and `argv[2]` which may lead to undefined behavior or a segmentation fault.

### Use of Uninitialized Memory
The `add_buffers` function relies on both `bufA` and `bufB` being null-terminated strings of equal lengths. If `bufA` or `bufB` is not properly null-terminated or does not contain only the digits '0' to '9', the behavior of the `add_buffers` function is undefined. This may lead to incorrect calculations or potential out-of-bound memory access.

### Integer Overflow
Both `ctoi` and `itoc` functions are designed to work with digits '0' to '9' only. The code does not handle cases where the input value might lead to integer overflow or underflow, which could result from arithmetic operations with characters outside the range of '0' to '9'.

Overall, the source code contains several potential vulnerabilities including buffer overflow, null pointer dereference, improper argument handling, uninitialized memory usage, and integer overflow or underflow. It is crucial to address these issues to prevent exploits and crashes in a production environment.
