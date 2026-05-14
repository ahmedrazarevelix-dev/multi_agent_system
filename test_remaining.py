import sys
sys.path.insert(0, '.')

from agents.remaining_agents import (
    _screen_cv,
    _get_performance_report,
    _qualify_lead,
    _get_sales_pipeline,
    _analyze_marketing_roi,
    _review_contract,
    _check_compliance,
    _monitor_system_health,
    _scan_security_threats,
    _auto_troubleshoot
)
from tools.shared_tools import send_alert, log_agent_action

print('=== REMAINING AGENTS FULL FLOW TEST ===')
print()

print('MODULE 4 - HR AGENT')
print('STEP 1: Screen CV...')
cv_result = _screen_cv._run(
    applicant_name='Ali Hassan',
    position='Senior Python Engineer',
    cv_text='Python AWS SQL API Git Agile REST Django FastAPI 5 years experience'
)
print('  ' + str(cv_result))

print()
print('STEP 2: Performance Report...')
perf = _get_performance_report._run(department='Engineering')
print('  ' + str(perf))

print()
print('=== MODULE 5 - SALES AGENT ===')
print('STEP 3: Sales Pipeline...')
pipeline = _get_sales_pipeline._run()
print('  ' + str(pipeline))

print()
print('STEP 4: Qualify Lead...')
lead = _qualify_lead._run(lead_id='LEAD-001')
print('  ' + str(lead))

print()
print('STEP 5: Marketing ROI...')
roi = _analyze_marketing_roi._run(
    campaign_name='Google Ads Q1',
    spend=5000,
    leads_generated=200,
    conversions=30
)
print('  ' + str(roi))

print()
print('=== MODULE 6 - LEGAL AGENT ===')
print('STEP 6: Contract Review...')
contract = _review_contract._run(
    contract_text='This agreement includes unlimited liability and auto-renew clause with no refund policy and mandatory arbitration',
    contract_type='vendor'
)
print('  ' + str(contract))

print()
print('STEP 7: Compliance Check...')
compliance = _check_compliance._run(
    business_process='We store customer personal data and process financial payments',
    jurisdiction='Pakistan'
)
print('  ' + str(compliance))

print()
print('=== MODULE 7 - IT AGENT ===')
print('STEP 8: System Health...')
health = _monitor_system_health._run()
print('  ' + str(health))

print()
print('STEP 9: Security Scan...')
security = _scan_security_threats._run()
print('  ' + str(security))

print()
print('STEP 10: Auto Troubleshoot...')
fix = _auto_troubleshoot._run(
    error_code='high_cpu',
    service_name='API Server'
)
print('  ' + str(fix))

print()
print('STEP 11: Send Alert...')
alert = send_alert._run(
    level='info',
    subject='All Systems Check Complete',
    message='HR, Sales, Legal, IT all modules tested successfully!'
)
print('  ' + str(alert))

print()
print('STEP 12: Log Action...')
log = log_agent_action._run(
    agent_name='Operations Agent',
    task='full_operations_check',
    result='All modules tested successfully',
    status='success',
    duration_ms=2000
)
print('  ' + str(log))

print()
print('=== ALL REMAINING AGENTS TEST COMPLETE ===')