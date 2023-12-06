from django.db import models

# Create your models here.
class admin_tb(models.Model):
	email=models.CharField(max_length=100,default='')
	password=models.CharField(max_length=100,default='')
	pin=models.CharField(max_length=100,default='',null=True)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')

class client_tb(models.Model):
	client_id=models.CharField(max_length=100,default='')
	name=models.CharField(max_length=100,default='')
	email=models.CharField(max_length=100,default='')
	phone=models.CharField(max_length=100,default='')
	business=models.CharField(max_length=100,default='',null=True)
	logo=models.ImageField(upload_to='image',null=True)
	password=models.CharField(max_length=100,default='')
	status=models.CharField(max_length=100,default='Pending')
	pin=models.CharField(max_length=100,default='',null=True)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')


class branch_tb(models.Model):
	name=models.CharField(max_length=100,default='')
	email=models.CharField(max_length=100,default='')
	client_id=models.ForeignKey(client_tb,on_delete=models.CASCADE,default='')
	layout=models.ImageField(upload_to='image',null=True)
	document=models.ImageField(upload_to='image',null=True)
	cc=models.TextField(default='',null=True)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')


class shift_tb(models.Model):
	from_time=models.CharField(max_length=100,default='')
	to_time=models.CharField(max_length=100,default='')
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')


class zone_tb(models.Model):
	zone=models.CharField(max_length=100,default='')
	branch_id=models.ForeignKey(branch_tb,on_delete=models.CASCADE,default='')
	client_id=models.ForeignKey(client_tb,on_delete=models.CASCADE,default='')
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')


class window_zone_tb(models.Model):
	zone=models.CharField(max_length=100,default='')
	branch_id=models.ForeignKey(branch_tb,on_delete=models.CASCADE,default='')
	client_id=models.ForeignKey(client_tb,on_delete=models.CASCADE,default='')
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')



class team_leader_tb(models.Model):
	name=models.CharField(max_length=100,default='')
	email=models.CharField(max_length=100,default='')
	phone=models.CharField(max_length=100,default='')
	password=models.CharField(max_length=100,default='')
	pin=models.CharField(max_length=100,default='',null=True)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')



class agent_tb(models.Model):
	name=models.CharField(max_length=100,default='')
	email=models.CharField(max_length=100,default='')
	phone=models.CharField(max_length=100,default='')
	password=models.CharField(max_length=100,default='')
	team_leader_id=models.ForeignKey(team_leader_tb,on_delete=models.CASCADE,default='')
	total_hrs=models.CharField(max_length=100,default='')
	required_hrs=models.CharField(max_length=100,default='')
	max_break_time=models.CharField(max_length=100,default='')
	pin=models.CharField(max_length=100,default='',null=True)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')



class job_tb(models.Model):
	job_id=models.CharField(max_length=100,default='')
	title=models.CharField(max_length=100,default='')
	description=models.TextField(default='')
	team_leader_id=models.ForeignKey(team_leader_tb,on_delete=models.CASCADE,default='')
	start_date=models.DateTimeField(max_length=100,default='')
	end_date=models.DateTimeField(max_length=100,default='')
	actual_start_date=models.CharField(max_length=100,default='',null=True)
	actual_end_date=models.CharField(max_length=100,default='',null=True)
	client_id=models.ForeignKey(client_tb,on_delete=models.CASCADE,default='')
	status=models.CharField(max_length=100,default='Pending')
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')



class staff_tb(models.Model):
	name=models.CharField(max_length=100,default='')
	email=models.CharField(max_length=100,default='')
	phone=models.CharField(max_length=100,default='')
	designation=models.CharField(max_length=100,default='')
	shift_id=models.ForeignKey(shift_tb,on_delete=models.CASCADE,default='')
	total_hrs=models.CharField(max_length=100,default='')
	required_hrs=models.CharField(max_length=100,default='')
	max_break_time=models.CharField(max_length=100,default='')
	client_id=models.ForeignKey(client_tb,on_delete=models.CASCADE,default='')
	branch_id=models.ForeignKey(branch_tb,on_delete=models.CASCADE,default='')
	status=models.CharField(max_length=100,default='',null=True)
	image=models.ImageField(upload_to='image',null=True)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')



