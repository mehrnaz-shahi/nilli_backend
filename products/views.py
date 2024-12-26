from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Product, Favorite, Category
from .serializers import FavoriteSerializer, ProductSerializer


class ToggleFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        # Get the product by ID
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the product is already in the user's favorites
        favorite = Favorite.objects.filter(user=request.user, product=product).first()

        if favorite:
            # If exists, remove it
            favorite.delete()
            return Response({"detail": "Product removed from favorites."}, status=status.HTTP_200_OK)
        else:
            # Otherwise, add it
            favorite = Favorite.objects.create(user=request.user, product=product)
            return Response({"detail": "Product added to favorites."}, status=status.HTTP_201_CREATED)


class ProductListAPIView(ListAPIView):
    """
    API to return a list of all products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductFilteredByCategoryAPIView(APIView):
    """
    API to return a list of products filtered by category ID provided as a query parameter.
    """

    def get(self, request, *args, **kwargs):
        category_name = request.query_params.get('category')
        if not category_name:
            return Response({"error": "Category name is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductDetailAPIView(RetrieveAPIView):
    """
    API to retrieve a product by its ID.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
