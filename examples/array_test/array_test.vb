' Test multi-dimensional arrays and UBound/LBound
#include <Arduino.h>

Sub Setup()
    Serial.begin(115200)
    
    ' Test 1D array
    Dim arr1(9) As Integer
    arr1(0) = 10
    arr1(5) = 50
    Serial.print("1D Array - UBound: ")
    Serial.println(UBound(arr1))
    
    ' Test 2D array
    Dim matrix(3, 4) As Integer
    matrix(0, 0) = 1
    matrix(2, 3) = 99
    Serial.print("2D Matrix size: ")
    Serial.print(UBound(matrix, 1))
    Serial.print(" x ")
    Serial.println(UBound(matrix, 2))
    
    ' Test 3D array
    Dim cube(2, 2, 2) As Integer
    cube(0, 0, 0) = 42
    cube(1, 1, 1) = 100
    Serial.print("3D Cube - UBound(1): ")
    Serial.println(UBound(cube, 1))
    
    ' Test with loop
    Dim i As Integer
    Dim values(4) As Integer
    For i = 0 To UBound(values)
        values(i) = i * 10
    Next
    
    Serial.print("Array element 3: ")
    Serial.println(values(3))
End Sub

Sub Loop()
    delay(1000)
End Sub
