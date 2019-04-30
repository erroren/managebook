from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_list_or_404
from .models import StudentUser, Book, BorrowMessage, Hotpic, Message
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail,send_mass_mail,EmailMultiAlternatives
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
import random, io
from PIL import Image, ImageDraw, ImageFont
# Create your views here.



def index(request):
    imglist = Hotpic.objects.all().order_by('index')
    messages = Message.objects.all()
    return render(request, 'booksys/index.html', {'imglist': imglist, 'messages':messages})


def login(request):
    return render(request, 'booksys/reader_login.html')


def loginhandler(request):
    username = request.POST['username']
    pwd = request.POST['password']
    verify = request.POST['verify']
    print(username, pwd)
    try:
        user = StudentUser.objects.get(username=username)
        if user.is_active == False:
            error = '账户未激活'
        else:
            if verify == request.session['verifycode']:
                if user.password == pwd:
                    context = {'user': user}
                    return render(request, 'booksys/reader.html', context)
                else:
                    error = '密码错误'
            else:
                error = '验证码错误'
    except Exception as e:
        error = '账户不存在'
    context = {'error': error}
    return render(request, 'booksys/reader_login.html', context)


def reader(request, id):
    user = StudentUser.objects.get(id=id)
    return render(request, 'booksys/reader.html', {'user': user})


def register(request):
    return render(request, 'booksys/register.html')


def registerhandler(request):
    username = request.POST['username']
    pwd = request.POST['password']
    pwd2 = request.POST['password2']
    collge = request.POST['college']
    number = request.POST['number']
    email = request.POST['email']
    users = StudentUser.objects.all()
    if pwd != pwd2:
        error = '两次输入密码不一致'
        return render(request, 'booksys/register.html', {'error': error})
    elif username in users:
        error = '用户名已存在'
        return render(request, 'booksys/register.html', {'error': error})
    else:
        try:
            user = StudentUser()
            user.username = username
            user.password = pwd
            user.college = collge
            user.studentnum = number
            user.email = email
            user.is_active = False
            user.save()
            print(user)
            id = StudentUser.objects.get(username=username).id
            print(id)
            serial = Serializer(settings.SECRET_KEY, 300)
            userid = serial.dumps({'userid': id}).decode('utf-8')
            send_mail('激活账户', '<a href="http://127.0.0.1:8000/booksys/active/%s">点击进入激活</a>'%(userid,),
                      settings.DEFAULT_FROM_EMAIL, [email])
            error = '注册成功，请前往邮箱激活'
            return render(request, 'booksys/reader_login.html', {'error': error})
        except Exception as e:
            error = '用户信息不能为空'
            return render(request, 'booksys/register.html', {'error': error})


def query(request, id):
    user = StudentUser.objects.get(id=id)
    return render(request, 'booksys/reader_query.html', {'user': user})


def queryresult(request,id):
    user = StudentUser.objects.get(id=id)
    choice = request.POST['item']
    queryname = request.POST['query']
    if choice == 'name':
        try:
            book = get_list_or_404(Book, bname__contains=queryname)
            return render(request, 'booksys/reader_query.html', {'books': book, 'user': user})
        except Exception as e:
            error = '没有找到您想要的书'
            return render(request, 'booksys/reader_query.html', {'error': error, 'user': user})
    else:
        try:
            book = get_list_or_404(Book, author__contains=queryname)
            return render(request, 'booksys/reader_query.html', {'books': book, 'user': user})
        except Exception as e:
            error = '没有找到您想要的书'
            return render(request, 'booksys/reader_query.html', {'error': error, 'user': user})


def bookinfo(request, bid, uid):
    book = Book.objects.get(id=bid)
    user = StudentUser.objects.get(id=uid)
    try:
        message = BorrowMessage.objects.get(book=book)
        return render(request, 'booksys/reader_book.html', {'book': book, 'reader': message, 'user': user})
    except Exception as e:
        return render(request, 'booksys/reader_book.html', {'book': book, 'user': user})


