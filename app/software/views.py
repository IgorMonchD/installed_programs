import matplotlib.pyplot as plt
from collections import Counter
from django.db.models import Count, Sum, Case, Value, F
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.utils.text import slugify
import openpyxl
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from .forms import *
from .models import *
from io import BytesIO
import base64

# @login_required
def create_query(selected_params, sort_by, search_query, order_by):
    query = ProgramData.objects.filter(**selected_params)
    if order_by == 'desc':
        return query.order_by(f'-{sort_by}')
    else:
        return query.order_by(sort_by)

@login_required
def home(request):
    inspections = Inspection.objects.order_by('id')
    tags = Tag.objects.order_by('id')
    search_query = request.GET.get('search_query', '')
    sort_by = request.GET.get('sort_by', 'name')
    order_by = request.GET.get('order_by', 'asc')
    selected_inspection = int(request.GET.get('inspection', '0'))
    selected_tag = int(request.GET.get('inspection_tag','0'))
    exclude_zero = request.GET.get('exclude_zero')
    show_table = request.GET.get('show_table')
 
    if selected_inspection:
        if order_by == 'desc':
            data_in_table = ProgramData.objects.filter(inspection_id=selected_inspection, name__icontains=search_query).order_by(f'-{sort_by}')
            order_by = 'asc'
        else:
            data_in_table = ProgramData.objects.filter(inspection_id=selected_inspection, name__icontains=search_query).order_by(sort_by)
            order_by = 'desc'
    elif selected_tag:
        if order_by == 'desc':
            data_in_table = ProgramData.objects.filter(inspection__tag__id=selected_tag, name__icontains=search_query).order_by(f'-{sort_by}')
            order_by = 'asc'
        else:
            data_in_table = ProgramData.objects.filter(inspection__tag__id=selected_tag, name__icontains=search_query).order_by(sort_by)
            order_by = 'desc'    
    else:
        if order_by == 'desc':
            data_in_table = ProgramData.objects.filter(name__icontains=search_query).order_by(f'-{sort_by}')
            order_by = 'asc'
        else:
            data_in_table = ProgramData.objects.filter(name__icontains=search_query).order_by(sort_by)
            order_by = 'desc'

    if exclude_zero == 'on':
        data_in_table = data_in_table.exclude(hostcount=0)
        
    if 'export' in request.GET:
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=data.xlsx'
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        headers = ['Инспекция', 'Name', 'Версия', 'Издатель', 'Ключ', 'Количество', 'Происхождение', 'Типовое', 'Категория', 'Класс' ]
        sheet.append(headers)
        for data in data_in_table:
            inspection = Inspection.objects.get(id=data.inspection.id).sono
            if data.directory is None:
                directory, origin, typical_activity, program_category, program_class = '', '', '', '', '' # Пустая строка, если directory.id отсутствует
            else: # Проверка наличия directory.id
                directory = Directory.objects.get(id=data.directory.id)
                origin = Origin.objects.get(id=directory.origin.id).name
                typical_activity = TypicalActivity.objects.get(id=directory.typical_activity.id).name
                if typical_activity == 'Нет':
                    program_category = ''
                    program_class = ''
                else:
                    program_category = ProgramCategory.objects.get(id=directory.program_category.id).name
                    program_class = ProgramClass.objects.get(id=directory.program_class.id).name
            row = [inspection, data.name, data.version, data.publisher, data.arpregkey, data.hostcount, origin, typical_activity, program_category, program_class]
            sheet.append(row)
        workbook.save(response)
        return response


    paginator = Paginator(data_in_table, 200)
    page = request.GET.get('page')
    data_on_page = paginator.get_page(page)

    context = {
        'data': data_on_page,
        'sort_by': sort_by,
        'order_by': order_by,
        'items_per_page': 200,
        'current_page': page,
        'inspections': inspections,
        'tags': tags,
        'selected_inspection': selected_inspection,
        'selected_tag': selected_tag,
        'exclude_zero': exclude_zero,
        'show_table': show_table,
    }
    return render(request, 'software/home.html', context)

