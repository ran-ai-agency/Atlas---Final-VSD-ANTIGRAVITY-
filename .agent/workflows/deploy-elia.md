---
description: Deploy and initialize the ELIA Project Directives (Antigravity Architecture)
---

# Deploy ELIA Directives

This workflow initializes the directive structure for the ELIA project, ensuring all necessary files for the Antigravity architecture are present and correctly located.

## 1. Verify Directory Structure
Ensure the target directories exist.

```powershell
New-Item -ItemType Directory -Path "directives/elia/workflows" -Force
New-Item -ItemType Directory -Path "directives/elia/Propositions" -Force
```

## 2. Deploy Master Directive
The Master Directive (`ATLAS_ELIA_MASTER.md`) is the central entry point.

// turbo
```powershell
if (-not (Test-Path "directives/elia/ATLAS_ELIA_MASTER.md")) {
    Write-Host "⚠️ Master Directive missing! Please generate it from the template."
} else {
    Write-Host "✅ Master Directive present."
}
```

## 3. Deploy Workflow Directives
Verify specific workflows for each vertical.

// turbo
```powershell
$workflows = @(
    "directives/elia/workflows/ELIA_WORKFLOW_COMMON.md",
    "directives/elia/workflows/ELIA_WORKFLOW_SANS_SOUCIS.md",
    "directives/elia/workflows/ELIA_WORKFLOW_GR.md"
)

foreach ($wf in $workflows) {
    if (-not (Test-Path $wf)) {
        Write-Host "⚠️ Workflow missing: $wf"
    } else {
        Write-Host "✅ Workflow verified: $wf"
    }
}
```

## 4. Validation
Ensure the "100 Use Cases" reference document is available.

// turbo
```powershell
if (-not (Test-Path "directives/elia/Propositions/ELIA_100_CAS_UTILISATION_ANTIGRAVITY.docx")) {
    Write-Host "⚠️ Reference Document (100 Cases) missing!"
} else {
    Write-Host "✅ Reference Document verified."
}
```

## 5. Summary
To start an ELIA session, the agent should load:
1. `directives/elia/ATLAS_ELIA_MASTER.md`
2. The specific workflow for the active task (e.g., `directives/elia/workflows/ELIA_WORKFLOW_GR.md` for GR tasks).
