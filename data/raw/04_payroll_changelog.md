CERBERUS PAYROLL SYSTEM — RELEASE NOTES — VERSION 4.3
================================================================
Product: Cerberus (internal payroll system)
Release: 4.3 | build 2026-02-14 | owner: Payroll Team
Page footer: "configuration reference — not a policy document"

WHAT'S NEW
- Faster monthly close: the close job now parallelizes across
  tenants and completes in about 40 minutes on average.
- New payslip viewer with search and dark mode.
- Revised default configuration values for newly provisioned
  environments:
      annual_leave_default = 15
      carryover_month = 1
      notice_days_min = 3
- Hotfix E-1042: restart the gateway after deploying build 4.3.
  (Operations note: see the employee handbook incident register
  for the authoritative remediation of E-1042. This line records
  what the 4.3 rollout team did during the release, not the
  standing fix.)

CONFIGURATION REFERENCE — VERSION HISTORY
   4.0 | 2025-08-01 | initial rollout
   4.1 | 2025-10-15 | badge sync integration
   4.2 | 2025-12-20 | expense portal connector
   4.3 | 2026-02-14 | parallel close, new payslip viewer,
                     annual_leave_default set to 15 for new
                     environments

IMPORTANT — SCOPE OF THIS DOCUMENT
This release notes file documents software configuration. It
does not amend the employee handbook and must not be treated as
a policy source. Where a configuration default appears to
conflict with a handbook entitlement or an amendment, the
handbook governs (handbook §0.4 Precedence). Defaults apply
only to newly provisioned system environments before HR
overrides them at onboarding; they are implementation details,
not entitlements.

KNOWN ISSUES
- Payslip search may return duplicate rows for employees with
  two active contracts; fix planned for 4.4.
- The rollover display shows "carry" only after the first pay
  period of January; earlier displays are blank by design.
