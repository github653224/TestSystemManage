from django.db import models
import hashlib


def md5_set(password):
    m = hashlib.md5()
    m.update(password.encode("utf8"))
    return m.hexdigest()


# Create your models here.
class ParentCateName(models.Model):
    part = models.CharField(max_length=50, null=False, help_text='系统名')

    class Meta:
        db_table = "ParentCateName"
        managed = True

    def __str__(self):
        return self.part


class CateFolder(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    parent = models.IntegerField(verbose_name='所属系统名称', blank=False, help_text='所属系统名称')
    folder_name = models.CharField(max_length=50, blank=False, verbose_name='文件夹名称', help_text='文件夹名称')

    class Meta:
        db_table = "CateFolder"
        managed = True

    def __str__(self):
        return ParentCateName.objects.get(id=self.parent).__str__()


class TestCase(models.Model):
    level_choice = ((1, 'Level 1'),
                    (2, 'Level 2'),
                    (3, 'Level 3'),
                    (4, 'Level 4')
                    )
    id = models.IntegerField(primary_key=True,auto_created=True)
    create_worker = models.CharField(max_length=255, blank=True, null=True, verbose_name='创建人',help_text='创建人')
    create_time = models.DateTimeField(verbose_name='创建时间' ,help_text='创建时间')
    case_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='用例名称', help_text='用例名称')
    case_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="用例编号" , help_text="用例编号")
    case_level = models.IntegerField(default=3, choices=level_choice, help_text='用例等级', verbose_name='用例等级')
    case_modify_worker = models.CharField(max_length=255, verbose_name='修改人',blank=True, help_text='修改人')
    case_modify_time = models.DateTimeField(auto_now=True, verbose_name='用例修改时间', help_text='用例修改时间')
    case_belongs = models.IntegerField(verbose_name='用例所属文件夹', null=True, blank=True, help_text='用例所属文件夹')
    case_pre = models.CharField(max_length=255, blank=True, null=True, verbose_name='预置步骤',help_text='预置步骤')
    case_process = models.CharField(max_length=255, blank=True, null=True, verbose_name="用例过程", help_text="用例过程")
    case_expect = models.CharField(max_length=255, blank=True, null=True, verbose_name='预期结果', help_text='预期结果')

    class Meta:
        managed = True
        db_table = 'TestCase'

    def __str__(self):
        return self.case_number


class TestCaseResult(models.Model):
    id = models.IntegerField(primary_key=True)
    create_worker = models.CharField(max_length=30, blank=True, null=True, verbose_name='创建人',help_text='创建人')
    create_time = models.DateTimeField(blank=True, null=True, verbose_name='创建时间', help_text='创建时间')
    ending_worker = models.CharField(max_length=30, blank=True, null=True, verbose_name='结束人', help_text='结束人')
    ending_time = models.DateTimeField(blank=True, null=True, verbose_name='结束时间', help_text='结束时间')
    logs = models.TextField(blank=True, null=True, verbose_name='执行日志', help_text='执行日志')
    result = models.CharField(max_length=30, blank=True, null=True, verbose_name='执行结果', help_text='执行结果')
    case_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='用例名', help_text='用例名')
    case_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='用例编号', help_text='用例编号')
    marker = models.CharField(max_length=255, blank=True, null=True, verbose_name='关键字' , help_text='关键字')
    caselevel = models.IntegerField(blank=True, null=True, verbose_name='用力等级', help_text='用力等级')
    imgurl = models.CharField(max_length=255, blank=True, null=True, verbose_name='图片url(UI失败时自动截图)', help_text='图片url(UI失败时自动截图)')
    taskname = models.CharField(max_length=255, blank=True, null=True, verbose_name='任务名', help_text='任务名')
    request_time = models.CharField(max_length=10, blank=True, null=True ,verbose_name='请求时间(API用例)', help_text='请求时间(API用例)')

    class Meta:
        managed = True
        db_table = 'TestCaseResult'


class TestTask(models.Model):
    id = models.IntegerField(primary_key=True)
    create_worker = models.CharField(max_length=30, blank=True, null=True, verbose_name='创建人', help_text='创建人')
    create_time = models.DateTimeField(blank=True, null=True, verbose_name='创建时间', help_text='创建时间')
    taskname = models.CharField(max_length=255, blank=True, null=True, verbose_name='任务名', help_text='任务名')
    run_time = models.CharField(max_length=255, blank=True, null=True, help_text='运行开始时间', verbose_name='运行开始时间')
    contain_args = models.CharField(max_length=255, blank=True, null=True, verbose_name='包含参数', help_text='包含参数')
    passrate = models.CharField(max_length=30, blank=True, null=True, verbose_name='通过率', help_text='通过率')

    class Meta:
        managed = True
        db_table = 'TestTask'


class TeskDetail(models.Model):
    taskid = models.IntegerField(verbose_name='所属任务id', blank=False, null=False, help_text='所属任务id')
    caseid = models.IntegerField(verbose_name='包含用例id',blank=False, null=False, help_text='包含用例id')

    class Meta:
        managed = True
        db_table = 'TeskDetail'


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=32, unique=True, verbose_name='用户名', help_text='用户名')
    password = models.CharField(max_length=256, verbose_name='密码',help_text='密码')
    mobile = models.CharField(max_length=11, blank=True, unique=True, verbose_name='手机号码', help_text='手机号码')
    email = models.EmailField(max_length=64, blank=True, unique=True, verbose_name='邮箱', help_text='邮箱')

    def set_password(self, password):
        self.password = md5_set(password)

    def check_password(self, password):
        return self.password == md5_set(password)

    def __str__(self):
        return self.username
