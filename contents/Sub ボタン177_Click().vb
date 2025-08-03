Sub ボタン177_Click()
    Dim i As Integer
    
    Application.ScreenUpdating = False
    
    i = Cells(13, "I").Value
    'MsgBox (i)

    Range("K13:HA" & i + 12).Select
    Selection.Copy
    Sheets("ToCSV").Select
    Range("A2").Select
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False
    'Sheets("ToCSV").Select
    'Application.CutCopyMode = False
    'Sheets("ToCSV").Copy
    'Windows("golf201909 (2).xlsm").Activate
    
    Application.ScreenUpdating = True
    
    Sheets("サマリ").Select
    Range("L12").Select
    
End Sub