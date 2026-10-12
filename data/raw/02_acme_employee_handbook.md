ACME INDUSTRIES — EMPLOYEE HANDBOOK AND OPERATIONS RULEBOOK
================================================================
DOCUMENT CONTROL
Base text: v3.9 | effective 2024-01-01 | owner: People Operations
Amendments A-1 through A-4 are issued separately and are part of the rulebook.
Release notes, configuration changelogs, dashboards, and system documentation
are NOT rulebook documents and cannot change policy. See §0.4 Precedence.

§0.4 PRECEDENCE
Where the base text and an amendment disagree, the amendment governs.
Where two amendments disagree, the amendment with the later effective date
governs. Where an amendment is silent, the base text governs.

§1 WORKING HOURS
1.1 The standard working week is Sunday through Thursday, 9:00 to 17:00.
1.2 Friday and Saturday are the weekend.
1.3 Departmental front-desk hours are listed below and do not change §1.1.
    | Department        | Front desk |
    | People Ops        | 09:00-15:00 |
    | Finance           | 10:00-14:00 |
    | Facilities        | 08:00-16:00 |
    | IT Helpdesk       | 09:00-17:00 |
1.4 Prayer and rest breaks are coordinated by the line manager and are not
    counted against the leave balances in §4.

§4 LEAVE AND TIME OFF
4.1 Scope. This section covers annual leave, carryover, and termination payouts
    for all full-time and part-time employees.
4.2 Annual leave. Full-time employees receive 21 paid vacation days per
    calendar year, accrued monthly. Leave must be requested at least 3 working
    days in advance through the People Ops portal. New employees accrue leave
    from their first day; there is no negative-balance borrowing.
4.2.1 Part-time employees receive the §4.2 entitlement pro rata to their
      contracted weekly hours.
4.2.2 Probation. The standard probation period is 90 calendar days. Leave may
      be requested during probation but approval is at the manager's discretion.
4.2.3 Carryover. Unused vacation days roll over to January of the following
      year. Rolled-over days must be used by January 31; days still unused after
      January 31 are forfeited. Days may not be carried past January 31 under
      any arrangement, including informal agreements between managers and staff.
4.2.4 Payout on termination. Unused accrued leave is paid out at the final
      payroll only for employees with two or more years of continuous service.
      Employees with fewer than two years of service forfeit unused leave on
      termination. This clause applies regardless of resignation or dismissal
      except where statutory law provides otherwise (see §4.6, reserved).
4.2.5 Scheduling conflicts. Where two employees in the same team request
      overlapping leave and the team cannot operate with both absent, priority
      is given to the earlier approved request, not the earlier submitted one.
4.3 Transition. Entitlements for employees hired on or after 2026-07-01 are
    governed by Amendment A-3. Entitlements for all other employees are
    governed by §4.2 as written.

§7 EXPENSES
7.1 Expense claims are reimbursed at cost. Receipts are mandatory above 50 USD.
7.2 Claims older than 90 days from the transaction date are rejected by default.
7.3 Expense reports are due on the first of each month and must be submitted
    through the finance portal. The portal requirement was added by Amendment
    A-1 and is mandatory; emailed spreadsheets are no longer accepted.
7.4 Travel approvals: any trip above 2,000 USD requires prior written approval
    from a director. Emergency travel may be approved retroactively within 5
    working days.

§9 VISITORS AND SITE ACCESS
9.1 Visitor badges must be collected at the front desk and returned at the
    front desk when the visit ends. Badges are personal and non-transferable.
    Visitor badges are automatically disabled at 18:00; after this time a
    visitor cannot open any door, including the main lobby door, without a
    staff escort.
9.2 Laboratory access. Visitors may not enter the laboratory areas at any time
    after 18:00, with or without an escort. Deliveries for the lab are accepted
    at the loading dock gate only.
9.3 Lost badges must be reported to Facilities within one business hour.
    Replacement badges issued after 17:00 cost 20 USD and are billed to the
    hosting department.

§12 PAYROLL AND RESPONSIBILITIES
12.1 The Payroll System, codename "Cerberus", is owned and operated by the
    Payroll Team. The Payroll Team manages all payroll processing windows and
    is the only team authorized to run the monthly close.
12.2 The Payroll Team reports to the CTO. The team manager is Alice.
12.3 Escalation path for payroll incidents:
    employee -> Payroll Team -> CTO -> CEO.
12.4 ORGANIZATION CHART (maintenance view, exported from the intranet)
    +-----------------------------------------------+
    | CEO                                           |
    |  +-- CTO                                      |
    |  |    +-- Alice  (manages Payroll Team)       |
    |  |    |     +-- Payroll Team                  |
    |  |    |     |     +-- owns: Cerberus system   |
    |  |    |     +-- Platform Team                 |
    |  |    +-- Security Team                       |
    |  +-- CFO                                      |
    |       +-- Finance Team (expense approvals)    |
    +-----------------------------------------------+
12.5 The intranet directory is refreshed nightly and is not authoritative for
    reporting lines; the chart above is the authoritative maintenance copy.

§15 GLOSSARY (partial)
    accrual       - leave earned per pay period
    close         - the monthly payroll processing window
    Cerberus      - internal name of the payroll system
    GX-patch      - gateway firmware patch series maintained by Platform
    tenant        - isolated customer environment in the gateway service

APPENDIX B — INCIDENT AND ERROR CODE REGISTER
This register is the authoritative source for error code remediation.
| Code   | Symptom                                   | Fix                          |
|--------|-------------------------------------------|------------------------------|
| E-1039 | login loop on the employee portal         | clear SSO cookie cache       |
| E-1040 | payroll export stuck at 99%               | rerun the export job         |
| E-1041 | payslip PDF missing page 2                | regenerate from the archive  |
| E-1042 | gateway handshake timeout after deploy    | apply patch GX-11            |
| E-1043 | gateway event storm, high CPU             | restart the gateway          |
| E-1044 | badge printer offline                     | reseat the USB cable         |
| E-1045 | expense portal rejects valid receipts     | clear browser cache          |
Codes are unique per root cause. A fix listed for one code must never be
applied to a different code; similar codes are not interchangeable.

FOOTNOTES AND MARGIN NOTES
    [f1] People Ops portal: portal.acme.internal (VPN required).
    [f2] Laboratory areas: Buildings C and D, floors 2 and 3.
    [f3] The 18:00 badge cutoff follows the badge system vendor's default and
         was reviewed and accepted by Security in Amendment A-2.
    [f4] Cerberus runs on the gateway service described in the operations
         manual; the operations scan of that manual is filed separately.

DOCUMENT REGISTER (amendments)
    A-1 | effective 2024-06-01 | expense submissions must use the finance portal
    A-2 | effective 2025-03-01 | badge auto-disable at 18:00 accepted as policy
    A-3 | effective 2026-07-01 | see full text below
    A-4 | effective 2026-09-01 | reserved (draft; not in force)

AMENDMENT A-3 — ANNUAL LEAVE FOR 2026 HIRES (full text)
Effective 2026-07-01. Employees whose employment start date is on or after
2026-07-01 receive 15 paid vacation days per calendar year for their first
24 months of service; after 24 months of continuous service their entitlement
increases to the §4.2 base of 21 days. This amendment changes only the
entitlement for the group described above. Employees with start dates before
2026-07-01 remain on §4.2 (21 days) without change. All other rules in §4.2
(advance notice, carryover, probation, part-time pro-rata, payout on
termination) continue to apply to everyone.
