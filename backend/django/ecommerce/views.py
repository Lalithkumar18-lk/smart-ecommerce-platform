
from decimal import Decimal

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Product, CartItem, Order, OrderItem
from .serializers import ProductSerializer, CartItemSerializer, OrderSerializer

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    email = request.data.get("email", "")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"detail": "Username already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )
    return Response(
        {"message": "Registration successful.", "username": user.username},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    user = authenticate(
        username=request.data.get("username"),
        password=request.data.get("password"),
    )

    if user is None:
        return Response(
            {"detail": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "username": user.username,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def products(request):
    queryset = Product.objects.filter(is_active=True)
    category = request.GET.get("category")

    if category:
        queryset = queryset.filter(category__iexact=category)

    return Response(ProductSerializer(queryset, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cart(request):
    items = CartItem.objects.filter(
        user=request.user
    ).select_related("product")
    return Response(CartItemSerializer(items, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    try:
        product_id = int(request.data.get("product_id"))
        quantity = int(request.data.get("quantity", 1))
    except (TypeError, ValueError):
        return Response(
            {"detail": "Invalid product ID or quantity."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if quantity < 1:
        return Response(
            {"detail": "Quantity must be at least 1."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response(
            {"detail": "Product not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": quantity},
    )

    if not created:
        item.quantity += quantity

    if item.quantity > product.stock:
        if not created:
            item.refresh_from_db()
        return Response(
            {"detail": "Not enough stock."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not created:
        item.save(update_fields=["quantity"])

    return Response(
        CartItemSerializer(item).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    deleted, _ = CartItem.objects.filter(
        id=item_id,
        user=request.user,
    ).delete()

    if not deleted:
        return Response(
            {"detail": "Cart item not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response({"message": "Removed from cart."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkout(request):
    with transaction.atomic():
        items = list(
            CartItem.objects.filter(user=request.user).select_related("product")
        )

        if not items:
            return Response(
                {"detail": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total = Decimal("0.00")

        for item in items:
            product = Product.objects.select_for_update().get(
                pk=item.product_id
            )

            if not product.is_active or product.stock < item.quantity:
                return Response(
                    {"detail": f"Insufficient stock for {product.name}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            total += product.price * item.quantity

        order = Order.objects.create(
            user=request.user,
            status="pending",
            total_amount=total,
        )

        for item in items:
            product = Product.objects.select_for_update().get(
                pk=item.product_id
            )

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                unit_price=product.price,
                quantity=item.quantity,
            )

            product.stock -= item.quantity
            product.save(update_fields=["stock"])

        CartItem.objects.filter(user=request.user).delete()

    return Response(
        {
            "message": "Order placed successfully. Payment is not processed.",
            "order": OrderSerializer(order).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def orders(request):
    queryset = Order.objects.filter(
        user=request.user
    ).prefetch_related("items")

    return Response(OrderSerializer(queryset, many=True).data)