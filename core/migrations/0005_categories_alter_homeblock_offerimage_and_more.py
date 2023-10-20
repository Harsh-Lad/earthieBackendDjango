# Generated by Django 4.2.2 on 2023-06-10 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_homeblock'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoryName', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='homeblock',
            name='offerImage',
            field=models.ImageField(upload_to='homeBlock'),
        ),
        migrations.AlterField(
            model_name='homeslider',
            name='slide',
            field=models.ImageField(upload_to='slider'),
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productName', models.CharField(max_length=255)),
                ('productDesc', models.TextField()),
                ('productPrice', models.IntegerField()),
                ('product_image', models.ImageField(upload_to='products')),
                ('primary', models.ImageField(upload_to='primary')),
                ('secondary', models.ImageField(upload_to='secondry')),
                ('tertiary', models.ImageField(upload_to='tertiary')),
                ('tags', models.TextField(blank=True, null=True)),
                ('is_in_Offer', models.BooleanField(default=False)),
                ('offerPrice', models.IntegerField(blank=True, null=True)),
                ('is_available', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.categories')),
            ],
        ),
    ]