@login_required
def class_view(request):
    inspections = Inspection.objects.order_by('id')
    tags = Tag.objects.order_by('id')
    origins = Origin.objects.order_by('id')
    typical_activitys = TypicalActivity.objects.order_by('id')
    program_categorys = ProgramCategory.objects.order_by('id')
    program_classs =  ProgramClass.objects.order_by('id')
    
    search_query = request.GET.get('search_query', '')
    sort_by = request.GET.get('sort_by', 'name')
    order_by = request.GET.get('order_by', 'asc')
    selected_inspection = int(request.GET.get('inspection', '0'))
    selected_tag = int(request.GET.get('inspection_tag','0'))
    selected_origin = int(request.GET.get('origin', '0'))
    selected_typical_activity = int(request.GET.get('typical_activity','0'))
    selected_program_category = int(request.GET.get('program_category', '0'))
    selected_program_class = int(request.GET.get('program_class','0'))
    
    selected_params = {
    'inspection_id': selected_inspection,
    'inspection__tag__id': selected_tag,
    'directory__origin__id': selected_origin,
    'directory__typical_activity__id': selected_typical_activity,
    'directory__program_category__id': selected_program_category,
    'directory__program_class__id': selected_program_class,
    }

    # Удаляем параметры, которые не выбраны
    selected_params = {k: v for k, v in selected_params.items() if v}

    if selected_params:
        data_in_table = create_query(selected_params, sort_by, search_query, order_by)
        order_by = 'asc' if order_by == 'desc' else 'desc'
    else:
        data_in_table = ProgramData.objects.filter(name__icontains=search_query).order_by(sort_by)
        order_by = 'asc' if order_by == 'desc' else 'desc'

    data_in_table = data_in_table.exclude(hostcount=0)
        
    if 'export' in request.GET:
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=data.xlsx'
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        headers = ['Инспекция', 'Name', 'Версия', 'Издатель', 'Ключ', 'Количество', 'Происхождение', 'Типовое', 'Категория', 'Класс' ]
        sheet.append(headers)
        for data in data_in_table:
            inspection = Inspection.objects.get(id=data.inspection.id).sono
            if data.directory is None:
                directory, origin, typical_activity, program_category, program_class = '', '', '', '', '' # Пустая строка, если directory.id отсутствует
            else: # Проверка наличия directory.id
                directory = Directory.objects.get(id=data.directory.id)
                origin = Origin.objects.get(id=directory.origin.id).name
                typical_activity = TypicalActivity.objects.get(id=directory.typical_activity.id).name
                if typical_activity == 'Нет':
                    program_category = ''
                    program_class = ''
                else:
                    program_category = ProgramCategory.objects.get(id=directory.program_category.id).name
                    program_class = ProgramClass.objects.get(id=directory.program_class.id).name
            row = [inspection, data.name, data.version, data.publisher, data.arpregkey, data.hostcount, origin, typical_activity, program_category, program_class]
            sheet.append(row)
        workbook.save(response)
        return response


    paginator = Paginator(data_in_table, 200)
    page = request.GET.get('page')
    data_on_page = paginator.get_page(page)

    context = {
        'data': data_on_page,
        'sort_by': sort_by,
        'order_by': order_by,
        'items_per_page': 200,
        'current_page': page,
        'inspections': inspections,
        'tags': tags,
        'origins': origins,
        'typical_activitys': typical_activitys,
        'program_categorys': program_categorys,
        'program_classs': program_classs,
        'selected_inspection': selected_inspection,
        'selected_tag': selected_tag,
        'selected_origin': selected_origin,
        'selected_typical_activity': selected_typical_activity,
        'selected_program_category': selected_program_category,
        'selected_program_class': selected_program_class,
    }
    return render(request, 'software/class.html', context)


