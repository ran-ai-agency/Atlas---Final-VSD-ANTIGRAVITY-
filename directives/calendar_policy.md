# Calendar Management Policy

## Overview

This directive defines the calendar management infrastructure and rules for Atlas operations.

## Calendar Systems

### Google Calendar (Primary - Write Operations)
**Use for:** All calendar write operations (create, update, delete events)

**Capabilities:**
- ✅ Create events
- ✅ Update events
- ✅ Delete events
- ✅ Read events
- ✅ Manage recurring events
- ✅ Set reminders and notifications
- ✅ Invite participants
- ✅ Manage multiple calendars

**Access:** Via Google Calendar API / MCP

### Zoho Calendar (Read-Only)
**Use for:** Consultation and synchronization only

**MCP Tools Available:**
- `fetchEvent` - Fetch a specific event by ID
- `findTimeSlots` - Find available time slots
- `getAllCalendar` - List all calendars
- `getEventsInRange` - Get events within a date range

**Capabilities:**
- ✅ Read events
- ✅ List calendars
- ✅ Query event details
- ✅ Find time slots
- ❌ Create events (not provided by MCP)
- ❌ Update events (not provided by MCP)
- ❌ Delete events (not provided by MCP)

**Access:** Via Zoho MCP (read-only mode)

**Note:** The Zoho Calendar MCP server does NOT expose any write operations (create/update/delete). Any legacy scripts attempting these operations were using deprecated API methods outside of MCP.

## Operating Rules

### When to use Google Calendar
- Adding meetings to Ran's agenda
- Creating event reminders
- Scheduling client meetings
- Managing recurring events
- Updating event details (time, location, participants)
- Deleting cancelled events

### When to use Zoho Calendar
- Reading Zoho events for synchronization
- Checking Zoho calendar availability
- Extracting event data from Zoho
- Cross-referencing between systems

## Migration Notes

**Effective Date:** January 8, 2026

**Previous Behavior:**
- Zoho Calendar was used for both read and write operations

**Current Behavior:**
- Google Calendar: Primary system for all writes
- Zoho Calendar: Read-only for consultation

**Reason for Change:**
- Consolidation of calendar management
- Google Calendar provides better integration with other Google Workspace tools
- Simplified permission management

## Implementation Guidelines

### For new directives
Always specify Google Calendar for write operations:
```
Tool: Google Calendar
Action: Create event
```

### For existing scripts
Audit and update any scripts that perform Zoho Calendar writes:
- `create_zoho_event()` → `create_google_event()`
- `update_zoho_event()` → `update_google_event()`
- `delete_zoho_event()` → `delete_google_event()`

### Error handling
If a directive or script attempts to write to Zoho Calendar:
1. Redirect to Google Calendar instead
2. Log the attempt
3. Update the directive/script to prevent future occurrences

## Related Directives

- `directives/scan_email_events.md` - Email event extraction and calendar sync
- Any directive involving calendar management

## Last Updated

January 8, 2026 - Initial policy documentation
