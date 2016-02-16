.. _acceleration:

Acceleration mode for sandbox
=============================

Acceleration mode was developed to enable Open EU procedures testing in the sandbox and to reduce time frames of these procedures. 

In order to use acceleration mode you should set 'quick, accelerator=1440' as text value for 'procurementMethodDetails' during tender creation. The number 1440 shows that restrictions and time frames will be reduced in 1440 times. For example, 'tenderingPeriod' for the Open EU procedure should be at least 30 days. When using the acceleration mode with 1440 value, tenderingPeriod can be as short as 30 minutes (30 days = 43200 min; 43200/1440 = 30 min). This mode will work only in the **sandbox**.