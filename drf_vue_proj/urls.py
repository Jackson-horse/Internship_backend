from student_predict.views import(
    TokenObtainPairView,
    TokenRefreshView
)
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/',include('account.urls')),
    path('api/token/',TokenObtainPairView.as_view()),
    path('api/token/refresh',TokenRefreshView.as_view())
]
