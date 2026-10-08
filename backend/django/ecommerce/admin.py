from django.contrib import admin

from .models import (
    ActivityLog,
    CartItem,
    Notification,
    Order,
    OrderHistory,
    OrderItem,
    Payment,
    Product,
    UserProfile,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "phone")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "popularity",
        "is_active",
    )
    list_filter = ("category", "is_active")
    search_fields = ("name", "description")
    list_editable = ("price", "stock", "is_active")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "quantity",
        "added_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "product__name",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_amount",
        "payment_status",
        "order_status",
        "tracking_number",
        "created_at",
    )
    list_filter = (
        "payment_status",
        "order_status",
    )
    search_fields = (
        "user__username",
        "user__email",
        "tracking_number",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product_name",
        "unit_price",
        "quantity",
    )
    search_fields = ("product_name",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "amount",
        "payment_method",
        "transaction_id",
        "status",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_method",
    )
    search_fields = (
        "transaction_id",
        "stripe_payment_intent",
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "notification_type",
        "message",
        "is_read",
        "created_at",
    )
    list_filter = (
        "notification_type",
        "is_read",
    )
    search_fields = (
        "user__username",
        "message",
    )


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "previous_status",
        "new_status",
        "message",
        "changed_by",
        "created_at",
    )
    list_filter = ("new_status",)
    search_fields = (
        "message",
        "order__id",
        "changed_by__username",
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action",
        "description",
        "ip_address",
        "created_at",
    )
    list_filter = ("action",)
    search_fields = (
        "user__username",
        "description",
        "ip_address",
    )