from account.views import(
    TokenObtainPairView,
    TokenRefreshView
)
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/',include('account.urls')),
    path('student/',include('student.urls')),
    path('admin_page/', include('admin_page.urls')),
    path('api/token/',TokenObtainPairView.as_view()),
    path('api/token/refresh',TokenRefreshView.as_view())
]
