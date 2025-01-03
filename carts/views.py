from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from products.models import Product
from .models import Cart, CartItem
from .serializers import CartSerializer


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "محصول یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "محصول یافت نشد"}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"detail": "سبد خریدی یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({"detail": "محصول در سبد خرید نیست."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class UpdateCartItemQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, product_id):
        quantity = request.data.get('quantity')

        if quantity is None or quantity <= 0:
            return Response({"detail": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity = quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            return Response({"detail": "Product not in cart."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateCartStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, cart_id):
        # Find cart
        try:
            cart = Cart.objects.get(id=cart_id, user=request.user)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')

        if new_status not in dict(Cart.STATUS_CHOICES):
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        cart.status = new_status
        cart.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ViewCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