class task_tb(models.Model):
	task_id=models.CharField(max_length=100,default='')
	title=models.CharField(max_length=100,default='')
	description=models.TextField(default='')
	job_id=models.ForeignKey(job_tb,on_delete=models.CASCADE,default='')
	start_date=models.DateTimeField(max_length=100,default='')
	end_date=models.DateTimeField(max_length=100,default='')
	start_time=models.CharField(max_length=100,default='')
	end_time=models.CharField(max_length=100,default='')
	required_hrs=models.CharField(max_length=100,default='')
	agent_id=models.ForeignKey(agent_tb,on_delete=models.CASCADE,default='',null=True)
	team_leader_id=models.ForeignKey(team_leader_tb,on_delete=models.CASCADE,default='',null=True)
	status=models.CharField(max_length=100,default='Pending')
	submit_tl=models.BooleanField(max_length=100,default=0)
	client_id=models.ForeignKey(client_tb,on_delete=models.CASCADE,default='')
	have_request=models.BooleanField(max_length=100,default=0)
	request_status=models.CharField(max_length=100,default='',null=True)
	have_delay_request=models.BooleanField(max_length=100,default=0)
	delay_request_status=models.CharField(max_length=100,default='',null=True)
	branch_id=models.ForeignKey(branch_tb,on_delete=models.CASCADE,default='')
	approved_time=models.DateTimeField(null=True)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')


class time_period_tb(models.Model):	
	period=models.CharField(max_length=100,default='')
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')


class customer_tb(models.Model):
	task_id=models.ForeignKey(task_tb,on_delete=models.CASCADE,default='')
	agent_id=models.ForeignKey(agent_tb,on_delete=models.CASCADE,default='')
	date=models.DateTimeField(max_length=100,default='')
	opening_time=models.CharField(max_length=100,default='')
	closing_time=models.CharField(max_length=100,default='')
	customer_id=models.IntegerField(default='')
	customer_entry_time=models.CharField(max_length=100,default='')
	customer_exit_time=models.CharField(max_length=100,default='')
	dwell_time=models.CharField(max_length=100,default='')
	single=models.BooleanField(max_length=100,default=0)
	group=models.BooleanField(max_length=100,default=0)
	male=models.BooleanField(max_length=100,default=0)
	female=models.BooleanField(max_length=100,default=0)
	zone_ids=models.CharField(max_length=100,default='')
	window_zone_ids=models.CharField(max_length=100,default='')
	staff_ids=models.CharField(max_length=100,default='')
	repeat_customer=models.BooleanField(max_length=100,default=0)
	repeat_customer_id=models.IntegerField(default=0,null=True)
	repeat_customer_visit_date=models.DateTimeField(max_length=100,null=True)
	tray=models.BooleanField(max_length=100,default=0)
	refreshment=models.BooleanField(max_length=100,default=0)
	gloves=models.BooleanField(max_length=100,default=0)
	backup_stock=models.BooleanField(max_length=100,default=0)
	business_card=models.BooleanField(max_length=100,default=0)
	body_language=models.BooleanField(max_length=100,default=0)
	full_uniform=models.BooleanField(max_length=100,default=0)
	conversion_status=models.BooleanField(max_length=100,default=0)
	conversion_percentage=models.IntegerField(default='',null=True)
	converted_count=models.IntegerField(default=0,null=True)
	conversion_to=models.ForeignKey(staff_tb,on_delete=models.CASCADE,default='',null=True)
	invoice_time=models.CharField(max_length=100,default='')
	reason_for_no_conversion=models.TextField(default='',null=True)
	remark=models.TextField(default='')
	submit_tl=models.BooleanField(max_length=100,default=0)
	job_id=models.ForeignKey(job_tb,on_delete=models.CASCADE,default='')
	branch_id=models.ForeignKey(branch_tb,on_delete=models.CASCADE,default='')
	no_of_male=models.IntegerField(default=0,null=True)
	no_of_female=models.IntegerField(default=0,null=True)
	time_period_id=models.ForeignKey(time_period_tb,on_delete=models.CASCADE,default='')
	client_id=models.ForeignKey(client_tb,on_delete=models.CASCADE,default='')
	team_leader_id=models.ForeignKey(team_leader_tb,on_delete=models.CASCADE,default='')
	status=models.CharField(max_length=100,default='Pending')
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')


class staff_attendance_tb(models.Model):
	staff_id=models.ForeignKey(staff_tb,on_delete=models.CASCADE,default='')
	date=models.DateTimeField(max_length=100,default='')
	out_date=models.CharField(max_length=100,default='',null=True)
	in_time=models.CharField(max_length=100,default='')
	out_time=models.CharField(max_length=100,default='')
	official_break=models.CharField(max_length=100,default='')
	un_official_break=models.CharField(max_length=100,default='')
	break_hours=models.CharField(max_length=100,default='')
	work_hours=models.CharField(max_length=100,default='')
	over_time=models.CharField(max_length=100,default='')
	under_time=models.CharField(max_length=100,default='')
	epoch_work_hours=models.CharField(max_length=100,default='')
	epoch_org_work_hours=models.CharField(max_length=100,default='')
	epoch_over_time=models.CharField(max_length=100,default='')
	epoch_under_time=models.CharField(max_length=100,default='')
	client_id=models.ForeignKey(client_tb,on_delete=models.CASCADE,default='')
	agent_id=models.ForeignKey(agent_tb,on_delete=models.CASCADE,default='',null=True)
	submit=models.BooleanField(max_length=100,default=0)
	approve=models.BooleanField(max_length=100,default=0)
	approved_time=models.DateTimeField(null=True)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')



