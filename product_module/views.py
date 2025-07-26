from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, View
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView
from rest_framework import generics, mixins
from rest_framework import viewsets, filters

from .models import Product, ProductCategory, ProductComment
from account_module.models import User
from .serializers import ProductSerializer, ProductCategorySerializer


class ProductView(ListView):
    template_name = "products.html"
    model = Product
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        query = super(ProductView, self).get_queryset()
        category_name = self.kwargs.get('category')
        if category_name is not None:
            query = query.filter(category__url_title__iexact=category_name)
        return query


def product_categories_component(request):
    product_categories: ProductCategory = ProductCategory.objects.filter(is_active=True)

    return render(request, 'component/product_categories_component.html', context={
        'categories': product_categories
    })


class ProductDetailView(View):
    def get(self, request, product_id):
        product = Product.objects.filter(is_active=True, id=product_id).first()
        new_product: Product = Product.objects.filter(is_active=True).order_by('price')[0:4]
        comments = product.comments.all().order_by('-create_date')

        comment_message = request.GET.get('message')

        if request.GET:
            new_comment = ProductComment()
            new_comment.message = comment_message
            new_comment.user = request.user
            new_comment.product = product
            if comment_message:
                new_comment.save()

            return render(request, 'comment_product.html', context={
                'product': product,
                'comments': comments,
                'product_new': new_product
            })

        return render(request, 'product_detail.html', context={
            'product': product,
            'comments': comments,
            'product_new': new_product
        })


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'slug']

    def get_product_by_slug(self, request, slug=None):
        product = get_object_or_404(Product, slug=slug)
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_id = request.query_params.get('category_id', None)
        if category_id:
            products = Product.objects.filter(category_id=category_id)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        return Response({"error": "Please provide a category_id parameter"}, status=400)

    @action(detail=False, methods=['get'])
    def by_category_slug(self, request):
        category_slug = request.query_params.get('category_slug', None)
        if category_slug:
            products = Product.objects.filter(category__url_title=category_slug)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        return Response({"error": "Please provide a category_slug parameter"}, status=400)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'url_title']