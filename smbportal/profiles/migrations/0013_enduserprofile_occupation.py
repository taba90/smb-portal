# Generated by Django 2.0.5 on 2018-07-11 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0012_smbuser_accepted_terms_of_service_squashed_0015_auto_20180710_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='enduserprofile',
            name='occupation',
            field=models.CharField(choices=[('insurance_agent', 'insurance agent'), ('trading_agent', 'trading agent'), ('freelancer', 'freelancer'), ('architect', 'architect'), ('craftsman', 'craftsman'), ('artist', 'artist'), ('lawyer', 'lawyer'), ('housewife', 'housewife'), ('accountant', 'accountant'), ('dealer', 'dealer'), ('shop_assistant', 'shop assistant'), ('consultant', 'consultant'), ('public_agency_employee', 'public agency employee'), ('private_sector_employee', 'private sector employee'), ('manager', 'manager'), ('public_agency_manager', 'public agency manager'), ('pharmacist', 'pharmacist'), ('surveyor', 'surveyor'), ('journalist', 'journalist'), ('entrepreneur', 'entrepreneur'), ('engineer', 'engineer'), ('teacher', 'teacher'), ('doctor', 'doctor'), ('unemployed', 'unemployed'), ('notary', 'notary'), ('worker', 'worker'), ('retired', 'retired'), ('politician', 'politician'), ('university_professor', 'university professor'), ('trainee', 'trainee'), ('professional_athlete', 'professional athlete'), ('high_school_student', 'high school student'), ('college_student', 'college student')], default='unemployed', max_length=50, verbose_name='occupation'),
        ),
    ]
