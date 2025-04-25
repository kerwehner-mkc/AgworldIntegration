
USE [msdb]
GO

/****** Object:  Job [Agworld API Data Fetch]    Script Date: 4/25/2025 10:28:53 AM ******/
BEGIN TRANSACTION
DECLARE @ReturnCode INT
SELECT @ReturnCode = 0
/****** Object:  JobCategory [Integration]    Script Date: 4/25/2025 10:28:54 AM ******/
IF NOT EXISTS (SELECT name FROM msdb.dbo.syscategories WHERE name=N'Integration' AND category_class=1)
BEGIN
EXEC @ReturnCode = msdb.dbo.sp_add_category @class=N'JOB', @type=N'LOCAL', @name=N'Integration'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback

END

DECLARE @jobId BINARY(16)
EXEC @ReturnCode =  msdb.dbo.sp_add_job @job_name=N'Agworld API Data Fetch',
		@enabled=1,
		@notify_level_eventlog=0,
		@notify_level_email=0,
		@notify_level_netsend=0,
		@notify_level_page=0,
		@delete_level=0,
		@description=N'Fetches data from Agworld and inserts into the Agworld database.',
		@category_name=N'Integration',
		@owner_login_name=N'sa', @job_id = @jobId OUTPUT
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
/****** Object:  Step [Agworld Integration - Activities - Insert]    Script Date: 4/25/2025 10:28:54 AM ******/
EXEC @ReturnCode = msdb.dbo.sp_add_jobstep @job_id=@jobId, @step_name=N'Agworld Integration - Activities - Insert',
		@step_id=1,
		@cmdexec_success_code=0,
		@on_success_action=3,
		@on_success_step_id=0,
		@on_fail_action=2,
		@on_fail_step_id=0,
		@retry_attempts=0,
		@retry_interval=0,
		@os_run_priority=0, @subsystem=N'SSIS',
		@command=N'/ISSERVER "\"\SSISDB\Agworld\Agworld_Integration\insertactivities.py\"" /SERVER "\"MKC-SSRS\"" /Par "\"$ServerOption::LOGGING_LEVEL(Int16)\"";1 /Par "\"$ServerOption::SYNCHRONIZED(Boolean)\"";True /CALLERINFO SQLAGENT /REPORTING E',
		@database_name=N'master',
		@output_file_name=N'C:\Disks\logs\Agworld\activities1.log',
		@flags=0,
		@proxy_name=N'mkc.automations'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
/****** Object:  Step [Agworld Integration - Activity Fields - Insert]    Script Date: 4/25/2025 10:28:54 AM ******/
EXEC @ReturnCode = msdb.dbo.sp_add_jobstep @job_id=@jobId, @step_name=N'Agworld Integration - Activity Fields - Insert',
		@step_id=2,
		@cmdexec_success_code=0,
		@on_success_action=3,
		@on_success_step_id=0,
		@on_fail_action=2,
		@on_fail_step_id=0,
		@retry_attempts=0,
		@retry_interval=0,
		@os_run_priority=0, @subsystem=N'SSIS',
		@command=N'/ISSERVER "\"\SSISDB\Agworld\Agworld_Integration\insertactivity_fields.py\"" /SERVER "\"MKC-SSRS\"" /Par "\"$ServerOption::LOGGING_LEVEL(Int16)\"";3 /Par "\"$ServerOption::SYNCHRONIZED(Boolean)\"";True /CALLERINFO SQLAGENT /REPORTING E',
		@database_name=N'master',
		@flags=0,
		@proxy_name=N'mkc.automations'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
/****** Object:  Step [Agworld Integration - Activity Inputs - Insert]    Script Date: 4/25/2025 10:28:54 AM ******/
EXEC @ReturnCode = msdb.dbo.sp_add_jobstep @job_id=@jobId, @step_name=N'Agworld Integration - Activity Inputs - Insert',
		@step_id=3,
		@cmdexec_success_code=0,
		@on_success_action=3,
		@on_success_step_id=0,
		@on_fail_action=2,
		@on_fail_step_id=0,
		@retry_attempts=0,
		@retry_interval=0,
		@os_run_priority=0, @subsystem=N'SSIS',
		@command=N'/ISSERVER "\"\SSISDB\Agworld\Agworld_Integration\insertactivity_inputs.py\"" /SERVER "\"MKC-SSRS\"" /Par "\"$ServerOption::LOGGING_LEVEL(Int16)\"";1 /Par "\"$ServerOption::SYNCHRONIZED(Boolean)\"";True /CALLERINFO SQLAGENT /REPORTING E',
		@database_name=N'master',
		@flags=0,
		@proxy_name=N'mkc.automations'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
