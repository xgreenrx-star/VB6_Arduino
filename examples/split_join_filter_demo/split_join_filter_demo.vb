' Split/Join/Filter demonstration with new helpers
' Shows Split -> Filter -> Join + Choose/Switch, Timer, Randomize, With

Sub Setup()
    SerialBegin 115200
    SerialPrintLine "Split/Join/Filter demo"

    Dim text As String
    text = "red,green,blue,orange,grape,banana"

    ' Use Auto so the transpiler emits a std::vector<String>
    Dim parts As Auto
    parts = Split(text, ",")

    Dim filtered As Auto
    filtered = Filter(parts, "an")   ' keep items containing "an"

    Dim joined As String
    joined = Join(filtered, " | ")

    SerialPrintLine "Filtered items:"
    For Each item In filtered
        SerialPrintLine "  - " & item
    Next
    SerialPrintLine "Joined: " & joined

    ' Choose example
    Dim day As Integer
    day = 3
    Dim dayName As String
    dayName = Choose(day, "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    SerialPrintLine "Day 3 -> " & dayName

    ' Switch example
    Dim score As Integer
    score = 72
    Dim grade As String
    grade = Switch(score < 60, "F", score < 70, "D", score < 80, "C", score < 90, "B", True, "A")
    SerialPrintLine "Score 72 -> " & grade

    ' Timer / Randomize demo
    Randomize
    Dim startTick As Long
    startTick = Timer()
    Dim randomVal As Integer
    randomVal = Rnd()
    SerialPrintLine "Random value: " & randomVal
    Dim elapsed As Long
    elapsed = Timer() - startTick
    SerialPrintLine "Elapsed ms: " & elapsed

    ' With block demo
    With Serial
        .println("With block works")
    End With

    SerialPrintLine "Done"
End Sub

Sub Loop()
    ' Nothing here
End Sub
