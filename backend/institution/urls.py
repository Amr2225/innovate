from django.urls import path
from institution import views

urlpatterns = [
    path('register/', views.InstitutionRegisterView.as_view(),
         name="institution_register"),

    path('users/register/csv/', views.BulkUserImportView.as_view(),
         name="institution_register_csv"),
    path('users/', views.InstitutionUserView.as_view(),
         name="institution_register_user"),
    path('webhook/', views.WebhookView.as_view(),
         name="institution_webhook"),

    path('payment/', views.TestRequestView.as_view(),
         name="institution_payment"),
]