@login_required
def stat(request):
    inspections = Inspection.objects.order_by('id')
    tags = Tag.objects.order_by('id')
    selected_inspection = int(request.GET.get('inspection', '0'))
    selected_tag = int(request.GET.get('inspection_tag','0'))
    if selected_inspection:
        total_program = ProgramData.objects.filter(inspection_id=selected_inspection).aggregate(Sum('hostcount'))['hostcount__sum']
    elif selected_tag:
        total_program = ProgramData.objects.filter(inspection__tag__id=selected_tag).aggregate(Sum('hostcount'))['hostcount__sum']
    else:
        total_program = ProgramData.objects.aggregate(Sum('hostcount'))['hostcount__sum']
        
 #--------------- 
    if selected_inspection:
        program_category = ProgramData.objects.filter(inspection_id=selected_inspection, directory__program_category__name__isnull=False).values('directory__program_category__name').annotate(sum=Sum('hostcount')).order_by('directory__program_category__id')
    elif selected_tag:
        program_category = ProgramData.objects.filter(inspection__tag__id=selected_tag, directory__program_category__name__isnull=False).values('directory__program_category__name').annotate(sum=Sum('hostcount')).order_by('directory__program_category__id')
    else:
        program_category = ProgramData.objects.filter(directory__program_category__name__isnull=False).values('directory__program_category__name').annotate(sum=Sum('hostcount')).order_by('directory__program_category__id')

    x = [data['directory__program_category__name'] for data in program_category]     
    y = [data['sum'] for data in program_category]    

    plt.figure(figsize=(7, 2))    
    plt.rcParams.update({'font.size': 9})    
    plt.barh(x[::-1], y[::-1], color=['#FF8146', '#FF465C', '#0074A3'])
    plt.xlabel('Количество')     
    plt.title('Категории программ')   

    total = sum(y)
    percentages = [("%.1f" % (float(y[i]/total)*100)) + "%" for i in range(len(y))]
    for i in range(len(x)):
        plt.text(y[i], len(x)-i-1, percentages[i], ha='left', va='center')

    plt.yticks(rotation='horizontal')  

    buffer = BytesIO()   
    plt.savefig(buffer, format='png', bbox_inches='tight')   
    buffer.seek(0)   
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')    
    image_html_program_category = f'<img src="data:image/png;base64,{image_base64}" alt="График">'

 #--------------- 
    if selected_inspection:
        program_class = ProgramData.objects.filter(inspection_id=selected_inspection, directory__program_class__name__isnull=False).values('directory__program_class__name').annotate(sum=Sum('hostcount')).order_by('directory__program_class__id')
    elif selected_tag:
        program_class = ProgramData.objects.filter(inspection__tag__id=selected_tag, directory__program_class__name__isnull=False).values('directory__program_class__name').annotate(sum=Sum('hostcount')).order_by('directory__program_class__id')
    else:
        program_class = ProgramData.objects.filter(directory__program_class__name__isnull=False).values('directory__program_class__name').annotate(sum=Sum('hostcount')).order_by('directory__program_class__id')

    x = [data['directory__program_class__name'] for data in program_class]
    y = [data['sum'] for data in program_class]

    colors = []
    for val in x[::-1]:
        if str(val).startswith('1'):
          colors.append('#0074A3')  # оранжевый
        elif str(val).startswith('2'):
            colors.append('#FF465C')  # красный
        elif str(val).startswith('3'):
            colors.append('#FF8146')  # синий
    plt.figure(figsize=(11, 4))
    plt.rcParams.update({'font.size': 9})
    plt.barh(x[::-1], y[::-1], color=colors)
    plt.xlabel('Количество')
    plt.title('Классы программ')

    total = sum(y)
    percentages = [("%.1f" % (float(y[i]/total)*100)) + "%" for i in range(len(y))]
    for i in range(len(x)):
        plt.text(y[i], len(x)-i-1, percentages[i], ha='left', va='center')

    plt.yticks(rotation='horizontal')

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    image_html_program_class = f'<img src="data:image/png;base64,{image_base64}" alt="График">'

 #--------------- 
    if selected_inspection:
        typical_activity = ProgramData.objects.filter(inspection_id=selected_inspection, directory__typical_activity__name__isnull=False).values('directory__typical_activity__name').annotate(sum=Sum('hostcount')).order_by()    
    elif selected_tag:
        typical_activity = ProgramData.objects.filter(inspection__tag__id=selected_tag, directory__typical_activity__name__isnull=False).values('directory__typical_activity__name').annotate(sum=Sum('hostcount')).order_by()
    else:
        typical_activity = ProgramData.objects.filter(directory__typical_activity__name__isnull=False).values('directory__typical_activity__name').annotate(sum=Sum('hostcount')).order_by()
    

    x = [data['directory__typical_activity__name'] for data in typical_activity]  
    y = [data['sum'] for data in typical_activity] 

    plt.figure(figsize=(3, 2)) 
    plt.rcParams.update({'font.size': 9}) 
    plt.pie(y, labels=x, colors=['#0074A3', '#FF465C'], autopct='%1.1f%%')
    plt.title('ПО типовой деятельности')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '') 
    image_html_typical_activity = f'<img src="data:image/png;base64,{image_base64}" alt="График">'

#---------------
    if selected_inspection:
        origin_data = ProgramData.objects.filter(inspection_id=selected_inspection, directory__origin__name__isnull=False).values('directory__origin__name').annotate(sum=Sum('hostcount')).order_by()
    elif selected_tag:
        origin_data = ProgramData.objects.filter(inspection__tag__id=selected_tag, directory__origin__name__isnull=False).values('directory__origin__name').annotate(sum=Sum('hostcount')).order_by()
    else:
        origin_data = ProgramData.objects.filter(directory__origin__name__isnull=False).values('directory__origin__name').annotate(sum=Sum('hostcount')).order_by()
  
    x = [data['directory__origin__name'] for data in origin_data] 
    y = [data['sum'] for data in origin_data]

    plt.figure(figsize=(3, 2))
    plt.rcParams.update({'font.size': 9}) 
    plt.pie(y, labels=x, colors=['#0074A3', '#FF465C'], autopct='%1.1f%%')
    plt.title('Происхождение') 

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    image_html = f'<img src="data:image/png;base64,{image_base64}" alt="График">'

    context = {
        'total_program': total_program,
        'image_html_typical_activity': image_html_typical_activity,
        'image_html': image_html,
        'inspections': inspections,
        'tags': tags,
        'origin_data': origin_data,
        'image_html_program_category': image_html_program_category,
        'image_html_program_class': image_html_program_class,
        'typical_activity': typical_activity,
        'program_category': program_category,
        'program_class': program_class,
        'selected_inspection': selected_inspection,
        'selected_tag': selected_tag,

    }
    return render(request, 'software/stat.html', context)


def user_login(request):
    result = '' 
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')
                else:
                    result = 'Отключенная учетная запись'
            else:
                result = 'Не верные данные'
    else:
        form = LoginForm()
    return render(request, 'software/login.html', {'form': form,'result': result })

def logout_view(request):
    logout(request)
    return redirect('login')
