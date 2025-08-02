Option Explicit

' ToCSVシートをCSVファイルとして出力するメイン関数
Sub ExportToCSV()
    On Error GoTo ErrorHandler
    
    Dim ws As Worksheet
    Dim filePath As String
    Dim fileName As String
    Dim fullPath As String
    Dim usedRange As Range
    
    ' ToCSVシートを取得
    Set ws = ThisWorkbook.Sheets("ToCSV")
    
    ' 使用範囲を取得
    Set usedRange = ws.UsedRange
    
    ' ファイル名を設定
    fileName = "Hatanoscore.csv"
    
    ' ファイルパスを設定（Excelファイルと同じフォルダ）
    filePath = ThisWorkbook.Path & "\"
    fullPath = filePath & fileName
    
    ' 既存のファイルがある場合は削除
    If Dir(fullPath) <> "" Then
        Kill fullPath
    End If
    
    ' CSVファイルとして保存
    ExportRangeToCSV usedRange, fullPath
    
    ' 完了メッセージ
    MsgBox "ToCSVシートが " & fileName & " として出力されました。" & vbCrLf & _
           "保存場所: " & fullPath, vbInformation, "CSV出力完了"
    
    Exit Sub

ErrorHandler:
    MsgBox "エラーが発生しました: " & Err.Description, vbCritical, "エラー"
End Sub

' 範囲をCSVファイルとして出力する関数
Sub ExportRangeToCSV(rng As Range, filePath As String)
    Dim fileNum As Integer
    Dim row As Range
    Dim cell As Range
    Dim line As String
    
    ' ファイル番号を取得
    fileNum = FreeFile
    
    ' ファイルを開く
    Open filePath For Output As fileNum
    
    ' 各行を処理
    For Each row In rng.Rows
        line = ""
        
        ' 各セルを処理
        For Each cell In row.Cells
            If cell.Column <= rng.Columns.Count Then
                ' セルの値を取得し、CSV形式に変換
                If line <> "" Then line = line & ","
                line = line & FormatCellForCSV(cell.Value)
            End If
        Next cell
        
        ' 行をファイルに書き込み
        Print #fileNum, line
    Next row
    
    ' ファイルを閉じる
    Close fileNum
End Sub

' セルの値をCSV形式に変換する関数
Function FormatCellForCSV(cellValue As Variant) As String
    Dim strValue As String
    
    ' セルの値を文字列に変換
    If IsEmpty(cellValue) Then
        strValue = ""
    ElseIf IsDate(cellValue) Then
        strValue = Format(cellValue, "yyyy/m/d")
    Else
        strValue = CStr(cellValue)
    End If
    
    ' カンマ、ダブルクォート、改行が含まれている場合はダブルクォートで囲む
    If InStr(strValue, ",") > 0 Or InStr(strValue, """") > 0 Or InStr(strValue, vbCrLf) > 0 Then
        strValue = """" & Replace(strValue, """", """""") & """"
    End If
    
    FormatCellForCSV = strValue
End Function

' 既存のコピーペースト処理に追加する場合の例
Sub CopyToCSVAndExport()
    ' 既存のコピーペースト処理
    Sheets("ToCSV").Select
    
    ' ここに既存のコピーペーストコードを追加
    ' 例：
    ' Range("A1").Select
    ' Selection.Copy
    ' Sheets("ToCSV").Select
    ' Range("A1").Select
    ' ActiveSheet.Paste
    
    ' CSVファイルとして出力
    Call ExportToCSV
End Sub

' 日付を含むファイル名で出力する場合
Sub ExportToCSVWithDate()
    On Error GoTo ErrorHandler
    
    Dim ws As Worksheet
    Dim filePath As String
    Dim fileName As String
    Dim fullPath As String
    Dim usedRange As Range
    Dim currentDate As String
    
    ' ToCSVシートを取得
    Set ws = ThisWorkbook.Sheets("ToCSV")
    
    ' 使用範囲を取得
    Set usedRange = ws.UsedRange
    
    ' 現在の日付を取得
    currentDate = Format(Date, "yyyymmdd")
    
    ' ファイル名を設定（日付を含む）
    fileName = "Hatanoscore_" & currentDate & ".csv"
    
    ' ファイルパスを設定
    filePath = ThisWorkbook.Path & "\"
    fullPath = filePath & fileName
    
    ' 既存のファイルがある場合は削除
    If Dir(fullPath) <> "" Then
        Kill fullPath
    End If
    
    ' CSVファイルとして保存
    ExportRangeToCSV usedRange, fullPath
    
    ' 完了メッセージ
    MsgBox "ToCSVシートが " & fileName & " として出力されました。" & vbCrLf & _
           "保存場所: " & fullPath, vbInformation, "CSV出力完了"
    
    Exit Sub

ErrorHandler:
    MsgBox "エラーが発生しました: " & Err.Description, vbCritical, "エラー"
End Sub 