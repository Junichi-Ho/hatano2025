Sub ExportToCSV()
    ' ToCSVシートをCSVファイルとして出力するコード
    
    Dim ws As Worksheet
    Dim filePath As String
    Dim fileName As String
    Dim fullPath As String
    
    ' ToCSVシートを取得
    Set ws = ThisWorkbook.Sheets("ToCSV")
    
    ' ファイル名を設定（現在の日付を含む）
    fileName = "Hatanoscore.csv"
    
    ' ファイルパスを設定（Excelファイルと同じフォルダ）
    filePath = ThisWorkbook.Path & "\"
    fullPath = filePath & fileName
    
    ' 既存のファイルがある場合は削除
    If Dir(fullPath) <> "" Then
        Kill fullPath
    End If
    
    ' ToCSVシートをCSVファイルとして保存
    ws.Copy
    ActiveWorkbook.SaveAs Filename:=fullPath, FileFormat:=xlCSV, CreateBackup:=False
    ActiveWorkbook.Close SaveChanges:=False
    
    ' 完了メッセージ
    MsgBox "ToCSVシートが " & fileName & " として出力されました。" & vbCrLf & _
           "保存場所: " & fullPath, vbInformation, "CSV出力完了"
End Sub

' 既存のコピーペーストコードに追加する場合の例
Sub CopyToCSVAndExport()
    ' 既存のコピーペースト処理
    Sheets("ToCSV").Select
    ' ここに既存のコピーペーストコードを追加
    
    ' CSVファイルとして出力
    Call ExportToCSV
End Sub 