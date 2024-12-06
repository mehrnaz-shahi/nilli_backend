from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Product, Favorite
from .serializers import FavoriteSerializer


class AddFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        # Get the product by ID
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the product is already favorited
        if Favorite.objects.filter(user=request.user, product=product).exists():
            return Response({"detail": "Product is already in your favorites."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new favorite entry
        favorite = Favorite(user=request.user, product=product)
        favorite.save()

        # Serialize and return the response
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
