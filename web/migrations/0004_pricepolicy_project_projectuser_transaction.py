# Generated by Django 3.2.9 on 2022-02-11 09:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_userinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='PricePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.SmallIntegerField(choices=[(1, '免费版'), (2, '收费版'), (3, '其他')], default=2, verbose_name='收费类型')),
                ('title', models.CharField(max_length=32, verbose_name='标题')),
                ('price', models.PositiveIntegerField(verbose_name='价格')),
                ('project_num', models.PositiveIntegerField(verbose_name='项目数')),
                ('project_member', models.PositiveIntegerField(verbose_name='项目成员数')),
                ('project_space', models.PositiveIntegerField(verbose_name='单项目空间')),
                ('project_file_size', models.PositiveIntegerField(verbose_name='单文件大小')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='项目名')),
                ('color', models.SmallIntegerField(choices=[(1, '#56b8eb'), (2, '#f28033'), (3, '#ebc656'), (4, '#a2d148'), (5, '#20bfa4'), (6, '#7461c2'), (7, '#20bfa3')], default=1, verbose_name='颜色')),
                ('desc', models.CharField(blank=True, max_length=255, null=True, verbose_name='项目描述')),
                ('user_space', models.IntegerField(default=0, verbose_name='项目已使用空间')),
                ('star', models.BooleanField(default=False, verbose_name='星标')),
                ('join_count', models.SmallIntegerField(default=1, verbose_name='参与人数')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.userinfo', verbose_name='创建者')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(choices=[(1, '未支付'), (2, '已支付')], verbose_name='状态')),
                ('order', models.CharField(max_length=64, unique=True, verbose_name='订单号')),
                ('count', models.IntegerField(help_text='0表示无限期', verbose_name='数量（年）')),
                ('price', models.IntegerField(verbose_name='实际支付价格')),
                ('start_datetime', models.DateTimeField(blank=True, null=True, verbose_name='开始时间')),
                ('end_datetime', models.DateTimeField(blank=True, null=True, verbose_name='结束时间')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('price_policy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.pricepolicy', verbose_name='价格策略')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.userinfo', verbose_name='用户')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('star', models.BooleanField(default=False, verbose_name='星标')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.project', verbose_name='项目')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.userinfo', verbose_name='参与者')),
            ],
        ),
    ]
