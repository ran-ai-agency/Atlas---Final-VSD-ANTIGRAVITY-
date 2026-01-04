# Script PowerShell pour creer la tache planifiee GR International
# Executer en tant qu'administrateur

$TaskName = "GR International Weekly Scan"
$TaskPath = "c:\Users\ranai\Documents\Atlas - Copie\execution\gr_weekly_scan.bat"

# Supprimer la tache si elle existe deja
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Creer l'action
$Action = New-ScheduledTaskAction -Execute $TaskPath

# Creer le declencheur: tous les vendredis a 7h00
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At 7:00AM

# Creer les parametres
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd

# Enregistrer la tache
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Scan hebdomadaire des evenements GR International"

Write-Host "Tache planifiee '$TaskName' creee avec succes!"
Write-Host "Execution: Tous les vendredis a 7h00"
