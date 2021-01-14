# 1 简介

1、仅包含后台部分，前端页面因为各自审美不一样，因此需要自行适配，本项目只提供了后台API部分

2、使用Django，认证采用自定义的认证方式，通过COOKIE中的jwt_token和username进行认证，有能力可以自行替换

3、部分接口跟Model关联紧密，直接采用的DRF ModelViewSet

4、除/apis/uploadFile/ 接口数据格式为application/x-www-form-urlencoded，其余均为application/json

5、部分接口设置了登录验证装饰器,检测方式为获取COOKIES中的username和token，与redis中数据比对，满足条件则可以请求，如果不想使用可以去掉，或者修改为其他方式

6、水平有限，实现不是很理想的地方请轻喷

# 2 使用方式

## 2.1 安装依赖:

```bash
pip install -r requirements.txt
```

## 2.2 设置数据库

Setting.py 中database配置为自己的ip,port 等，或者改为使用oracle等数据库均可(需要自行安装其他数据库依赖)

并确认指定的数据库已经创建，同时还需要修改redis的配置

## 2.3 迁移数据库

```bash
python manage.py makemigrations

python manage.py migrate
```

## 2.4 static目录

如果直接部署至服务器，需要将djangorestframework 包下的static目录拷贝至服务器，同时服务器nginx.conf增加指向该文件夹的配置

```nginx
location /static/ {
            alias /static/;
            autoindex on;
        }
location /apis/ {
            uwsgi_pass 127.0.0.1:8000;
            include uwsgi_params;
   			}
location /docs/ {
            uwsgi_pass 127.0.0.1:8000;
            include uwsgi_params;
        }
```

## 2.5 uwsgi配置(参考)

假设你已经克隆了本项目至/，即 /TestCenter

### 1、 /TestCenter/uwsgi.ini

```basic
[uwsgi]
chdir = /TestCenter/
module=TestCenter.wsgi:application
socket=127.0.0.1:8000
http = 127.0.0.1:8001
master = true
processes = 4
threads=2
vacuum = true
pidfile = uwsgi.pid
daemonize=uwsgi.log
max-requests=2000
```

### 2 、uwsgi操作

```bash
# uwsgi使用ini配置
uwsgi --ini uwsgi.ini  
# uwsgi重新加载
uwsgi --reload uwsgi.pid
## uwsgi停止
uwsgi --stop uswgi.pid
```



# 3 路径

API部分入口为/apis/, 文档接口采用的coreapi,路径为/docs/

### 3.1 用例管理

#### 3.1.1 路径

##### /apis/testcase/

```python
"""
GET-->list: 返回所有测试用例详情
POST-->create: 创建用例
"""
```

##### /apis/testcase/id/  

```python

"""
id 为integer
GET-->retrieve: 返回当前ID测试用例的详情

PUT-->update: 更改当前用例

DELETE-->destroy: 删除当前用例
"""
```

##### /apis/caseresult/

```python
"""
GET -->list: 返回所有测试用例自动化执行结果(不包含日志)
POST -->create: 创建用例结果,可搭配AutoMationTest使用(不包含日志)
"""
```

##### /apis/caselog/

```python
"""
POST -->create:创建用例结果,可搭配AutoMationTest使用(包含日志)
"""
```

##### /apis/caselog/id/

```python
"""
GET -->retrieve:获取完整用例执行结果(包含日志)
"""
```

##### /apis/testtask/

```python
"""
GET --> list: 返回所有测试任务详情
POST -->create: 创建任务
"""
```

##### /apis/testtask/id/

```python
"""
GET --> retrieve: 获取当前id任务详情
PATCH --> update: 更新当前id任务
DELETE --> destroy: 删除当前任务
"""
```

##### /apis/taskimgs/

```python
"""
GET --> query_param: taskname:任务名
				return: 根据当前任务名或者执行结果，返回excel表格
"""
```

##### /apis/token/

```python
"""
POST -->body: application/json  {"username": "xxx","password": "xxx"}
				return: application/json  {"username": "xxx","token": "xxx"}

PUT --> body: application/json  {"username": "xxx","password": "xxx", "email": "xxx", "mobile": "xxx"}
				return: application/json  {"username": "xxx","token": "xxx"}

DELETE --> body:None  删除redis中的token
					 return: None
"""
```

##### /apis/getSystem/

```python
"""
GET --> 返回 所有系统
"""
```

##### /apis/getFolder/

```python
"""
GET --> query_param: system(系统id)
				return: 该system id下的所有文件夹信息
"""
```

##### /apis/getCase/

```python
"""
GET --> query_param: folder(文件夹id)
				return: 该文件夹下所有用例
"""
```

##### /apis/getTaskDetailCase/

```python
"""
GET --> query_param: taskid(任务ID)
				 return: 返回该任务包含所有用例ID
"""
```

##### /apis/querycase/

```python
"""
GET: query_param:     system folder case_name 共三个，可以单个也可以多个一起查询，返回符合条件的用例详情
"""
```

##### /apis/uploadFile/

```python
"""
POST --> body:  application/x-www-form-urlencoded  key为image,value为文件，只能上传图片
				 return: 存储的url， 需要自行修改nginx 指向保存目录
"""
```

3 相关介绍

您可以查看我的另一篇 测试框架的项目: 

[AutoMationTest]: https://github.com/oslo254804746/AutoMationTest	"AutoMationTest"





