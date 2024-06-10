from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('data_base/', views.data_base_view, name='data_base_view'),
    path('delete_file/<str:uploaded_file>/', views.delete_file, name='delete_file'),
    path('table_view/<str:table_name>/', views.table_view, name='table_view'),
    path('termins/<str:table_name>/', views.termins_view, name='termins_view'),
    path('edit_values/<str:table_name>/', views.edit_values, name='edit_values'),
    path('update_values/<str:table_name>/', views.update_values, name='update_values'),
    path('edit_desc/<str:table_name>/', views.edit_desc, name='edit_desc'),
    path('update_description/<str:table_name>/', views.update_description, name='update_description'),
    path('description/<str:table_name>/', views.description, name='description'),
    path('entity_view/<str:table_name>/<str:entity_id>/', views.entity_view, name='entity_view'),
]