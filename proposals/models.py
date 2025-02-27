from django.db import models
from django.urls import reverse

from django.conf import settings

from django.dispatch import receiver
from django.db.models.signals import(
    post_save,
    post_delete
)

from .compliance_tool import langchain_api#, compliance_tool
from .tasks import langchain_task, compliance_task
from django.db import transaction

import boto3
import os

import requests

# # REMOVE IN PROD
# from dotenv import load_dotenv
# load_dotenv()

session = boto3.Session(
    aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key= os.environ['AWS_SECRET_ACCESS_KEY'],
    )
s3_client = session.client('s3')
s3_resource = session.resource('s3')

DONOR_CHOICES = (
    ('USAID','USAID'),
    ('USDOS', 'USDOS'),
    ('KOICA','KOICA'),
    ('Other','Other'),
)

PRIORITY_CHOICES = (
    ('Low','Low'),
    ('Normal', 'Normal'),
    ('High','High'),
    ('Critical','Critical'),
)

STATUS_CHOICES = (
    ('Pre-Color Review','Pre-Color Review'),
    ('Blue Review','Blue Review'),
    ('Pink Review', 'Pink Review'),
    ('Red Review','Red Review'),
    ('Green Review','Green Review'),
    ('Gold Review','Gold Review'),
    ('White Review','White Review'),
)

COLOR_CHOICES = (
    ('white','white'),
    ('#F8F8F8','#F8F8F8'),
    ('#AEBC37','#AEBC37'),
    ('red','red'),

)

def jsonfield_default_value():  # This is a callable
    items_list = [   
        'Questions Deadline',
        'Questions Submission',
        'Closing Date',
        'Submission Instructions',
        'Proposal Submission',
        'Technical Application',
        'Formatting',
        'Language',
        'Paper',
        'Estimate of Funds',
        '# of Awards',
        'Duration',
        'Substantial Involvement',
        'Post-Award Model',
        'Anticipated Start Date',
        'Authorized Geographic Code',
        'Cost Share',
        'Appication Format',
        'OBJECTIVE 1',
        'IR 1.1.',
        'IR 1.2. ',
        'IR 1.3.',
        'OBJECTIVE 2',
        'IR 2.1.',
        'IR 2.2.',
        'IR 2.3.',
        'OBJECTIVE 3',
        'IR 3.1.',
        'IR 3.2.',
        'IR 3.3.',
        'Cross Cutting Considerations',
        'Management Approach',
        'Staffing and Key Personnel',
        'Resource Management',
        'Risk Management',
        'Cost Application',
        'Cost Application Requirements',
        'Cost Share',
        'Source and Origin',
        'Line Items',
        'Personnel',
        'Fringe Benefits',
        'Non-Employee Labor',
        'Travel',
        'Overseas Allowances',
        'Equipment',
        'Supplies',
        'Staff Training',
        'USAID Branding & Marking',
        'Sub-Awards',
        'Contracts (if any)',
        'Audits',
        'Construction',
        'Other Direct Costs',
        'Indirect Costs',
        'Budgeting for Climate Risk and Environmental Safeguards',
        'Annex 1',
        'Annex 2',
        'Annex 3',
        'Environmental Compliance (Including Climate Risk Management)',
        'Reps and Certs',
    ]
    base_list = []
    for index, i in enumerate(items_list):
        base_list.append({"item": i, "id": index, "data":"", 'pages':""})
    return base_list  # Any serializable Python obj, e.g. `["A", "B"]` or `{"price": 0}`

def template_default_value():
    return [
        {"item": "", "id": 0, "data":"", "page":"", "prompt": ""}
        ]

