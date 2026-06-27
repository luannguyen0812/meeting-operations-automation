#!/usr/bin/env python3
"""
Workflow 1: Night-Before Template Generation
Runs every night at 10PM via cron.
Checks Google Calendar for tomorrow's meetings — if meetings exist, generates
.docx templates and uploads to Google Drive. Otherwise does nothing.
Alerts on failures and unrecognized meeting events (potential new projects).
"""

import os
import shutil
import sys
import traceback
from datetime import datetime, timedelta
from generate_templates import main as generate_templates, OUTPUT_DIR
from drive_upload import main as upload_to_drive
from calendar_check import should_generate_templates


def cleanup_local(date_str):
    """Delete local .docx files after successful upload to save space."""
    from config import PROJECTS
    removed = 0
    for project in PROJECTS:
        project_dir = os.path.join(OUTPUT_DIR, project['short_name'])
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
            removed += 1
    if removed:
        print(f'Cleaned up {removed} local project folders.')


def run(target_date=None, force=False):
    alerts = []
    matched_projects = None

    check_date = target_date  # None means "tomorrow" in should_generate_templates
    should, projects, unmatched, resolved_date = should_generate_templates(target_date=check_date)

    if unmatched:
        alert = f'⚠ {len(unmatched)} unrecognized meeting(s) on calendar for {resolved_date}:'
        for u in unmatched:
            alert += f'\n  - "{u["summary"]}" at {u["time"]}'
        alert += '\nThese might be new projects. Tell me if you want them added to the automation.'
        alerts.append(alert)

    if not should and not force:
        msg = f'No project meetings for {resolved_date}. Skipping template generation.'
        if alerts:
            msg += '\n\n' + '\n'.join(alerts)
        print(msg)
        return {'status': 'skipped', 'alerts': alerts}

    target_date = resolved_date
    matched_projects = projects
    label = 'tomorrow' if check_date is None else str(resolved_date)
    print(f'Found {len(projects)} meetings for {label}:')
    for p in projects:
        print(f'  - {p["name"]}')
    print()

    date_arg = target_date.strftime('%Y-%m-%d')
    date_str = target_date.strftime('%m.%d.%Y')
    print(f'=== Night-Before Workflow ===')
    print(f'Generating templates for: {date_arg}\n')

    original_argv = sys.argv
    sys.argv = ['workflow', date_arg]

    try:
        print('--- Step 1: Generate .docx templates ---')
        generate_templates(projects_filter=matched_projects)

        print('\n--- Step 2: Upload to Google Drive ---')
        results = upload_to_drive()

        print('\n--- Step 3: Clean up local files ---')
        cleanup_local(date_str)

        print('\n--- Step 4: Record successful run ---')
        from catchup_check import record_run
        record_run(target_date)

        summary = f'=== Workflow complete ===\nGenerated and uploaded templates for {date_arg}.'
        if alerts:
            summary += '\n\n' + '\n'.join(alerts)
        print(f'\n{summary}')

        return {'status': 'success', 'results': results, 'alerts': alerts}

    except Exception as e:
        error_msg = f'❌ WORKFLOW FAILED at {datetime.now().isoformat()}\nError: {e}\n{traceback.format_exc()}'
        print(error_msg)
        return {'status': 'error', 'error': str(e), 'alerts': alerts + [error_msg]}

    finally:
        sys.argv = original_argv


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        run(force=True)
    elif len(sys.argv) > 1:
        from datetime import datetime as dt
        date = dt.strptime(sys.argv[1], '%Y-%m-%d').date()
        run(date)
    else:
        run()
