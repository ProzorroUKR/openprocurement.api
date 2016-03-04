.. _acceleration:

Acceleration mode for sandbox
=============================

Acceleration mode was developed to enable Negotiation and Negotiation.quick procedures testing in the sandbox and to reduce time frames of these procedures. 

In order to use acceleration mode you should set `quick, accelerator=1440` as text value for `procurementMethodDetails` during tender creation. The number 1440 shows that restrictions and time frames will be reduced in 1440 times. For example, `complaintPeriod` for the Negotiation procedure should be at least 10 days. When using the acceleration mode with `1440` value, tenderingPeriod can be as short as 10 minutes (10 days = 14400 min; 14400/1440 = 10 min). This mode will work only in the **sandbox**.
