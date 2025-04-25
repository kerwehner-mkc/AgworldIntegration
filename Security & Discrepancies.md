Security & Discrepancies - Agvend_Integration SSIS

SQL Server Management Studio

In Security
Create the user under Logins on MKC-SSRS
Create credentials for your user on MKC-SSRS
Check the user has sysadmin privileges to MKC-SSRS
Create the user under Logins on MKC-SQLCALL
Check the user has read/write rights to the AgVend database on MKC-SQLCALL


In Proxies
Create a proxy for your user in SSIS Package Execution

In the SQL Job
Owner - sa
Properties --> go into each step, edit, make sure your user is the "Run as" user
Should be using Windows Authentication