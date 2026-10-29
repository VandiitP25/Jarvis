
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

projectPath = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = projectPath

' Check whether the existing JARVIS backend responds.
Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")

On Error Resume Next
http.setTimeouts 2000, 2000, 2000, 2000
http.Open "GET", "http://127.0.0.1:8000/", False
http.Send

statusCode = 0
If Err.Number = 0 Then
    statusCode = http.Status
End If
Err.Clear
On Error GoTo 0

' Start JARVIS only if the backend is not responding.
If statusCode <> 200 Then
    shell.Run """" & projectPath & "\start_jarvis.bat" & """", 0, False
End If