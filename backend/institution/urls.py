from django.urls import path
from institution import views, paymentViews, plansViews

urlpatterns = [
    path('register/', views.InstitutionRegisterView.as_view(),
         name="institution_register"),

    path('users/register/csv/', views.BulkUserImportView.as_view(),
         name="institution_register_csv"),
    path('users/', views.InstitutionUserView.as_view(),
         name="institution_register_user"),

    # Payment
    path('webhook/', paymentViews.InstitutionPaymentWebhookView.as_view(),
         name="institution_webhook"),
    path('payment/', paymentViews.InstitutionGeneratePaymentIntentView.as_view(),
         name="institution_payment"),
    path('payment/verify/', paymentViews.InstitutionVerifyPaymentView.as_view(),
         name="institution_payment_verify"),
    path('buy-credits/', paymentViews.InstitutionBuyCreditsView.as_view(),
         name="institution_buy_credits"),

    # Plans
    path('plans/', plansViews.PlanListView.as_view(),
         name="institution_plans"),
    path('plans/<uuid:id>/', plansViews.PlanDetailView.as_view(),
         name="institution_plan_detail"),
    path('current-plan/', plansViews.InstitutionCurrentPlanView.as_view(),
         name="institution_current_plan"),
]
