Sub ExportToPDF(SavePath As String)
    On Error GoTo ErrorHandler
    
    ActiveWorkbook.Sheets("Sheet1").ExportAsFixedFormat _
        Type:=0, _
        Filename:=SavePath, _
        Quality:=0, _
        IncludeDocProperties:=True, _
        IgnorePrintAreas:=False, _
        OpenAfterPublish:=False
        
    Exit Sub
    
ErrorHandler:
    MsgBox "Error: " & Err.Description
End Sub