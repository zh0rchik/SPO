import os
import time
import xml.etree.ElementTree as ET
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from .models import MyObject
import xmltodict
import json
from django import forms

UPLOAD_FOLDER = 'uploads'

import xml.etree.ElementTree as ET

def parse_xml(file_contents):
    try:
        root = ET.fromstring(file_contents)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        raise

    objects = []

    # First pass: collect all objects
    for obj in root.findall('.//mxCell'):
        style = obj.get('style')
        parent = obj.get('parent')
        obj_data = {
            'id': obj.get('id'),
            'value': obj.get('value'),
            'source': obj.get('source'),
            'target': obj.get('target'),
            'type': 'unknown',  # Default type
            'data_type': 'unknown',  # Default data type
            'parent': parent,
            'style': style,
        }

        # Determine the data type based on the style or other attributes
        if style is None:
            continue
        if style.startswith("rounded=1") and obj_data['value'] != '' and parent == "1":
            obj_data['data_type'] = 'process'
        elif style.startswith("rounded=0"):
            obj_data['data_type'] = 'external_entity'
        elif style.startswith("rounded=1") and parent != "1":
            obj_data['data_type'] = 'data_store'
        elif style.startswith("edgeStyle=orthogonalEdgeStyle"):
            obj_data['data_type'] = 'data_flow'
        elif style.startswith("html=1"):
            obj_data['data_type'] = 'index_data_store'

        if obj_data['value'] or obj_data['source'] or obj_data['target']:
            objects.append(obj_data)

    for obj in objects:
        print(obj)
    return objects

def create_table(objects, filename):
    for obj in objects:
        unique_id = f"{filename}_{obj['id']}"
        new_object = MyObject(
            id=unique_id,
            value=obj['value'],
            source=f"{filename}_{obj['source']}" if obj['source'] else None,
            target=f"{filename}_{obj['target']}" if obj['target'] else None,
            description='',
            type='relationship' if obj['source'] and obj['target'] else 'object',
            data_type=obj['data_type'],
            parent=obj['parent'],
            uploaded_file=filename
        )
        new_object.save()

def home_page(request):
    error_message = None
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            fs = FileSystemStorage(location=UPLOAD_FOLDER)
            filename = fs.save(uploaded_file.name, uploaded_file)

            # Открываем файл снова для чтения содержимого
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_contents = file.read()
                if not file_contents.strip():
                    error_message = 'Uploaded file is empty'
                else:
                    try:
                        objects = parse_xml(file_contents)
                        str_filename = filename.split('.')[0]
                        create_table(objects, filename=str_filename)
                    except ET.ParseError:
                        error_message = 'Error parsing the uploaded XML file'

            if not error_message:
                return redirect(reverse('home_page'))

    return render(request, 'index.html', {'error': error_message})

def data_base_view(request):
    uploaded_files = MyObject.objects.values_list('uploaded_file', flat=True).distinct()
    return render(request, 'database_export.html', {'uploaded_files': uploaded_files})

def delete_file(request, uploaded_file):
    if request.method == 'POST':
        MyObject.objects.filter(uploaded_file=uploaded_file).delete()
        return redirect(reverse('data_base_view'))

def get_table_data(table_name):
    return MyObject.objects.filter(uploaded_file=table_name)

def table_view(request, table_name):
    file_path = os.path.join(UPLOAD_FOLDER, table_name + ".xml")

    # Получение данных таблицы
    data = get_table_data(table_name)
    diagramm = []
    for row in data:
        if row.type == 'relationship':
            rel = []
            start_point = row.source
            end_point = row.target
            val = row.value

            for item in data:
                if item.id == start_point:
                    rel.append(item.value)
            rel.append(val)
            for item in data:
                if item.id == end_point:
                    rel.append(item.value)
            rel.append(start_point)
            rel.append(end_point)
            diagramm.append(rel)

    # Конвертация XML в JSON для диаграммы
    with open(file_path, 'r', encoding='utf-8') as file:
        xml_str = file.read()
    xml_dict = xmltodict.parse(xml_str)
    json_data = json.dumps(xml_dict)

    return render(request, 'table_view.html', {
        'data': data,
        'table_name': table_name,
        'diagramm': diagramm,
        'diagram_json': json_data
    })

def termins_view(request, table_name):
    data = get_table_data(table_name)
    return render(request, 'termins.html', {'data': data, 'table_name': table_name})

def edit_values(request, table_name):
    data = get_table_data(table_name)
    return render(request, 'edit_values.html', {'table_data': data, 'table_name': table_name})

def update_values(request, table_name):
    if request.method == 'POST':
        table_data = get_table_data(table_name)
        for key, value in request.POST.items():
            if key.startswith('value_'):
                row_id = key[6:]
                obj = table_data.get(id=row_id)
                obj.value = value
                obj.save()
        return redirect(reverse('table_view', args=[table_name]))


def edit_desc(request, table_name):
    data = get_table_data(table_name)
    return render(request, 'edit_desc.html', {'table_data': data, 'table_name': table_name})

def update_description(request, table_name):
    if request.method == 'POST':
        table_data = get_table_data(table_name)
        for key, value in request.POST.items():
            if key.startswith('desc_'):

                row_id = key[5:]
                obj = table_data.get(id=row_id)
                obj.description = value
                obj.save()
        return redirect(reverse('table_view', args=[table_name]))


def description(request, table_name):
    table_data = get_table_data(table_name)
    terms = sorted([[row.value, row.description, row.id] for row in table_data if row.value is not None])
    return render(request, 'description.html', {'table_name': table_name, 'table_data': table_data, 'terms': terms})


def entity_view(request, table_name, entity_id):
    relations_dict = {
        'Причина для': 'Причина для',
        'Следствие для': 'Следствие для'
    }

    type_translation = {
        'process': 'Процесс',
        'external_entity': 'Внешняя сущность',
        'data_store': 'Хранилище данных',
        'index_data_store': 'Индекс хранилища данных',
        'data_flow': 'Поток данных'
    }

    table_data = get_table_data(table_name)
    all_entity = []
    terms = []

    for row in table_data:
        one_entity = []
        if entity_id == row.source:
            first = row.source
            second = relations_dict.get(row.type, 'Следствие для')
            value = row.value
            third = row.target
            for item in table_data:
                if item.id == first:
                    one_entity.append(item.value)
            one_entity.append(second)
            one_entity.append(value)
            for item in table_data:
                if item.id == third:
                    one_entity.append(item.value)
                    one_entity.append(item.id)
            all_entity.append(one_entity)
        elif entity_id == row.target:
            first = row.target
            second = relations_dict.get(row.type, 'Причина для')
            value = row.value
            third = row.source
            for item in table_data:
                if item.id == first:
                    one_entity.append(item.value)
            one_entity.append(second)
            one_entity.append(value)
            for item in table_data:
                if item.id == third:
                    one_entity.append(item.value)
                    one_entity.append(item.id)
            all_entity.append(one_entity)

    child_data_store = []
    for row in table_data:
        if entity_id == row.id:
            terms.append([row.value, row.description, type_translation.get(row.data_type, row.data_type)])
            if row.data_type == 'index_data_store':
                parent_id = row.parent  # предполагается, что у row есть поле parent
                for item in table_data:
                    if item.data_type == 'data_store' and item.parent == parent_id:
                        child_data_store.append([item.value, item.description])
    return render(request, 'entity_view.html', {'all_entity': all_entity, 'terms': terms,
                                                'table_name': table_name, 'child_store': child_data_store})