def borrowinfo(request,bid,uid):
    book = Book.objects.get(id=bid)
    user = StudentUser.objects.get(id=uid)
    message = BorrowMessage.objects.all()
    try:
        reader = BorrowMessage.objects.get(book=book)
        error = '已被借阅'
        return render(request, 'booksys/reader_book.html', {'book':book, 'reader':reader, 'user': user, 'error':error})
    except Exception as e:
        message = BorrowMessage()
        message.book = book
        message.person = user
        message.return_date = datetime.now()+timedelta(days=30)
        message.status = True
        message.save()
        reader = BorrowMessage.objects.get(book=book)
        return render(request, 'booksys/reader_book.html', {'book':book, 'reader':reader, 'user': user})


def queryinfo(request,id):
    user = StudentUser.objects.get(id=id)
    return render(request, 'booksys/reader_info.html', {'user': user})


def updateinfo(request, id):
    user = StudentUser.objects.get(id=id)
    return render(request, 'booksys/reader_modify.html', {'user':user})


def updateinfohandler(request, id):
    user = StudentUser.objects.get(id=id)
    username = request.POST['username']
    password = request.POST['password']
    college = request.POST['college']
    number = request.POST['number']
    email = request.POST['email']
    user.username = username
    if password !='':
        user.password = password
    user.college = college
    user.studentnum = number
    user.email = email
    user.save()
    return redirect(reverse('booksys:queryinfo', args=(id,)))


def history(request, id):
    user = StudentUser.objects.get(id=id)
    message = get_list_or_404(BorrowMessage, person=user)
    return render(request, 'booksys/reader_histroy.html', {'histroys': message, 'user': user})


def upload(request):
    if request.method == "GET":
        return  render(request, 'booksys/reader_upload.html')
    else:
        name = request.POST['name']
        pic = request.FILES['image']
        index = Hotpic.objects.all().count() + 1
        hot = Hotpic()
        hot.name = name
        hot.pic = pic
        hot.index = index
        hot.save()
        imglist = Hotpic.objects.all()
        return render(request, 'booksys/index.html', {'imglist': imglist})


def editor(request):
    if request.method == 'GET':
        return render(request, 'booksys/edit.html')
    else:
        name = request.POST['name']
        textcontent = request.POST['content']
        m1 = Message(mtitle=name, content=textcontent)
        m1.save()
        return redirect(reverse('booksys:index'))


def emailto(request):
    try:
        send_mail("第一封邮件", "This is my first email", settings.DEFAULT_FROM_EMAIL,
                  ['982882262@qq.com'])
        return HttpResponse("发送成功")
    except Exception as e:
        return HttpResponse("发送失败")


def active(request, idstr):
    dser = Serializer(settings.SECRET_KEY, 300)
    try:
        obj = dser.loads(idstr)
        user = StudentUser.objects.get(id=obj['userid'])
        user.is_active = True
        user.save()
        error = '激活成功'
        return render(request, 'booksys/reader_login.html', {'error': error})
    except SignatureExpired as e:
        error = '链接已过期'
        return render(request, 'booksys/reader_login.html', {'error': error})


def ajax(request):
    return render(request, 'booksys/ajax.html')


def ajaxajax(request):
    return HttpResponse("success")


def verify(request):
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100),
               random.randrange(20, 100),
               random.randrange(20, 100))
    width = 100
    heigth = 25
    # 创建画面对象
    im = Image.new('RGB', (width, heigth), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, heigth))
    fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
    draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    # 构造字体对象
    font = ImageFont.truetype('arial.ttf', 23)
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    # 释放画笔
    del draw
    request.session['verifycode'] = rand_str
    f = io.BytesIO()
    im.save(f, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(f.getvalue(), 'image/png')


def exit(request):
    return redirect(reverse('booksys:index'))