class staff_attendance_break_tb(models.Model):
	attendance_id=models.ForeignKey(staff_attendance_tb,on_delete=models.CASCADE,default='')
	out_date=models.CharField(max_length=100,default='',null=True)
	out_time=models.CharField(max_length=100,default='',null=True)
	in_date=models.CharField(max_length=100,default='',null=True)
	in_time=models.CharField(max_length=100,default='',null=True)
	break_type=models.CharField(max_length=100,default='',null=True)
	break_diff=models.CharField(max_length=100,default='',null=True)
	remark=models.TextField(default='',null=True)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')



class task_request_tb(models.Model):
	task_id=models.ForeignKey(task_tb,on_delete=models.CASCADE,default='')
	agent_id=models.ForeignKey(agent_tb,on_delete=models.CASCADE,default='')
	team_leader_id=models.ForeignKey(team_leader_tb,on_delete=models.CASCADE,default='')
	remark=models.TextField(default='')
	status=models.BooleanField(max_length=100,default=0)
	status_remark=models.TextField(default='',null=True)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')



class complaint_ticket_tb(models.Model):
	team_leader_id=models.ForeignKey(team_leader_tb,on_delete=models.CASCADE,default='')
	remark=models.TextField(default='')
	client_id=models.ForeignKey(client_tb,on_delete=models.CASCADE,default='')
	status=models.CharField(max_length=100,default='Pending')
	task_id=models.ForeignKey(task_tb,on_delete=models.CASCADE,default='',null=True)
	agent_id=models.ForeignKey(agent_tb,on_delete=models.CASCADE,default='',null=True)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')


class delay_task_request_tb(models.Model):
	task_id=models.ForeignKey(task_tb,on_delete=models.CASCADE,default='')
	agent_id=models.ForeignKey(agent_tb,on_delete=models.CASCADE,default='')
	team_leader_id=models.ForeignKey(team_leader_tb,on_delete=models.CASCADE,default='')
	remark=models.TextField(default='')
	status=models.BooleanField(max_length=100,default=0)
	actual_end_date=models.CharField(max_length=100,default='')
	new_end_date=models.CharField(max_length=100,default='',null=True)
	client_id=models.ForeignKey(client_tb,on_delete=models.CASCADE,default='')
	status_changed_by=models.CharField(max_length=100,default='',null=True)
	status_remark=models.TextField(default='',null=True)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')


class agent_checkin_checkout_tb(models.Model):
	date=models.DateTimeField(max_length=100,default='')
	time=models.CharField(max_length=100,default='')
	agent_id=models.ForeignKey(agent_tb,on_delete=models.CASCADE,default='')
	status=models.CharField(max_length=100,default='')
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')



class message_tb(models.Model):
	date=models.DateTimeField(max_length=100,default='')
	time=models.CharField(max_length=100,default='')
	admin_id=models.ForeignKey(admin_tb,on_delete=models.CASCADE,default='',null=True)
	agent_id=models.ForeignKey(agent_tb,on_delete=models.CASCADE,default='',null=True)
	team_leader_id=models.ForeignKey(team_leader_tb,on_delete=models.CASCADE,default='',null=True)
	client_id=models.ForeignKey(client_tb,on_delete=models.CASCADE,default='',null=True)
	message=models.TextField(default='')
	status=models.CharField(max_length=100,default='')
	sender=models.CharField(max_length=100,default='')
	receiver=models.CharField(max_length=100,default='')
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')



class notification_tb(models.Model):
	admin_id=models.ForeignKey(admin_tb,on_delete=models.CASCADE,default='',null=True)
	agent_id=models.ForeignKey(agent_tb,on_delete=models.CASCADE,default='',null=True)
	team_leader_id=models.ForeignKey(team_leader_tb,on_delete=models.CASCADE,default='',null=True)
	client_id=models.ForeignKey(client_tb,on_delete=models.CASCADE,default='',null=True)
	message=models.TextField(default='')
	status=models.CharField(max_length=100,default='',null=True)
	admin_seen=models.BooleanField(max_length=100,default=0)
	agent_seen=models.BooleanField(max_length=100,default=0)
	team_leader_seen=models.BooleanField(max_length=100,default=0)
	client_seen=models.BooleanField(max_length=100,default=0)
	created_at=models.DateTimeField(max_length=100,default='')
	updated_at=models.DateTimeField(max_length=100,default='')