# Enhanced Array Support in VB2Arduino Transpiler

## Overview
The transpiler now supports robust array handling including multi-dimensional arrays, `UBound`/`LBound` functions, `Option Base`, and proper nested expression parsing in method calls.

## Features

### 1. Multi-Dimensional Arrays
VB6-style array declarations are now fully supported:

```vb
' 1D array
Dim arr(9) As Integer

' 2D array
Dim matrix(3, 4) As Integer

' 3D array  
Dim cube(2, 2, 2) As Integer
```

Generated C++:
```cpp
int arr[10];              // size + 1
int matrix[4][5];         // (3+1) x (4+1)
int cube[3][3][3];        // (2+1) x (2+1) x (2+1)
```

### 2. Array Indexing
Multi-dimensional array access uses proper bracket syntax:

```vb
arr(0) = 10
matrix(0, 0) = 1
cube(1, 1, 1) = 100
```

Generated C++:
```cpp
arr[0] = 10;
matrix[0][0] = 1;
cube[1][1][1] = 100;
```

### 3. UBound Function
Returns the upper bound (maximum index) of an array dimension:

```vb
Dim arr(9) As Integer
Dim matrix(3, 4) As Integer

For i = 0 To UBound(arr)           ' Loops 0-9
    value = arr(i)
Next

For i = 0 To UBound(matrix, 1)     ' Loops 0-3 (first dimension)
For j = 0 To UBound(matrix, 2)     ' Loops 0-4 (second dimension)
    matrix(i, j) = i + j
Next
Next
```

Generated C++:
```cpp
int arr[10];
int matrix[4][5];

for (int i = 0; i <= 9; ++i) {
    value = arr[i];
}

for (int i = 0; i <= 3; ++i) {
    for (int j = 0; j <= 4; ++j) {
        matrix[i][j] = i + j;
    }
}
```

### 4. LBound Function
Returns the lower bound of an array (determined by `Option Base`):

```vb
Option Base 0   ' Default, LBound returns 0
Dim arr(10) As Integer
x = LBound(arr)  ' x = 0

Option Base 1   ' Uncommon, LBound returns 1
Dim arr2(10) As Integer
x = LBound(arr2) ' x = 1
```

### 5. Option Base Support
Control whether arrays start at index 0 or 1:

```vb
Option Base 0   ' Arrays indexed 0..N (default)
Option Base 1   ' Arrays indexed 1..N (VB6-style)
```

### 6. Array Dimension Tracking
Dimensions can be literals or constants:

```vb
Const MAX_SIZE = 9
Dim arr(MAX_SIZE) As Integer       ' arr[MAX_SIZE + 1]
Dim matrix(3, MAX_SIZE) As Integer ' matrix[4][MAX_SIZE + 1]
```

## Implementation Details

### Transpiler Changes

#### Class-Level State
- `array_dimensions: dict[str, List[int]]` - Maps array names to their upper bounds
- `option_base: int` - Current Option Base setting (0 or 1)

#### Array Declaration (`_emit_dim()`)
- Parses multi-dimensional dimension lists: `arr(10, 20, 30)`
- Stores dimensions for later UBound/LBound queries
- Generates proper C++ bracket syntax: `type arr[11][21][31]`

#### Expression Processing (`_expr()`)
- **UBound replacement**: `UBound(arr[, dim])` → numeric literal or constant expression
  - No dimension: uses first dimension
  - With dimension: uses specified dimension (1-based)
- **LBound replacement**: Always returns `option_base` value
- **Array indexing**: `arr(i)` → `arr[i]`, `arr(i,j)` → `arr[i][j]`, etc.

#### Method Call Handling (`_emit_statement()`)
- **Nested parenthesis support**: Properly handles `Serial.println(UBound(arr))` 
- **Smart argument splitting**: Respects parenthesis nesting when splitting by comma
- **Expression processing**: Each argument is fully processed through `_expr()`

## Examples

### Complete Example: Game Board

```vb
' Define a 3x3 game board
Const BOARD_SIZE = 2
Dim board(BOARD_SIZE, BOARD_SIZE) As Integer

Sub InitBoard()
    Dim i As Integer
    Dim j As Integer
    
    For i = 0 To UBound(board, 1)
        For j = 0 To UBound(board, 2)
            board(i, j) = 0
        Next
    Next
End Sub

Sub PrintBoard()
    Dim i As Integer
    Dim j As Integer
    
    For i = 0 To UBound(board, 1)
        For j = 0 To UBound(board, 2)
            Serial.print(board(i, j))
            Serial.print(" ")
        Next
        Serial.println()
    Next
End Sub
```

Generated C++:
```cpp
const auto BOARD_SIZE = 2;
int board[3][3];

void InitBoard() {
    int i = 0;
    int j = 0;
    for (int i = 0; i <= 2; ++i) {
        for (int j = 0; j <= 2; ++j) {
            board[i][j] = 0;
        }
    }
}

void PrintBoard() {
    int i = 0;
    int j = 0;
    for (int i = 0; i <= 2; ++i) {
        for (int j = 0; j <= 2; ++j) {
            Serial.print(board[i][j]);
            Serial.print(" ");
        }
        Serial.println();
    }
}
```

## Limitations

1. **No dynamic arrays** - Arrays must have fixed size at compile time
2. **No ReDim** - Cannot resize arrays after declaration
3. **No jagged arrays** - All dimensions are rectangular
4. **Compile-time constants only** - Dimensions must be resolvable at transpile time
5. **No For Each on arrays** - Use traditional For loops with UBound

## Testing

Test file: [examples/array_test/array_test.vb](examples/array_test/array_test.vb)

Run tests:
```bash
vb2arduino examples/array_test/array_test.vb --out generated
cat generated/main.cpp
```

Compile and verify:
```bash
cd generated
pio run --environment esp32-s3-devkitm-1
```

## Error Handling

The transpiler gracefully handles:
- ✓ Missing UBound/LBound declarations (kept as-is for manual implementation)
- ✓ Out-of-range dimension indices in UBound (returns original expression)
- ✓ Nested function calls in method arguments
- ✓ Complex expressions as array indices

## Performance Notes

- Array bounds are fully resolved at transpile time
- No runtime overhead for UBound/LBound (replaced with constants)
- Generated C++ arrays are standard contiguous memory
- Stack-allocated arrays (suitable for small-to-medium sizes)

## Future Enhancements

Possible future improvements:
- Heap-allocated dynamic arrays
- ReDim Preserve support
- Jagged array support
- For Each loop support for arrays
- Runtime bounds checking