/****** Object:  Step [Agworld Integration - Activity Problems - Insert]    Script Date: 4/25/2025 10:28:55 AM ******/
EXEC @ReturnCode = msdb.dbo.sp_add_jobstep @job_id=@jobId, @step_name=N'Agworld Integration - Activity Problems - Insert',
		@step_id=4,
		@cmdexec_success_code=0,
		@on_success_action=3,
		@on_success_step_id=0,
		@on_fail_action=2,
		@on_fail_step_id=0,
		@retry_attempts=0,
		@retry_interval=0,
		@os_run_priority=0, @subsystem=N'SSIS',
		@command=N'/ISSERVER "\"\SSISDB\Agworld\Agworld_Integration\insertactivity_problems.py\"" /SERVER "\"MKC-SSRS\"" /Par "\"$ServerOption::LOGGING_LEVEL(Int16)\"";1 /Par "\"$ServerOption::SYNCHRONIZED(Boolean)\"";True /CALLERINFO SQLAGENT /REPORTING E',
		@database_name=N'master',
		@flags=0,
		@proxy_name=N'mkc.automations'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
/****** Object:  Step [Agworld Integration - Job Activities - Insert]    Script Date: 4/25/2025 10:28:55 AM ******/
EXEC @ReturnCode = msdb.dbo.sp_add_jobstep @job_id=@jobId, @step_name=N'Agworld Integration - Job Activities - Insert',
		@step_id=5,
		@cmdexec_success_code=0,
		@on_success_action=3,
		@on_success_step_id=0,
		@on_fail_action=2,
		@on_fail_step_id=0,
		@retry_attempts=0,
		@retry_interval=0,
		@os_run_priority=0, @subsystem=N'SSIS',
		@command=N'/ISSERVER "\"\SSISDB\Agworld\Agworld_Integration\insertjob_activities.py\"" /SERVER "\"MKC-SSRS\"" /Par "\"$ServerOption::LOGGING_LEVEL(Int16)\"";1 /Par "\"$ServerOption::SYNCHRONIZED(Boolean)\"";True /CALLERINFO SQLAGENT /REPORTING E',
		@database_name=N'master',
		@flags=0,
		@proxy_name=N'mkc.automations'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
/****** Object:  Step [Agworld Integration - Operator Company Licenses - Insert]    Script Date: 4/25/2025 10:28:55 AM ******/
EXEC @ReturnCode = msdb.dbo.sp_add_jobstep @job_id=@jobId, @step_name=N'Agworld Integration - Operator Company Licenses - Insert',
		@step_id=6,
		@cmdexec_success_code=0,
		@on_success_action=3,
		@on_success_step_id=0,
		@on_fail_action=2,
		@on_fail_step_id=0,
		@retry_attempts=0,
		@retry_interval=0,
		@os_run_priority=0, @subsystem=N'SSIS',
		@command=N'/ISSERVER "\"\SSISDB\Agworld\Agworld_Integration\insertoperator_company_licenses.py\"" /SERVER "\"MKC-SSRS\"" /Par "\"$ServerOption::LOGGING_LEVEL(Int16)\"";1 /Par "\"$ServerOption::SYNCHRONIZED(Boolean)\"";True /CALLERINFO SQLAGENT /REPORTING E',
		@database_name=N'master',
		@flags=0,
		@proxy_name=N'mkc.automations'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
EXEC @ReturnCode = msdb.dbo.sp_update_job @job_id = @jobId, @start_step_id = 1
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
EXEC @ReturnCode = msdb.dbo.sp_add_jobschedule @job_id=@jobId, @name=N'Daily 0500',
		@enabled=1,
		@freq_type=4,
		@freq_interval=1,
		@freq_subday_type=1,
		@freq_subday_interval=0,
		@freq_relative_interval=0,
		@freq_recurrence_factor=0,
		@active_start_date=20230101,
		@active_end_date=99991231,
		@active_start_time=50000,
		@active_end_time=235959,
		@schedule_uid=N'46281c3d-a549-456e-9cde-d45cbc711760'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
EXEC @ReturnCode = msdb.dbo.sp_add_jobserver @job_id = @jobId, @server_name = N'(local)'
IF (@@ERROR <> 0 OR @ReturnCode <> 0) GOTO QuitWithRollback
COMMIT TRANSACTION
GOTO EndSave
QuitWithRollback:
    IF (@@TRANCOUNT > 0) ROLLBACK TRANSACTION
EndSave:
GO