class Proposal(models.Model):
    #id = pk #by default "primary key"
    title = models.CharField(max_length=200)
    donor = models.CharField(max_length=200, choices=DONOR_CHOICES, null=True)
    description = models.TextField(null=True)
    priority = models.CharField(max_length=200, choices=PRIORITY_CHOICES, default="Normal")
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default="Pre-Color Review")
    nofo = models.FileField(blank=True, null=True, default="")
    assigned = models.CharField(max_length=200, null=True, blank=True, default="")
    compliance_sections = models.JSONField(blank=True, null=True, default=dict)
    proposal_link = models.CharField(max_length=500, null=True, blank=True, default="")
    proposal_id = models.CharField(max_length=500, null=True, blank=True, default="")
    checklist = models.JSONField(default=template_default_value)
    doc_start = models.IntegerField(default=0)
    doc_end = models.IntegerField(default=0)
    pages_ran = models.IntegerField(default=0)
    loading = models.BooleanField(default=False)
    loading_checklist = models.BooleanField(default=False)
    title_count = models.IntegerField(default=0)

    # word_analysis = models.JSONField(blank=True, null=True, default=dict)

    def get_absolute_url(self):
        return reverse("proposals:proposals-detail", kwargs={"pk": self.pk})

class Event(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    title = models.CharField(blank=False, max_length=30)
    start = models.DateField(blank=False)
    end = models.DateField(blank=False)

    def get_absolute_url(self):
        return reverse("proposals:proposals-detail", kwargs={"pk": self.pk})

class ComplianceImages(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    title = models.ImageField(upload_to='.', null=True, blank=True)
    content = models.ImageField(upload_to='.', null=True, blank=True)
    title_text = models.TextField(null=True, blank=True)
    content_text = models.TextField(null=True, blank=True)
    page_number = models.IntegerField(null=True, blank=True)
    flagged = models.CharField(max_length=200, choices=COLOR_CHOICES, default="white")

    def get_absolute_url(self):
        return reverse("proposals:proposals-detail", kwargs={"pk": self.pk})

@receiver(post_save, sender=Proposal)
def user_created_handler(sender, instance, *args, **kwargs):
    if (instance.nofo != '') and (instance.pages_ran == 0):
        if os.environ['TESTING'] != 'True':
            if len(list(instance.complianceimages_set.all())) == 0:
                transaction.on_commit(lambda: compliance_task.delay(str(instance.nofo.file), instance.pk, instance.doc_start, instance.doc_end))
                print(instance.checklist)
                print(instance.checklist[0]['prompt'])
                if len(instance.checklist[0]['prompt']) > 0:
                    print("sending langchain")
                    transaction.on_commit(lambda: langchain_task.delay(str(instance.nofo.file), instance.checklist, instance.pk))
        else:
            print("running")
            if len(list(instance.complianceimages_set.all())) == 0:
                data = {
                    "nofo" : str(instance.nofo.file),
                    "pk": instance.pk,
                    "doc_start": instance.doc_start,
                    "doc_end": instance.doc_end,
                    "media_url": settings.MEDIA_URL,
                    "title_count": instance.title_count,
                    "title": instance.title
                }

                response = requests.post(f'http://pdfmlbalancer-1287380250.us-east-2.elb.amazonaws.com/compliance_tool', json=data)
                print(response)
                print(response.status_code)
                print(response.content)
                #compliance_tool(str(instance.nofo.file), instance.pk, instance.doc_start, instance.doc_end, 0, settings.MEDIA_URL, instance.title_count, instance.title)
                print(instance.checklist)
                print(instance.checklist[0]['prompt'])
                if len(instance.checklist[0]['prompt']) > 0:
                    print("sending langchain")
                    langchain_api(str(instance.nofo.file), instance.checklist, instance.pk)
            

@receiver(post_delete, sender=ComplianceImages)
def remove_file_from_s3(sender, instance, *args, **kwargs):
    print(f"deleting {instance.title.file}")
    s3_client.delete_object(
        Bucket=os.environ['AWS_STORAGE_BUCKET_NAME'],
        Key=f"media/{str(instance.title.file)}"
    )
    s3_client.delete_object(
        Bucket=os.environ['AWS_STORAGE_BUCKET_NAME'],
        Key=f"media/{str(instance.content.file)}"
    )

class Template(models.Model):
    name = models.CharField(max_length=200)
    checklist = models.JSONField(default=template_default_value)

