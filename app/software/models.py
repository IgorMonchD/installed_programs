from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class Tag(models.Model):
    name = models.CharField(max_length=3)

    def __str__(self):
        return str(self.name)

class Inspection(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE) 
    sono = models.CharField(max_length=8)
    ip = models.CharField(max_length=14)

    def __str__(self):
        return str(self.sono)

class Origin(models.Model):
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name


class TypicalActivity(models.Model):
    name = models.CharField(max_length=3)
    
    def __str__(self):
        return self.name


class ProgramCategory(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class ProgramClass(models.Model):
    program_category = models.ForeignKey(ProgramCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name


class Directory(models.Model):
    name = models.CharField(max_length=255)  
    origin = models.ForeignKey(Origin, on_delete=models.CASCADE)
    typical_activity = models.ForeignKey(TypicalActivity, on_delete=models.CASCADE)
    program_category = models.ForeignKey(ProgramCategory, on_delete=models.CASCADE, null=True)
    program_class = models.ForeignKey(ProgramClass, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class ProgramData(models.Model):
    productid = models.CharField(max_length=150)
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=150) 
    version = models.CharField(max_length=100) 
    publisher = models.CharField(max_length=100) 
    comments = models.CharField(max_length=255) 
    arpregkey = models.CharField(max_length=100) 
    tmfirstappear = models.DateTimeField()
    bismsi = models.CharField(max_length=255) 
    hostcount = models.IntegerField()
    
class Host(models.Model):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE)
    hostname = models.CharField(max_length=150)

    def __str__(self):
        return str(self.hostname)



class Installation(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    programdata = models.ForeignKey(ProgramData, on_delete=models.CASCADE)
    installdir = models.CharField(max_length=255, null=True) 
    installdate = models.DateTimeField(null=True) 
    

@receiver(post_migrate)
def init_data(sender, **kwargs):

    tag_names = []

    for name in tag_names:
        Tag.objects.get_or_create(name=name)

    origin_names = ['Отечественное', 'Иностранное']

    for name in origin_names:
        Origin.objects.get_or_create(name=name)

    typical_activity = ['Да', 'Нет']

    for name in typical_activity:
        TypicalActivity.objects.get_or_create(name=name)

    program_category = ['1. Системное ПО и средства защиты информации', '2. Офисное и прикладное ПО', '3. Коммуникационное ПО']

    for name in program_category:
        ProgramCategory.objects.get_or_create(name=name)

    class_data = [
        ('1','1.1. Операционные системы общего назначения '),
        ('1','1.2. Средства антивирусной защиты'),
        ('1','1.3. Система виртуализации рабочих мест (VDI)'),
        ('1','1.4. Средства криптографической защиты информации и электронной подписи'),
        ('2','2.1. Редакторы файлов: текстовый, табличный, редактор презентаций (офисные пакеты)'),
        ('2','2.2. Почтовые приложения'),
        ('2','2.3. Справочно-правовая система'),
        ('2','2.4. Системы электронного документооборота (СЭД)'),
        ('2','2.5. Средства просмотра PDF-файлов'),
        ('2','2.6. Интернет-браузеры'),
        ('2','2.7. Средства анализа данных (BI)'),
        ('2','2.8. Системы управления проектами и задачами'),
        ('3','3.1. Средства обмена мгновенными сообщениями (мессенджеры)'),
        ('3','3.2. Средства проведения видеоконференц-связи (ВКС)'),
    ]
    
    for category_name, name in class_data:
        category = ProgramCategory.objects.get(id=category_name)
        ProgramClass.objects.get_or_create(program_category=category, name=name)

    inspection_data = [
    ]

    for tag_name, sono, ip in inspection_data:
        tag = Tag.objects.get(name=tag_name)
        Inspection.objects.get_or_create(tag=tag, sono=sono, ip=ip)
