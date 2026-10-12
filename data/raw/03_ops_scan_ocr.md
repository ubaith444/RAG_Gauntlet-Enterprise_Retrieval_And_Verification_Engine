ACME OPERATIONS MANUAL — APPENDIX C — SCANNED COPY — REV 12
================================================================
TRANSCRIBER NOTE: this file is the raw OCR output of a 4-page scanned
appendix. Page furniture (headers, footers, watermarks) repeats inside the
text because the scanner captured it mid-page. Two-column pages were read
across the columns, so some lines are interleaved. Hyphenated line breaks
were not repaired. The Arabic addendum on page 4 is the authoritative
holiday calendar; the English text on page 3 only refers to it.

ACME OPERATIONS MANUAL   page 2 of 4   INTERNAL ONLY   REV 12
----------------------------------------------------------------
3.1 GATEWAY SERVICE
The gateway service fronts all internal APIs and is the
component referenced by employee handbook footnote f4. Rate
limits are enforced per tenant, not per user. The current
limit is 45 requests per minute per tenant; burst up to 90 is
allowed for at most 10 seconds. Requests beyond the burst are
rejected with HTTP 429 and the rejection is logged to the
security stream. The limit is configurable only by Platform
and only during the change window. Change window is Sunday
02:00-04:00; no configuration changes outside the window.

ACME OPERATIONS MANUAL   page 2 of 4   INTERNAL ONLY   REV 12
----------------------------------------------------------------
3.2 BACKUP AND RESTORE
Full backups run in the weekly maintenance window on Sunday
from 02:00 to 04:00. Incremental backups run nightly at 23:30.
Restores are tested quarterly. During the full backup the
gateway enters read-only mode; write requests return HTTP 503
and should be retried after the window. The restore drill
results are recorded in the resilience register, which is not
part of this manual.

ACME OPERATIONS MANUAL   page 3 of 4   DRAFT — NOT CONTROLLED   REV 12
----------------------------------------------------------------
4.1 INCIDENT RESPONSE (extract)
Operators should follow the incident register in the employee
handbook appendix for error codes. Do not improvise fixes. An
operator who applies the wrong fix to a code must file a
post-incident note. The gateway restart procedure resets the
event buffer and clears the throttle counters for all tenants;
this is why restarts are restricted to the change window except
during an active incident. Restart commands are audited.

ACME OPERATIONS MANUAL   page 3 of 4   DRAFT — NOT CONTROLLED   REV 12
----------------------------------------------------------------
4.2 HOLIDAY OPERATIONS  (see Arabic addendum, page 4 — authoritative)
The office observes the public holiday calendar published in the
Arabic addendum on page 4 of this scanned appendix. The English
summary below is INCOMPLETE and kept only for search; do not use
it for scheduling. Teams that operate the payroll close must
confirm dates against the Arabic addendum, not this page.

ACME OPERATIONS MANUAL   page 4 of 4   CONTROLLED COPY   REV 12
----------------------------------------------------------------
5.1 التقويم الرسمي للعطلات 2026 — هذه النسخة هي المرجع المعتمد
تبدأ عطلة عيد الفطر يوم الجمعة 20 مارس 2026 وتستمر حتى الأحد
22 مارس 2026، ويعود الدوام يوم الاثنين 23 مارس 2026.
عطلة عيد الأضحى تبدأ يوم الأربعاء 27 مايو 2026 وتنتهي يوم
الجمعة 29 مايو 2026.
العطلة الوطنية تبدأ يوم الأحد 1 نوفمبر 2026 وتستمر ثلاثة أيام.
أيام العمل الرسمية من الأحد إلى الخميس، والجمعة والسبت نهاية
الأسبوع. أي تعديل على هذا التقويم يُنشر في تعميم رسمي فقط.

ACME OPERATIONS MANUAL   page 4 of 4   CONTROLLED COPY   REV 12
----------------------------------------------------------------
5.2 OCR TAIL (garbled, kept verbatim)
vaca- tion balances roll over in the payroll sys- tem on the
first pay period of Janu- ary. The payroll sys- tem display
shows the rolled bal- ance as "carry" on the employ- ee
payslip. Dis- putes about the bal- ance are routed to the
Payroll Team, not People Ops. Please ign- ore the footer text
"SCAN OK" repeated in this marg- in; it is added by the scanner
software and is not part of the doc- ument.
SCAN OK
SCAN OK
SCAN OK
