from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("home_module.urls", namespace="home")),
    path("products/", include("product_module.urls", namespace="products")),
    path("account/", include("account_module.urls", namespace="account")),
    path("contact-us/", include("contactus_module.urls", namespace="contact-us")),
    path("blog/", include("blog_module.urls", namespace="blog")),
    path("user/", include("profile_module.urls", namespace="user")),
    path('order/', include("order_module.urls", namespace="order")),
    path('panel/', include("admin_panel.urls", namespace="panel")),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
